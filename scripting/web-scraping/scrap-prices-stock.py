 # import libraries ->
import csv
import json
import os
import random
import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

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
  print('[bold yellow]⁕ price intelligence module...[/bold yellow]')
  
  projectName = input(' > Nombre del proyecto: ').strip()
  targetUrl = input(' > Url de la categoria o pagina a monitorear: ').strip()
  
  if not targetUrl.startswith(('http://', 'https://')):
    targetUrl = 'https://' + targetUrl
  
  baseFolder = os.path.join('price-intelligence', projectName)
  configPath = os.path.join(baseFolder, 'config.json')
  config = None
  
  if os.path.exists(configPath):
    useExisting = input(' > Configuracion existente encontrada. Usarla? [s/N]: ').strip().lower()
    if useExisting in ('s', 'si', 'yes', 'y'):
      with open(configPath, 'r', encoding='utf-8') as file:
        config = json.load(file)
      print('[bold cyan]  - Configuracion cargada[/bold cyan]')
  
  if config is None:
    config = __buildConfig(projectName, targetUrl, baseFolder)
    __saveJson(configPath, config)
    print('[bold cyan]  - Configuracion guardada[/bold cyan]')
  
  __runIntelligence(config)


def __buildConfig(projectName, targetUrl, baseFolder):
  print('[bold yellow]⁕ configure selectors[/bold yellow]')
  print('[bold white]  - Deja en blanco para deteccion automatica (experimental)[/bold white]')
  
  config = {
    'projectName': projectName,
    'targetUrl': targetUrl,
    'baseFolder': baseFolder,
    'productSelector': input(' > Selector css del contenedor de producto: ').strip(),
    'nameSelector': input(' > Selector css del nombre: ').strip(),
    'priceSelector': input(' > Selector css del precio: ').strip(),
    'oldPriceSelector': input(' > Selector css del precio anterior (opcional): ').strip(),
    'stockSelector': input(' > Selector css del stock/disponibilidad (opcional): ').strip(),
    'skuSelector': input(' > Selector css del sku/referencia (opcional): ').strip(),
    'stockKeywords': {
      'inStock': ['in stock', 'disponible', 'available', 'en stock', 'add to cart', 'anadir al carrito', 'comprar'],
      'outOfStock': ['out of stock', 'agotado', 'no disponible', 'unavailable', 'sin stock', 'sold out']
    },
    'proxy': input(' > Proxy (url completa) o deja en blanco: ').strip(),
    'maxProducts': 50,
    'delay': 1.0,
    'retries': 3
  }
  
  try:
    config['maxProducts'] = int(input(' > Maximo de productos a extraer [50]: ').strip() or '50')
  except ValueError:
    config['maxProducts'] = 50
  
  try:
    config['delay'] = float(input(' > Delay entre peticiones en segundos [1.0]: ').strip() or '1.0')
  except ValueError:
    config['delay'] = 1.0
  
  try:
    config['retries'] = int(input(' > Reintentos por peticion [3]: ').strip() or '3')
  except ValueError:
    config['retries'] = 3
  
  return config


def __runIntelligence(config):
  baseFolder = config['baseFolder']
  if not os.path.exists(baseFolder):
    os.makedirs(baseFolder)
  
  targetUrl = config['targetUrl']
  domain = urlparse(targetUrl).netloc
  
  print(f'[bold cyan]  - Proyecto: {config["projectName"]}[/bold cyan]')
  print(f'[bold cyan]  - Dominio: {domain}[/bold cyan]')
  print(f'[bold cyan]  - Url objetivo: {targetUrl}[/bold cyan]')
  
  if not __checkRobotsTxt(targetUrl):
    proceed = input(' > robots.txt restringe el rastreo. Continuar de todos modos? [s/N]: ').strip().lower()
    if proceed not in ('s', 'si', 'yes', 'y'):
      print('[bold red]  - Operacion cancelada por el usuario[/bold red]')
      return
  
  session = __createSession(config)
  
  print('[bold blue]  ⁕ fetching target page...[/bold blue]')
  response = __fetchPage(session, targetUrl, config)
  if response is None:
    print('[bold red]  - No se pudo obtener la pagina objetivo[/bold red]')
    return
  
  soup = BeautifulSoup(response.text, 'html.parser')
  productElements = __detectProducts(soup, config)
  
  if not productElements:
    print('[bold yellow]  - No se detectaron productos. Revisa los selectores css.[/bold yellow]')
    return
  
  print(f'[bold cyan]  - Productos detectados: {len(productElements)}[/bold cyan]')
  
  products = []
  for index, element in enumerate(productElements):
    if len(products) >= config['maxProducts']:
      break
    
    product = __extractProductData(element, targetUrl, domain, config)
    if product:
      products.append(product)
      print(f'[bold green]  - [{index + 1}] {product["name"]} | {product["price"]} | {product["availability"]}[/bold green]')
    else:
      print(f'[bold yellow]  - [{index + 1}] Producto omitido por datos incompletos[/bold yellow]')
    
    if index < len(productElements) - 1:
      time.sleep(config['delay'])
  
  timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
  runData = {
    'projectName': config['projectName'],
    'domain': domain,
    'targetUrl': targetUrl,
    'timestamp': datetime.now().isoformat(),
    'totalProducts': len(products),
    'products': products
  }
  
  __saveRunData(baseFolder, timestamp, runData)
  
  historicalData = __loadLatestRun(baseFolder)
  changesReport = __analyzeChanges(runData, historicalData)
  __saveChangesReport(baseFolder, timestamp, changesReport)
  
  __printReport(runData, changesReport)


def __createSession(config):
  userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  ]
  
  session = requests.Session()
  session.headers.update({
    'User-Agent': random.choice(userAgents),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
  })
  
  if config.get('proxy'):
    session.proxies = {
      'http': config['proxy'],
      'https': config['proxy']
    }
  
  return session


def __checkRobotsTxt(targetUrl):
  parsed = urlparse(targetUrl)
  robotsUrl = f'{parsed.scheme}://{parsed.netloc}/robots.txt'
  parser = RobotFileParser()
  parser.set_url(robotsUrl)
  
  try:
    parser.read()
    return parser.can_fetch('*', targetUrl)
  except Exception:
    return True


def __fetchPage(session, url, config, attempt=1):
  try:
    response = session.get(url, timeout=15, allow_redirects=True)
    response.raise_for_status()
    return response
  except requests.exceptions.RequestException as error:
    print(f'[bold yellow]  - Intento {attempt} fallido para {url}: {error}[/bold yellow]')
    if attempt < config['retries']:
      waitTime = 2 ** attempt
      print(f'[bold yellow]  - Reintentando en {waitTime}s...[/bold yellow]')
      time.sleep(waitTime)
      return __fetchPage(session, url, config, attempt + 1)
    return None


def __detectProducts(soup, config):
  selector = config.get('productSelector', '')
  
  if selector:
    return soup.select(selector)
  
  candidates = []
  seenContainers = set()
  
  pricePattern = re.compile(r'([€$£]\s*\d+[\d.,]*|\d+[\d.,]*\s*[€$£])')
  priceTexts = soup.find_all(text=pricePattern)
  
  for text in priceTexts:
    element = text.parent
    for _ in range(5):
      if element is None or element.name == 'body':
        break
      
      containerId = id(element)
      if containerId in seenContainers:
        element = element.parent
        continue
      
      link = element.find('a', href=True)
      if link and len(element.get_text(strip=True)) > 20:
        seenContainers.add(containerId)
        candidates.append(element)
        break
      
      element = element.parent
  
  return candidates[:config['maxProducts']]


def __extractProductData(element, baseUrl, domain, config):
  product = {
    'url': '',
    'name': '',
    'price': None,
    'oldPrice': None,
    'currency': '',
    'availability': 'unknown',
    'sku': '',
    'timestamp': datetime.now().isoformat()
  }
  
  link = element.find('a', href=True)
  if link:
    product['url'] = urljoin(baseUrl, link['href'].strip())
  else:
    product['url'] = baseUrl
  
  nameSelector = config.get('nameSelector', '')
  if nameSelector:
    nameNode = element.select_one(nameSelector)
  else:
    nameNode = link
  
  if nameNode:
    product['name'] = nameNode.get_text(strip=True)
  else:
    product['name'] = element.get_text(strip=True)[:100]
  
  priceSelector = config.get('priceSelector', '')
  if priceSelector:
    priceNode = element.select_one(priceSelector)
  else:
    priceNode = __findPriceNode(element)
  
  if priceNode:
    priceText = priceNode.get_text(strip=True)
    product['price'], product['currency'] = __parsePrice(priceText)
  
  oldPriceSelector = config.get('oldPriceSelector', '')
  if oldPriceSelector:
    oldPriceNode = element.select_one(oldPriceSelector)
    if oldPriceNode:
      oldPriceText = oldPriceNode.get_text(strip=True)
      product['oldPrice'], _ = __parsePrice(oldPriceText)
  
  stockSelector = config.get('stockSelector', '')
  if stockSelector:
    stockNode = element.select_one(stockSelector)
    if stockNode:
      product['availability'] = __inferAvailability(stockNode.get_text(strip=True), config)
  else:
    product['availability'] = __inferAvailability(element.get_text(strip=True), config)
  
  skuSelector = config.get('skuSelector', '')
  if skuSelector:
    skuNode = element.select_one(skuSelector)
    if skuNode:
      product['sku'] = skuNode.get_text(strip=True)
  
  if not product['sku']:
    product['sku'] = __extractSkuFromUrl(product['url']) or __generateSku(product['name'])
  
  if product['name'] and product['price'] is not None:
    return product
  
  return None


def __findPriceNode(element):
  pricePattern = re.compile(r'([€$£]\s*\d+[\d.,]*|\d+[\d.,]*\s*[€$£]|\d+[\d.,]*\s*EUR|\d+[\d.,]*\s*USD)')
  
  for node in element.find_all(text=pricePattern):
    if node.parent.name not in ('script', 'style'):
      return node.parent
  
  return None


def __parsePrice(priceText):
  if not priceText:
    return None, ''
  
  priceText = priceText.replace('\xa0', ' ').replace(',', '.')
  
  currencyMap = {'€': 'EUR', '$': 'USD', '£': 'GBP', 'eur': 'EUR', 'usd': 'USD', 'gbp': 'GBP'}
  currency = ''
  
  for symbol, code in currencyMap.items():
    if symbol in priceText.lower():
      currency = code
      break
  
  numbers = re.findall(r'\d[\d.]*', priceText)
  if not numbers:
    return None, currency
  
  candidates = []
  for number in numbers:
    try:
      candidates.append(float(number))
    except ValueError:
      continue
  
  if not candidates:
    return None, currency
  
  price = max(candidates)
  return price, currency


def __inferAvailability(text, config):
  textLower = text.lower()
  
  for keyword in config['stockKeywords']['outOfStock']:
    if keyword in textLower:
      return 'out_of_stock'
  
  for keyword in config['stockKeywords']['inStock']:
    if keyword in textLower:
      return 'in_stock'
  
  return 'unknown'


def __extractSkuFromUrl(url):
  patterns = [
    r'[?&]sku=([^&]+)',
    r'[?&]pid=([^&]+)',
    r'[?&]id=([^&]+)',
    r'/p/([^/?]+)',
    r'/product/([^/?]+)'
  ]
  
  for pattern in patterns:
    match = re.search(pattern, url)
    if match:
      return match.group(1)
  
  return None


def __generateSku(name):
  clean = re.sub(r'[^a-zA-Z0-9]', '-', name.lower())[:30].strip('-')
  return clean or 'sku-unknown'


def __saveRunData(baseFolder, timestamp, runData):
  jsonPath = os.path.join(baseFolder, f'products_{timestamp}.json')
  __saveJson(jsonPath, runData)
  
  csvPath = os.path.join(baseFolder, f'products_{timestamp}.csv')
  with open(csvPath, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['sku', 'name', 'price', 'old_price', 'currency', 'availability', 'url', 'timestamp'])
    for product in runData['products']:
      writer.writerow([
        product['sku'],
        product['name'],
        product['price'],
        product['oldPrice'],
        product['currency'],
        product['availability'],
        product['url'],
        product['timestamp']
      ])
  
  latestPath = os.path.join(baseFolder, 'latest.json')
  __saveJson(latestPath, runData)
  
  print(f'[bold cyan]  - Json guardado: {jsonPath}[/bold cyan]')
  print(f'[bold cyan]  - Csv guardado: {csvPath}[/bold cyan]')


def __loadLatestRun(baseFolder):
  latestPath = os.path.join(baseFolder, 'latest.json')
  if not os.path.exists(latestPath):
    return None
  
  try:
    with open(latestPath, 'r', encoding='utf-8') as file:
      return json.load(file)
  except Exception:
    return None


def __analyzeChanges(currentData, previousData):
  report = {
    'timestamp': datetime.now().isoformat(),
    'previousTimestamp': previousData.get('timestamp') if previousData else None,
    'totalCurrent': len(currentData['products']),
    'totalPrevious': len(previousData['products']) if previousData else 0,
    'newProducts': [],
    'removedProducts': [],
    'priceDrops': [],
    'priceIncreases': [],
    'stockChanges': [],
    'unchanged': 0
  }
  
  if not previousData:
    return report
  
  currentMap = {p['sku']: p for p in currentData['products']}
  previousMap = {p['sku']: p for p in previousData['products']}
  
  for sku, product in currentMap.items():
    if sku not in previousMap:
      report['newProducts'].append(product)
      continue
    
    previous = previousMap[sku]
    
    if product['price'] is not None and previous['price'] is not None:
      if product['price'] < previous['price']:
        report['priceDrops'].append({
          'sku': sku,
          'name': product['name'],
          'oldPrice': previous['price'],
          'newPrice': product['price'],
          'difference': round(previous['price'] - product['price'], 2)
        })
      elif product['price'] > previous['price']:
        report['priceIncreases'].append({
          'sku': sku,
          'name': product['name'],
          'oldPrice': previous['price'],
          'newPrice': product['price'],
          'difference': round(product['price'] - previous['price'], 2)
        })
    
    if product['availability'] != previous['availability']:
      report['stockChanges'].append({
        'sku': sku,
        'name': product['name'],
        'old': previous['availability'],
        'new': product['availability']
      })
    
    if (product['price'] == previous['price'] and
        product['availability'] == previous['availability']):
      report['unchanged'] += 1
  
  for sku, product in previousMap.items():
    if sku not in currentMap:
      report['removedProducts'].append(product)
  
  return report


def __saveChangesReport(baseFolder, timestamp, report):
  jsonPath = os.path.join(baseFolder, f'changes_{timestamp}.json')
  __saveJson(jsonPath, report)
  
  print(f'[bold cyan]  - Reporte de cambios: {jsonPath}[/bold cyan]')


def __saveJson(path, data):
  with open(path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)


def __printReport(runData, changesReport):
  products = runData['products']
  prices = [p['price'] for p in products if p['price'] is not None]
  inStock = sum(1 for p in products if p['availability'] == 'in_stock')
  outOfStock = sum(1 for p in products if p['availability'] == 'out_of_stock')
  unknownStock = sum(1 for p in products if p['availability'] == 'unknown')
  
  print('\n[bold yellow]⁕ intelligence report[/bold yellow]')
  print(f'[bold cyan]  - Total productos: {len(products)}[/bold cyan]')
  print(f'[bold green]  - En stock: {inStock}[/bold green]')
  print(f'[bold red]  - Agotados: {outOfStock}[/bold red]')
  print(f'[bold white]  - Sin determinar: {unknownStock}[/bold white]')
  
  if prices:
    print(f'[bold cyan]  - Precio medio: {round(sum(prices) / len(prices), 2)}[/bold cyan]')
    print(f'[bold cyan]  - Precio minimo: {min(prices)}[/bold cyan]')
    print(f'[bold cyan]  - Precio maximo: {max(prices)}[/bold cyan]')
  
  if changesReport.get('previousTimestamp'):
    print('\n[bold yellow]⁕ changes vs previous run[/bold yellow]')
    print(f'[bold green]  - Nuevos productos: {len(changesReport["newProducts"])}[/bold green]')
    print(f'[bold red]  - Productos eliminados: {len(changesReport["removedProducts"])}[/bold red]')
    print(f'[bold green]  - Bajadas de precio: {len(changesReport["priceDrops"])}[/bold green]')
    print(f'[bold red]  - Subidas de precio: {len(changesReport["priceIncreases"])}[/bold red]')
    print(f'[bold yellow]  - Cambios de stock: {len(changesReport["stockChanges"])}[/bold yellow]')
    print(f'[bold white]  - Sin cambios: {changesReport["unchanged"]}[/bold white]')
  else:
    print('\n[bold yellow]  - Primera ejecucion: no hay datos historicos para comparar[/bold yellow]')
  
  print('[bold white]// operation finish[/bold white]')


 # secure function boot ->
if __name__ == '__main__':
  typer.run(__main)
