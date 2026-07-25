 # import libraries ->
import os
import re
import requests
import typer
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from rich import print


 # main function ->
def __main():
  print('[bold blue]⁕ function loading...[/bold blue]')
  __inputData()


 # secondary functions ->
def __downloadImages(url, folder):
  if not os.path.exists(folder):
    os.makedirs(folder)
  
  headers = {'User-Agent': 'Mozilla/5.0 (compatible; scrap-web-images/1.0)'}
  
  try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(f'[bold red]  - Failed to fetch the page: {e}[/bold red]')
    return
  
  soup = BeautifulSoup(response.text, 'html.parser')
  images = soup.find_all('img')
  
  imgUrls = []
  for img in images:
    imgUrl = img.get('src') or img.get('data-src')
    
    if not imgUrl or imgUrl.startswith('data:'):
      continue
    
    if not imgUrl.startswith('http'):
      imgUrl = urljoin(url, imgUrl)
    
    imgUrl = imgUrl.split('#')[0]
    
    if imgUrl not in imgUrls:
      imgUrls.append(imgUrl)
  
  if not imgUrls:
    print('[bold yellow]  - No images found on the page.[/bold yellow]')
    print('[bold white]// operation finish[/bold white]')
    return
  
  print(f'[bold cyan]  - Found {len(imgUrls)} images[/bold cyan]')
  
  downloaded = 0
  failed = 0
  
  with requests.Session() as session, ThreadPoolExecutor(max_workers=8) as executor:
    session.headers.update(headers)
    futureToUrl = {executor.submit(__fetchImage, session, imgUrl, folder): imgUrl for imgUrl in imgUrls}
    
    for future in as_completed(futureToUrl):
      if future.result():
        downloaded += 1
      else:
        failed += 1
  
  print(f'[bold cyan]  - Downloaded: {downloaded} | Failed: {failed}[/bold cyan]')
  print('[bold white]// operation finish[/bold white]')

def __fetchImage(session, imgUrl, folder):
  parsed = urlparse(imgUrl)
  imgName = os.path.basename(parsed.path)
  
  if not imgName or '.' not in imgName:
    imgName = 'image.jpg'
  
  imgName = re.sub(r'[^a-zA-Z0-9._-]', '_', imgName)
  imgName = __getUniqueName(folder, imgName)
  imgPath = os.path.join(folder, imgName)
  
  try:
    response = session.get(imgUrl, timeout=15, stream=True)
    response.raise_for_status()
    
    contentType = response.headers.get('content-type', '')
    if not contentType.startswith('image/'):
      return False
    
    with open(imgPath, 'wb') as f:
      for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
    
    print(f'[bold green]  - Downloaded {imgName} [/bold green]')
    return True
  
  except Exception as e:
    print(f'[bold red]  - Failed to download {imgUrl}: {e}[/bold red]')
    return False

def __getUniqueName(folder, name):
  if not os.path.exists(os.path.join(folder, name)):
    return name
  
  base, ext = os.path.splitext(name)
  count = 1
  
  while True:
    newName = f"{base}_{count:03d}{ext}"
    if not os.path.exists(os.path.join(folder, newName)):
      return newName
    count += 1

def __inputData():
  print('[bold yellow]⁕ downloading images...[/bold yellow]')
  
  webPage = input(' > Introduce la Url de la que quieres descargar las imagenes: ')
  saveFolder = input(' > Introduce el nombre de la carpeta en la que se guardaran las imagenes: ')
  
  __downloadImages(webPage, saveFolder)
  __renameImages(saveFolder, "image")

def __renameImages(imageFolder, prefix):
  if not os.path.exists(imageFolder):
    print(f'[bold red]  - Folder not found: {imageFolder}[/bold red]')
    return
  
  print('\n[bold yellow]⁕ renaming images...[/bold yellow]')
  
  files = sorted([f for f in os.listdir(imageFolder) if os.path.isfile(os.path.join(imageFolder, f))])
  count = 0
  
  for filename in files:
    src = os.path.join(imageFolder, filename)
    ext = os.path.splitext(filename)[1].lower() or '.jpg'
    
    while True:
      dstName = f"{prefix}-{str(count).zfill(3)}{ext}"
      dst = os.path.join(imageFolder, dstName)
      if not os.path.exists(dst) and src != dst:
        break
      count += 1
    
    try:
      os.rename(src, dst)
      print(f'[bold green]  - renamed image | {dstName} [/bold green]')
      count += 1
    except Exception as e:
      print(f'[bold red]  - Failed to rename {filename}: {e}[/bold red]')
  
  print('[bold white]// operation finish[/bold white]')


 # secure function boot ->
if __name__ == '__main__':
  typer.run(__main)
