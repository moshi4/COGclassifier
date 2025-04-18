from __future__ import annotations

import logging
import shutil
from pathlib import Path

from cogclassifier import const, utils
from cogclassifier.blast import RpsBlast
from cogclassifier.cog import (
    CogCddIdTable,
    CogClassifyStats,
    CogDefinitionRecord,
    CogFuncCategoryRecord,
)


class CogClassifier:
    """COG Classification Class"""

    def __init__(
        self,
        query: str | Path,
        *,
        download_dir: str | Path | None = None,
        thread_num: int | None = None,
        evalue: float = 1e-2,
    ):
        download_dir = const.CACHE_DIR if download_dir is None else download_dir
        thread_num = const.DEFAULT_CPU if thread_num is None else thread_num

        self._query = Path(query)
        self._download_dir = Path(download_dir)
        self._thread_num = thread_num
        self._evalue = evalue

    def run(self) -> CogClassifyStats:
        """Run COGclassifier"""
        logger = logging.getLogger(__name__)

        # Download NCBI COG & CDD resources
        logger.info("Download COG & CDD resources in NCBI FTP site")
        cddid_tbl_gzfile = utils.ftp_download(const.CDDID_TBL_FTP, self._download_dir)

        cog_le_targz_file = utils.ftp_download(const.COG_LE_FTP, self._download_dir)
        cog_le_dir = self._download_dir / "Cog_LE"
        if not cog_le_dir.exists():
            logger.info(f"Unpack {cog_le_targz_file} => {cog_le_dir}")
            shutil.unpack_archive(cog_le_targz_file, cog_le_dir)

        # Load NCBI COG & CDD resources
        logger.info(f"Load COG Functional Category {const.COG_FUNC_CATEGORY_FILE}")
        cog_fc_rec = CogFuncCategoryRecord(const.COG_FUNC_CATEGORY_FILE)
        logger.info(f"Load COG Definition {const.COG_DEFINITION_FILE}")
        cog_def_rec = CogDefinitionRecord(const.COG_DEFINITION_FILE)
        logger.info(f"Load COG <=> CDD ID Conversion Table {cddid_tbl_gzfile}")
        cog_cdd_id_table = CogCddIdTable(cddid_tbl_gzfile)

        # Run RPS-BLAST
        rpsblast_db = cog_le_dir / "Cog"
        blast_rec = RpsBlast(
            self._query,
            rpsblast_db,
            outfile=None,
            evalue=self._evalue,
            thread_num=self._thread_num,
        ).run()

        stats = CogClassifyStats(
            self._query,
            blast_rec,
            cog_fc_rec,
            cog_def_rec,
            cog_cdd_id_table,
        )
        logger.info(
            f"{stats.classify_ratio * 100:.2f}% ({stats.classify_count} / {stats.query_count}) sequences are classified into COG functional category"  # noqa: E501
        )

        return stats
