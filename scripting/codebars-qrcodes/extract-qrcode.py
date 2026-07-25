 # import libraries ->
import typer
from PIL import Image
from pyzbar.pyzbar import decode
from rich import print

 # main function ->
def __main():
  def decodeQr (filename):
    image = Image.open(filename)
    decodeObjects = decode(image)
    
    for obj in decodeObjects:
      print(f"[bold blue] > Linked URL: {obj.data.decode('utf-8')} [/bold blue]")

  filename = input(" > Introduce la Imagen QR a decodificar: ")
  decodeQr(filename)


 # secure function boot ->
if __name__ == "__main__":
  typer.run(__main)