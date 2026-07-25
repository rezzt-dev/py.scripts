 # tests for password generator and analyzer ->

from __future__ import annotations

import string

import pytest

from only_one_key.core.password import passwordAnalyzer, passwordGenerator


class TestPasswordGenerator:
  def test_generatesRequestedLength(self):
    password = passwordGenerator(16)
    assert len(password) == 16

  def test_minimumLengthEnforced(self):
    with pytest.raises(ValueError, match="minima es 8"):
      passwordGenerator(4)

  def test_requiresAtLeastOnePool(self):
    with pytest.raises(ValueError, match="al menos un tipo"):
      passwordGenerator(12, useUppercase=False, useLowercase=False, useDigits=False, usePunctuation=False)

  def test_includesAllRequestedPools(self):
    password = passwordGenerator(
      20,
      useUppercase=True,
      useLowercase=True,
      useDigits=True,
      usePunctuation=True,
    )
    assert any(c in string.ascii_uppercase for c in password)
    assert any(c in string.ascii_lowercase for c in password)
    assert any(c in string.digits for c in password)
    assert any(c in string.punctuation for c in password)


class TestPasswordAnalyzer:
  def test_veryWeak(self):
    level, score = passwordAnalyzer("abc")
    assert level == "very weak"
    assert 0 <= score < 40

  def test_weak(self):
    level, score = passwordAnalyzer("abcdef12")
    assert level == "weak"
    assert 40 <= score < 60

  def test_veryWeakShortPassword(self):
    """una contrasena con tipos variados pero menos de 8 caracteres sigue siendo muy debil."""
    level, score = passwordAnalyzer("Abcdef1")
    assert level == "very weak"
    assert score < 40

  def test_safe(self):
    level, score = passwordAnalyzer("Abcdef1!")
    assert level in ("safe", "very safe")
    assert score >= 60

  def test_verySafe(self):
    level, score = passwordAnalyzer("MyS3cur3P@ssw0rd!2024")
    assert level == "very safe"
    assert score >= 80

  def test_scoreCappedAt100(self):
    _, score = passwordAnalyzer("A" * 50 + "1!a")
    assert score == 100
