 # password generator and analyzer ->

from __future__ import annotations

import secrets
import string
from secrets import SystemRandom

__all__ = ["passwordGenerator", "passwordAnalyzer"]


def passwordGenerator(
  length: int,
  *,
  useUppercase: bool = True,
  useLowercase: bool = True,
  useDigits: bool = True,
  usePunctuation: bool = True,
) -> str:
  """genera una contrasena aleatoria segura usando secrets.

  garantiza que al menos haya un caracter de cada tipo solicitado.
  """
  if length < 8:
    raise ValueError("la longitud minima es 8 caracteres.")

  pools: list[str] = []
  required: list[str] = []

  if useUppercase:
    pools.append(string.ascii_uppercase)
    required.append(secrets.choice(string.ascii_uppercase))
  if useLowercase:
    pools.append(string.ascii_lowercase)
    required.append(secrets.choice(string.ascii_lowercase))
  if useDigits:
    pools.append(string.digits)
    required.append(secrets.choice(string.digits))
  if usePunctuation:
    pools.append(string.punctuation)
    required.append(secrets.choice(string.punctuation))

  if not pools:
    raise ValueError("debes seleccionar al menos un tipo de caracter.")

  alphabet = "".join(pools)
  passwordChars = required + [secrets.choice(alphabet) for _ in range(length - len(required))]
   # systemrandom es el generador criptograficamente seguro de secrets ->
  SystemRandom().shuffle(passwordChars)
  return "".join(passwordChars)


def passwordAnalyzer(password: str) -> tuple[str, int]:
  """analiza la fortaleza de una contrasena y devuelve (nivel, puntuacion 0-100)."""
  score = 0
  maxScore = 100

  length = len(password)
  hasUpper = any(c.isupper() for c in password)
  hasLower = any(c.islower() for c in password)
  hasDigit = any(c.isdigit() for c in password)
  hasPunct = any(c in string.punctuation for c in password)

   # puntuacion por longitud (hasta 40 puntos) ->
  if length >= 16:
    score += 40
  elif length >= 12:
    score += 30
  elif length >= 8:
    score += 20
  else:
    score += length * 2

   # puntuacion por diversidad de caracteres (hasta 60 puntos, 15 por tipo) ->
  criteria = [hasUpper, hasLower, hasDigit, hasPunct]
  score += sum(15 for criterion in criteria if criterion)

  score = min(score, maxScore)

  if length < 8:
    level = "very weak"
    score = min(score, 20)
  elif score >= 80:
    level = "very safe"
  elif score >= 60:
    level = "safe"
  elif score >= 40:
    level = "weak"
  else:
    level = "very weak"

  return level, score
