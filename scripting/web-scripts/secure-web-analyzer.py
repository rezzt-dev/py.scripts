 # import libraries ->
import requests
import typer
from rich import print


 # main function ->
def __main():
  url = input(' > Introduce la Url a comprobar: ')
  esSegura = testURL(url)

  if esSegura is None:
    print('[bold yellow]  - No se pudo analizar la URL.[/bold yellow]')

  elif esSegura:
    print('[bold green]  - La URL es Segura.[/bold green]')

  else:
    print('[bold red]  - La URL No es Segura.[bold red]')


 # secondary function ->
def testURL(url):
  apiKey = 'f26676f8edb40c7d946c42bc63cd38d2d6e657ab0a3c49174d38eb682e3dc942'
  vtUrl = 'https://www.virustotal.com/vtapi/v2/url/report'
  params = {'apikey': apiKey, 'resource': url}
  
  response = requests.get(vtUrl, params=params)
  result = response.json()
  
  if result['response_code'] == 1:
    positives = result['positives']
    total = result['total']
    
    if positives > 0:
      return False
    else:
      return True
  else:
    return None


 # secure function boot ->
if __name__ == '__main__':
  typer.run(__main)