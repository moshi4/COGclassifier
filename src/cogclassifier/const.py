import os
from pathlib import Path

COG_FUN_FTP = "https://ftp.ncbi.nih.gov/pub/COG/COG2024/data/fun-24.tab"
COG_DEF_FTP = "https://ftp.ncbi.nih.gov/pub/COG/COG2024/data/cog-24.def.tab"

CDDID_TBL_FTP = "https://ftp.ncbi.nih.gov/pub/mmdb/cdd/cddid.tbl.gz"
COG_LE_FTP = "https://ftp.ncbi.nih.gov/pub/mmdb/cdd/little_endian/Cog_LE.tar.gz"

RESOURCES_DIR = Path(__file__).parent / "resources"
COG_FUNC_CATEGORY_FILE = RESOURCES_DIR / "cog_func_category.tsv"
COG_DEFINITION_FILE = RESOURCES_DIR / "cog_definition.tsv"

_cpu_count = os.cpu_count()
MIN_CPU = 1
MAX_CPU = 1 if _cpu_count is None else _cpu_count
DEFAULT_CPU = 1 if MAX_CPU == 1 else MAX_CPU - 1

CACHE_DIR = Path.home() / ".cache" / "cogclassifier_v2"

UNKNOWN_VERSION = "?.?.?"
