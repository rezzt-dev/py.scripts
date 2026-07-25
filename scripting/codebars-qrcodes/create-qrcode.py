 # import libraries ->
import typer
import qrcode
import qrcode.constants
from rich import print

 # main function ->
def __main():
  def codeQrGenerator (url, filename):
      code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
      )
      
      code.add_data(url)
      code.make(fit=True)
      
      codeImage = code.make_image(fill_color="black", back_color="white")
      codeImage.save(filename)
      
      print(f"[bold green]  - code generated as {filename} [/bold green]")

  print("[bold yellow]  - script loading...[/bold yellow]")

  url = input(" > Introduce el link/url para generar el QR: ")
  filename = input(" > Introduce el nombre para guardar el QR: ")

  codeQrGenerator(url, filename)


 # secure function boot ->
if __name__ == "__main__":
  typer.run(__main)
