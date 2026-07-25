 # import libraries ->
import csv
import json
import os
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse, urldefrag

import requests
import typer
from bs4 import BeautifulSoup
from rich import print


 # main function ->
def __main():
  print('[bold blue]⁕ function loading...[/bold blue]')
  __inputData()


 # secondary functions ->
def __inputData():
  print('[bold yellow]⁕ starting technical seo audit...[/bold yellow]')
  
  targetUrl = input(' > Introduce la Url principal a auditar: ').strip()
  projectName = input(' > Introduce el nombre del proyecto: ').strip()
  
  try:
    maxPages = int(input(' > Maximo de paginas a rastrear [20]: ').strip() or '20')
  except ValueError:
    maxPages = 20
  
  try:
    maxDepth = int(input(' > Profundidad maxima [2]: ').strip() or '2')
  except ValueError:
    maxDepth = 2
  
  if not targetUrl.startswith(('http://', 'https://')):
    targetUrl = 'https://' + targetUrl
  
  print('[bold yellow]  - Nota: este audit analiza html estatico. schema markup inyectado por javascript no sera detectado.[/bold yellow]')
  
  __runAudit(targetUrl, projectName, maxPages, maxDepth)

def __runAudit(baseUrl, projectName, maxPages, maxDepth):
  domain = urlparse(baseUrl).netloc
  reportFolder = os.path.join('seo-audit-reports', projectName)
  
  if not os.path.exists(reportFolder):
    os.makedirs(reportFolder)
  
  auditData = {
    'baseUrl': baseUrl,
    'domain': domain,
    'date': datetime.now().isoformat(),
    'maxPages': maxPages,
    'maxDepth': maxDepth,
    'robotsTxt': __checkRobotsTxt(baseUrl),
    'sitemap': __checkSitemap(baseUrl),
    'pages': [],
    'issues': [],
    'summary': {}
  }
  
  crawled = set()
  toCrawl = [(baseUrl, 0)]
  headers = {'User-Agent': 'Mozilla/5.0 (compatible; seo-tech-audit/1.0)'}
  session = requests.Session()
  session.headers.update(headers)
  
  print(f'[bold cyan]  - Dominio: {domain}[/bold cyan]')
  print(f'[bold cyan]  - Limite: {maxPages} paginas | Profundidad: {maxDepth}[/bold cyan]')
  
  while toCrawl and len(crawled) < maxPages:
    url, depth = toCrawl.pop(0)
    
    if url in crawled or depth > maxDepth:
      continue
    
    crawled.add(url)
    print(f'[bold blue]  ⁕ crawling {url}[/bold blue]')
    
    try:
      pageData = __analyzePage(session, url, baseUrl, domain)
      auditData['pages'].append(pageData)
      
      for issue in pageData['issues']:
        auditData['issues'].append(issue)
      
      if pageData['status'] == 200:
        for link in pageData['internalLinks']:
          fullUrl = urldefrag(link)[0]
          if fullUrl not in crawled and len(crawled) + len(toCrawl) < maxPages:
            toCrawl.append((fullUrl, depth + 1))
      
      time.sleep(0.5)
    
    except Exception as error:
      print(f'[bold red]  - Error crawling {url}: {error}[/bold red]')
      auditData['issues'].append({
        'url': url,
        'type': 'crawl_error',
        'severity': 'high',
        'message': str(error)
      })
  
  auditData['summary'] = __buildSummary(auditData)
  __saveReport(reportFolder, auditData)
  __printSummary(auditData['summary'])

def __checkRobotsTxt(baseUrl):
  result = {'exists': False, 'url': None, 'sitemaps': [], 'blocksAll': False, 'error': None}
  parsed = urlparse(baseUrl)
  robotsUrl = f'{parsed.scheme}://{parsed.netloc}/robots.txt'
  result['url'] = robotsUrl
  
  try:
    response = requests.get(robotsUrl, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
      result['exists'] = True
      for line in response.text.splitlines():
        lineLower = line.strip().lower()
        if lineLower.startswith('sitemap:'):
          result['sitemaps'].append(line.split(':', 1)[1].strip())
        if 'disallow:' in lineLower and lineLower.split('disallow:')[1].strip() == '/':
          result['blocksAll'] = True
  except Exception as error:
    result['error'] = str(error)
  
  return result

def __checkSitemap(baseUrl):
  result = {'exists': False, 'url': None, 'urls': 0, 'error': None}
  parsed = urlparse(baseUrl)
  sitemapUrl = f'{parsed.scheme}://{parsed.netloc}/sitemap.xml'
  result['url'] = sitemapUrl
  
  try:
    response = requests.get(sitemapUrl, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
      result['exists'] = True
      result['urls'] = response.text.count('<loc>')
  except Exception as error:
    result['error'] = str(error)
  
  return result

def __analyzePage(session, url, baseUrl, domain):
  issues = []
  startTime = time.time()
  response = session.get(url, timeout=15, allow_redirects=True)
  loadTime = round(time.time() - startTime, 3)
  
  status = response.status_code
  finalUrl = response.url
  isRedirect = status in (301, 302, 307, 308) or finalUrl != url
  
  if isRedirect:
    issues.append({
      'url': url,
      'type': 'redirect',
      'severity': 'medium',
      'message': f'redirige a {finalUrl}'
    })
  
  if not response.url.startswith('https://'):
    issues.append({
      'url': url,
      'type': 'no_https',
      'severity': 'high',
      'message': 'la pagina no usa https'
    })
  
  soup = BeautifulSoup(response.text, 'html.parser')
  
  titleTag = soup.title
  title = titleTag.string.strip() if titleTag and titleTag.string else ''
  titleLength = len(title)
  
  if not title:
    issues.append({'url': url, 'type': 'missing_title', 'severity': 'high', 'message': 'falta el titulo'})
  elif titleLength > 60:
    issues.append({'url': url, 'type': 'title_too_long', 'severity': 'medium', 'message': f'titulo demasiado largo ({titleLength} caracteres)'})
  elif titleLength < 30:
    issues.append({'url': url, 'type': 'title_too_short', 'severity': 'low', 'message': f'titulo demasiado corto ({titleLength} caracteres)'})
  
  metaDesc = soup.find('meta', attrs={'name': 'description'})
  description = metaDesc.get('content', '').strip() if metaDesc else ''
  descLength = len(description)
  
  if not description:
    issues.append({'url': url, 'type': 'missing_meta_description', 'severity': 'medium', 'message': 'falta la meta description'})
  elif descLength > 160:
    issues.append({'url': url, 'type': 'meta_description_too_long', 'severity': 'medium', 'message': f'meta description demasiado larga ({descLength} caracteres)'})
  elif descLength < 120:
    issues.append({'url': url, 'type': 'meta_description_too_short', 'severity': 'low', 'message': f'meta description demasiado corta ({descLength} caracteres)'})
  
  canonical = ''
  canonicalTag = soup.find('link', attrs={'rel': 'canonical'})
  if canonicalTag:
    canonical = canonicalTag.get('href', '').strip()
  if not canonical:
    issues.append({'url': url, 'type': 'missing_canonical', 'severity': 'medium', 'message': 'falta etiqueta canonical'})
  
  metaRobots = soup.find('meta', attrs={'name': 'robots'})
  robotsContent = metaRobots.get('content', '').lower() if metaRobots else ''
  if 'noindex' in robotsContent:
    issues.append({'url': url, 'type': 'noindex', 'severity': 'high', 'message': 'la pagina tiene noindex'})
  
  viewport = soup.find('meta', attrs={'name': 'viewport'})
  if not viewport:
    issues.append({'url': url, 'type': 'missing_viewport', 'severity': 'medium', 'message': 'falta viewport, posiblemente no es responsive'})
  
  h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
  if len(h1s) == 0:
    issues.append({'url': url, 'type': 'missing_h1', 'severity': 'high', 'message': 'falta etiqueta h1'})
  elif len(h1s) > 1:
    issues.append({'url': url, 'type': 'multiple_h1', 'severity': 'medium', 'message': f'hay {len(h1s)} etiquetas h1'})
  
  headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(2, 7)}
  
  images = soup.find_all('img')
  imagesWithoutAlt = sum(1 for img in images if not img.get('alt', '').strip())
  if imagesWithoutAlt > 0:
    issues.append({
      'url': url,
      'type': 'images_without_alt',
      'severity': 'low',
      'message': f'{imagesWithoutAlt} imagenes sin alt de {len(images)}'
    })
  
  internalLinks = set()
  externalLinks = set()
  
  for link in soup.find_all('a', href=True):
    href = link['href'].strip()
    if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
      continue
    fullUrl = urldefrag(urljoin(url, href))[0]
    if urlparse(fullUrl).netloc == domain:
      internalLinks.add(fullUrl)
    elif fullUrl.startswith('http'):
      externalLinks.add(fullUrl)
  
  pageSize = len(response.content)
  
  return {
    'url': url,
    'finalUrl': finalUrl,
    'status': status,
    'loadTime': loadTime,
    'pageSize': pageSize,
    'title': title,
    'titleLength': titleLength,
    'description': description,
    'descriptionLength': descLength,
    'canonical': canonical,
    'robots': robotsContent,
    'h1s': h1s,
    'headings': headings,
    'images': len(images),
    'imagesWithoutAlt': imagesWithoutAlt,
    'internalLinks': sorted(internalLinks),
    'externalLinksCount': len(externalLinks),
    'issues': issues
  }

def __buildSummary(auditData):
  pages = auditData['pages']
  issues = auditData['issues']
  
  summary = {
    'pagesCrawled': len(pages),
    'totalIssues': len(issues),
    'highIssues': sum(1 for i in issues if i['severity'] == 'high'),
    'mediumIssues': sum(1 for i in issues if i['severity'] == 'medium'),
    'lowIssues': sum(1 for i in issues if i['severity'] == 'low'),
    'avgLoadTime': round(sum(p['loadTime'] for p in pages) / len(pages), 3) if pages else 0,
    'robotsTxtExists': auditData['robotsTxt']['exists'],
    'robotsBlocksAll': auditData['robotsTxt']['blocksAll'],
    'sitemapExists': auditData['sitemap']['exists'],
    'sitemapUrls': auditData['sitemap']['urls']
  }
  
  return summary

def __saveReport(folder, auditData):
  timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
  
  jsonPath = os.path.join(folder, f'report_{timestamp}.json')
  with open(jsonPath, 'w', encoding='utf-8') as file:
    json.dump(auditData, file, indent=2, ensure_ascii=False)
  
  csvPath = os.path.join(folder, f'report_{timestamp}.csv')
  with open(csvPath, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['url', 'status', 'load_time', 'title_length', 'description_length', 'h1_count', 'images_without_alt', 'internal_links', 'external_links', 'issues_count'])
    for page in auditData['pages']:
      writer.writerow([
        page['url'],
        page['status'],
        page['loadTime'],
        page['titleLength'],
        page['descriptionLength'],
        len(page['h1s']),
        page['imagesWithoutAlt'],
        len(page['internalLinks']),
        page['externalLinksCount'],
        len(page['issues'])
      ])
  
  print(f'[bold cyan]  - Json report: {jsonPath}[/bold cyan]')
  print(f'[bold cyan]  - Csv report: {csvPath}[/bold cyan]')

def __printSummary(summary):
  print('\n[bold yellow]⁕ audit summary[/bold yellow]')
  print(f'[bold cyan]  - Pages crawled: {summary["pagesCrawled"]}[/bold cyan]')
  print(f'[bold cyan]  - Total issues: {summary["totalIssues"]}[/bold cyan]')
  print(f'[bold red]  - High severity: {summary["highIssues"]}[/bold red]')
  print(f'[bold yellow]  - Medium severity: {summary["mediumIssues"]}[/bold yellow]')
  print(f'[bold white]  - Low severity: {summary["lowIssues"]}[/bold white]')
  print(f'[bold cyan]  - Avg load time: {summary["avgLoadTime"]}s[/bold cyan]')
  print(f'[bold cyan]  - Robots.txt: {"found" if summary["robotsTxtExists"] else "not found"}[/bold cyan]')
  if summary['robotsBlocksAll']:
    print('[bold red]  - Warning: robots.txt bloquea todo el sitio[/bold red]')
  print(f'[bold cyan]  - Sitemap.xml: {"found" if summary["sitemapExists"] else "not found"} ({summary["sitemapUrls"]} urls)[/bold cyan]')
  print('[bold white]// operation finish[/bold white]')


 # secure function boot ->
if __name__ == '__main__':
  typer.run(__main)
