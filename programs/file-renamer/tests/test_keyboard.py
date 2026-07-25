"""Tests de las utilidades de teclado."""

import pytest

from simple_file_renamer.utils.keyboard import parse_yes_no


@pytest.mark.parametrize(
    "value,default,expected",
    [
        ("s", False, True),
        ("S", False, True),
        (" si ", False, True),
        ("yes", False, True),
        ("Y", False, True),
        ("n", False, False),
        ("NO", False, False),
        ("", True, True),
        ("", False, False),
        ("maybe", False, False),
        ("maybe", True, True),
    ],
)
def test_parse_yes_no(value: str, default: bool, expected: bool) -> None:
    assert parse_yes_no(value, default=default) is expected
