import shutil


def test_pytest_available():
    assert shutil.which("pytest") is not None


def test_black_available():
    assert shutil.which("black") is not None


def test_flake8_available():
    assert shutil.which("flake8") is not None
