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
def cog_count_file(data_dir: Path) -> Path:
    """cog_count.tsv file fixture"""
    return data_dir / "cog_count.tsv"


@pytest.fixture(scope="session")
def cog_download_dir(data_dir: Path) -> Path:
    """cog_download directory fixture"""
    cog_download_dir = data_dir / "cog_download"
    cog_download_dir.mkdir(exist_ok=True)
    return cog_download_dir
