 # import libraries ->
import barcode
import typer
from barcode.writer import ImageWriter
from PIL import Image


 # main function ->
def __main():
  number = input(" > Introduce un codigo de 12 digitos: ")
  barcodeFormat = barcode.get_barcode_class('upc')

  customBarcode = barcodeFormat(number, writer = ImageWriter())
  customBarcode.save("customBarcode")


 # secure function boot ->
if __name__ == "__main__":
  typer.run(__main)
