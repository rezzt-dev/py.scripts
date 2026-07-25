 # import libraries ->
import typer
from PIL import Image
from pyzbar.pyzbar import decode
from rich import print


 # main function ->
def __main():
  image = Image.open("C:/Users/Administrator/Documents/python-projects/customBarcode.png")
  decodeObjects = decode(image)

  for obj in decodeObjects:
    print(f"El código UPC es: {obj.data.decode('utf-8')}")


 # secure function boot ->
if __name__ == "__main__":
  typer.run(__main)
