 # credential model ->

from __future__ import annotations

import json
from dataclasses import dataclass, asdict

__all__ = ["Credential"]


@dataclass(frozen=True, slots=True)
class Credential:
  """representa una credencial guardada en el vault."""

  page: str
  username: str
  password: str

  def toJson(self) -> str:
    """serializa la credencial a una cadena json."""
    return json.dumps(asdict(self), ensure_ascii=False)

  @classmethod
  def fromJson(cls, payload: str) -> "Credential":
    """deserializa una cadena json a una credencial."""
    data = json.loads(payload)
    return cls(page=data["page"], username=data["username"], password=data["password"])
