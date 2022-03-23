from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Data directory fixture"""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def example_fasta_file(data_dir: Path) -> Path:
    """example.faa file fixture"""
    return data_dir / "example.faa"


@pytest.fixture(scope="session")
def classifier_count_file(data_dir: Path) -> Path:
    """classifier_count.tsv file fixture"""
    return data_dir / "classifier_count.tsv"


@pytest.fixture(scope="session")
def cog_download_dir(data_dir: Path) -> Path:
    """cog_download directory fixture"""
    cog_download_dir = data_dir / "cog_download"
    cog_download_dir.mkdir(exist_ok=True)
    return cog_download_dir


@pytest.fixture(scope="session")
def remove_small_download_files(cog_download_dir: Path):
    """Delete 'cog-20.def.tab' & 'fun-20.tab' files"""
    cog_def_file = cog_download_dir / "cog-20.def.tab"
    cog_fun_file = cog_download_dir / "fun-20.tab"
    yield
    if cog_def_file.exists():
        cog_def_file.unlink()
    if cog_fun_file.exists():
        cog_fun_file.unlink()
