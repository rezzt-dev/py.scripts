 # import libraries ->
import os
import typer
from rich import print
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


 # script constants ->
API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyAiOMdvPW--pumuJURPi-4Ky45bFPTDAoI')
CX = os.getenv('GOOGLE_CX', '71600df756a49497b')
MAX_RESULTS = 100


 # main function ->
def __main():
  print('[bold blue]⁕ function loading...[/bold blue]')

  browseWord = input(' > Introduce la palabra a buscar: ')

  if not browseWord:
    print('[bold red]  - La palabra a buscar no puede estar vacia.[/bold red]')
    return

  try:
    numUrlOutputs = int(input(' > Introduce el numero de Urls a mostrar: '))
  except ValueError:
    print('[bold red]  - El numero de Urls debe ser un numero entero.[/bold red]')
    return

  if numUrlOutputs <= 0:
    print('[bold red]  - El numero de Urls debe ser mayor que cero.[/bold red]')
    return

  if numUrlOutputs > MAX_RESULTS:
    print(f'[bold yellow]  - El numero se limita a {MAX_RESULTS} resultados.[/bold yellow]')
    numUrlOutputs = MAX_RESULTS

  try:
    __returnResults(browseWord, numUrlOutputs)
  except HttpError as err:
    print(f'[bold red]  - Error de la api de google: {err}[/bold red]')
  except Exception as err:
    print(f'[bold red]  - Error inesperado: {err}[/bold red]')


 # secondary functions ->
def __searchUrlWord(browseWord, numResults):
  service = build('customsearch', 'v1', developerKey=API_KEY)
  results = []
  countStart = 1

  while len(results) < numResults:
    query = f"inurl:{browseWord}"
    remaining = numResults - len(results)

    try:
      res = service.cse().list(
        q=query,
        cx=CX,
        start=countStart,
        num=min(10, remaining)
      ).execute()
    except HttpError as err:
      print(f'[bold red]  - Error en la peticion: {err}[/bold red]')
      break

    links = res.get('items', [])
    results.extend(links)
    countStart += 10

    if not links:
      break

  return results[:numResults]


def __returnResults(browseWord, numResults):
  results = __searchUrlWord(browseWord, numResults)

  print('\n[bold yellow]⁕ searching urls...[/bold yellow]')

  for url in results:
    print(f"[bold green]  - {url['link']}[/bold green]")

  print('[bold white] + function finished...[/bold white]\n')


 # secure function boot ->
if __name__ == '__main__':
  typer.run(__main)
