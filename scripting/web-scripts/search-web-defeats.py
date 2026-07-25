 # import libraries ->
import re
import typer
import requests
from rich import print
from bs4 import BeautifulSoup


 # main function ->
def __main():
  print('[bold blue]⁕ function loading...[/bold blue]')
  
  url = input(' > introduce la url para analizar: ')
  __scanVulnerabilities(url)
  
  print('[bold purple] > script finalizado. [/bold purple]')


 # secondary functions ->
def __scanVulnerabilities(url):
  print('\n[bold blue]⁕ escaneando vulnerabilidades...[/bold blue]')
  
  try:
    response = requests.get(url)
    response.raise_for_status()
    
  except requests.exceptions.RequestException as e:
    print(f"[bold red]  - Error al acceder a la URL: [/bold red] {url}")
    return
  
  soup = BeautifulSoup(response.text, 'html.parser')
  forms = soup.find_all('form')
  
  for form in forms:
    __analizeForms(url, form)
    
  links = soup.find_all('a', href=True)
  for link in links:
    __analizeLinks(url, link)
    
  print('\n[bold white]⁕ function finish.[/bold white]')

def __analizeLinks(baseUrl, link):
  print('\n[bold blue]⁕ analizando link...[/bold blue]')
  
  href = link['href']
  linkUrl = href if 'http' in href else baseUrl + href
  linkText = link.text.strip()
  
  if re.search(r'(javascript:|data)', href, re.IGNORECASE):
    print(f'[bold red]  - enlace potencialmente preligoso, recomendable no acceder![/bold red]')
  else:
    print('\n[bold white] > enlace seguro, puedes acceder sin problema.[/bold white]')
    
def __analizeForms(baseUrl, form):
  print('\n[bold blue]⁕ analizando formulario...[/bold blue]')
  
  action = form.get('action')
  method = form.get('method', 'get').lower()
  inputs = form.find_all('input')
  
  formUrl = baseUrl if action == "" or action is None else action
  formUrl = formUrl if 'http' in formUrl else baseUrl + formUrl
  
  print(f'[bold white]  - analizando formulario: [/bold white] {formUrl} [bold white] | metodo: [/bold white] {method.upper()}')
  data = {}
  
  for inputTag in inputs:
    inputName = inputTag.get('name')
    inputType = inputTag.get('type', 'text')
    inputValue = inputTag.get('value', '')
    
    if inputType == 'text':
      data[inputName] = "<script>alert('XSS')</script>"
    elif inputType == 'password':
      data[inputName] = "password 'OR' 1 '=' 1"
    else:
      data[inputName] = inputValue
  
  if method == 'post':
    response = requests.post(formUrl, data=data)
  else:
    response = requests.get(formUrl, params=data)
  
  if "<script>alert('XSS')</script>" in response.text:
    print(f'[bold yellow]  - vulnerabilidad XSS detectada en el formulario: {formUrl} [/bold yellow]')
  
  if "SQL" in response.text or "syntax" in response.text or "error" in response.text:
    print(f"[bold yellow]  - posbile vulneravilidad de inyeccion SQL detectada en el formulario: {formUrl} [/bold yellow]")
    
  else:
    print('\n[bold white] > enlace seguro, puedes acceder sin problema.[/bold white]')
  
  print('\n[bold white]⁕ function finish.[/bold white]')


 # secure function boot ->
if __name__ == '__main__':
  typer.run(__main)