"""Test that the package can be imported correctly."""


def test_can_import_core_utilities():
    """Verify all core utility classes can be imported."""
    from utils import Datetime, Decode, Decorators, Dict, Encode, Integer, Iterable, String

    assert Datetime is not None
    assert Decode is not None
    assert Decorators is not None
    assert Dict is not None
    assert Encode is not None
    assert Integer is not None
    assert Iterable is not None
    assert String is not None


def test_can_import_io_utilities():
    """Verify filesystem and I/O utilities can be imported."""
    from utils import FileIO, Path

    assert FileIO is not None
    assert Path is not None


def test_can_import_pattern_utilities():
    """Verify pattern matching and validation utilities can be imported."""
    from utils import Regex, Validator

    assert Regex is not None
    assert Validator is not None


def test_can_import_other_utilities():
    """Verify other utility classes can be imported."""
    from utils import Logger, Random

    assert Logger is not None
    assert Random is not None


def test_basic_functionality():
    """Verify basic functionality works after import."""
    from utils import Integer, String

    # Test String utility
    # "Hello World" truncated to length 5 with "..." suffix
    # becomes "He..." (2 chars + 3 char suffix = 5 total)
    result = String.truncate("Hello World", length=5, suffix="...")
    assert result == "He..."

    # Test Integer utility
    result = Integer.clamp(10, min_val=0, max_val=5)
    assert result == 5
