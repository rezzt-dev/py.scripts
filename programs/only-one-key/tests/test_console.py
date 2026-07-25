 # tests for console helpers ->

from __future__ import annotations

from unittest.mock import patch

from only_one_key.ui import console


class TestPromptQuit:
  def test_returnsTrueWhenUserPressesQ(self):
    with patch.object(console, "ask", return_value="q"):
      assert console.promptQuit() is True

  def test_returnsTrueForUppercaseQ(self):
    with patch.object(console, "ask", return_value="Q"):
      assert console.promptQuit() is True

  def test_returnsFalseForOtherInput(self):
    with patch.object(console, "ask", return_value="s"):
      assert console.promptQuit() is False

  def test_returnsFalseForEmptyInput(self):
    with patch.object(console, "ask", return_value=""):
      assert console.promptQuit() is False


class TestCopyToClipboard:
  def test_returnsTrueOnSuccess(self):
    with patch("subprocess.run") as mockRun:
      mockRun.return_value.returncode = 0
      assert console.copyToClipboard("secret") is True

  def test_returnsFalseWhenNoToolAvailable(self):
    with patch("subprocess.run") as mockRun:
      mockRun.side_effect = FileNotFoundError()
      assert console.copyToClipboard("secret") is False

  def test_returnsFalseOnUnexpectedError(self):
    with patch("subprocess.run", side_effect=OSError("boom")):
      assert console.copyToClipboard("secret") is False
