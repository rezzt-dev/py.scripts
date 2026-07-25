 # import libraries ->
import os
import requests
import typer
from PIL import Image, UnidentifiedImageError
from rich import print
from pyzbar.pyzbar import decode


 # main function ->
def __main():
  print('[bold blue]⁕ function loading...[/bold blue]')
  
  filename = input(' > Introduce la imagen del codigo QR: ')
  
  try:
    qrCodeUrl = decodeQr(filename)
  except FileNotFoundError:
    print('[bold red]  - No se encontro el archivo. Revisa la ruta.[/bold red]')
    return
  except UnidentifiedImageError:
    print('[bold red]  - El archivo no es una imagen valida.[/bold red]')
    return
  except Exception as error:
    print(f'[bold red]  - Error al leer el QR: {error}[/bold red]')
    return
  
  if qrCodeUrl is None:
    print('[bold yellow]  - No se detecto ninguna Url en el codigo QR.[/bold yellow]')
    return
  
  print(f'[bold cyan]  - Url detectada: {qrCodeUrl}[/bold cyan]')
  
  try:
    testedUrl = testUrl(qrCodeUrl)
  except requests.exceptions.RequestException as error:
    print(f'[bold red]  - Error de conexion con VirusTotal: {error}[/bold red]')
    return
  except Exception as error:
    print(f'[bold red]  - Error al analizar la Url: {error}[/bold red]')
    return
  
  isSafeUrl(testedUrl)


 # secondary functions ->
def decodeQr (filename):
  with Image.open(filename) as image:
    decodeObject = decode(image)
  
  for obj in decodeObject:
    data = obj.data.decode('utf-8')
    if data.startswith(('http://', 'https://')):
      return data
  
  return None

def testUrl (url):
  apiKey = os.getenv('VT_API_KEY', 'f26676f8edb40c7d946c42bc63cd38d2d6e657ab0a3c49174d38eb682e3dc942')
  vtUrl = 'https://www.virustotal.com/vtapi/v2/url/report'
  params = {'apikey': apiKey, 'resource': url}
  headers = {'User-Agent': 'secure-qrcode-tester/1.0'}
  
  response = requests.get(vtUrl, params=params, headers=headers, timeout=15)
  response.raise_for_status()
  result = response.json()
  
  if result.get('response_code') == 1:
    positives = result.get('positives', 0)
    total = result.get('total', 0)
    
    print(f'[bold cyan]  - Motores que detectan amenaza: {positives}/{total}[/bold cyan]')
    
    if positives > 0:
      return False
    else:
      return True
  else:
    return None

def isSafeUrl (urlResult):
  if urlResult is None:
    print('[bold yellow]  - No se ha podido analizar la Url.[/bold yellow]')
  elif urlResult:
    print('[bold green]  - La Url es segura. Puedes acceder sin problema.[/bold green]')
  else:
    print('[bold red]  - La Url no es segura. No la abras en el navegador.[/bold red]')


 # secure function boot ->
if __name__ == '__main__':
  typer.run(__main)
