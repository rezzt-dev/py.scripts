 # tests for input validators ->

from __future__ import annotations

import pytest

from only_one_key.utils.validators import parseYesNo, validateMenuOption, validateMinLength


class TestValidateMenuOption:
  def test_validOption(self):
    assert validateMenuOption("3", range(1, 6)) == 3

  def test_invalidString(self):
    with pytest.raises(ValueError, match="numero entero"):
      validateMenuOption("abc", range(1, 6))

  def test_outOfRange(self):
    with pytest.raises(ValueError, match="opcion no valida"):
      validateMenuOption("7", range(1, 6))


class TestValidateMinLength:
  def test_validValue(self):
    assert validateMinLength("hello", 3) == "hello"

  def test_tooShort(self):
    with pytest.raises(ValueError, match="al menos"):
      validateMinLength("ab", 3)

  def test_trimsWhitespace(self):
    assert validateMinLength("  hello  ", 3) == "hello"


class TestParseYesNo:
  def test_affirmativeValues(self):
    assert parseYesNo("s") is True
    assert parseYesNo("S") is True
    assert parseYesNo("si") is True
    assert parseYesNo("yes") is True
    assert parseYesNo("y") is True

  def test_negativeValues(self):
    assert parseYesNo("n") is False
    assert parseYesNo("N") is False
    assert parseYesNo("no") is False

  def test_emptyReturnsFalse(self):
    assert parseYesNo("") is False

  def test_invalidRaises(self):
    with pytest.raises(ValueError):
      parseYesNo("maybe")
