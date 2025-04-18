from __future__ import annotations

import csv
import gzip
import logging
from functools import cached_property
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, ConfigDict

from cogclassifier.blast import BlastAlignmentRecord


class CogFuncCategory(BaseModel):
    """COG Functional Category Class"""

    letter: str
    group: str
    color: str
    desc: str

    model_config = ConfigDict(frozen=True)

    @property
    def as_tsv(self) -> str:
        """Return the fields as tsv"""
        return "\t".join(map(str, self.model_dump().values()))


class CogFuncCategoryRecord:
    """COG Functional Category Record Class"""

    def __init__(self, cog_fc_file: str | Path):
        """
        Parameters
        ----------
        config_file : str | Path
            COG functional category file
        """
        cfc_list: list[CogFuncCategory] = []
        with open(cog_fc_file, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                keys = CogFuncCategory.model_fields
                cfc_list.append(CogFuncCategory(**dict(zip(keys, row))))

        self._letters = [cfc.letter for cfc in cfc_list]
        self._cfc_list = cfc_list
        self._letter2cfc = {cfc.letter: cfc for cfc in cfc_list}

    def get(self, letter: str) -> CogFuncCategory:
        """Get target letter COG info"""
        return self[letter]

    def get_all(self) -> list[CogFuncCategory]:
        """Get all COG info"""
        return self._cfc_list

    def get_letters(self) -> list[str]:
        """Get all COG letters"""
        return self._letters

    def __str__(self) -> str:
        return "\n".join([cfc.as_tsv for cfc in self.get_all()])

    def __len__(self) -> int:
        return len(self.get_all())

    def __getitem__(self, letter: str) -> CogFuncCategory:
        return self._letter2cfc[letter]


class CogDefinition(BaseModel):
    """COG Definition Class"""

    id: str
    letter: str
    cog_name: str
    gene_name: str
    func_pathway: str
    pubmed_id_list: list[str]
    pdb_id_list: list[str]

    model_config = ConfigDict(frozen=True)

    @property
    def one_letter(self) -> str:
        """One letter (e.g. letter=`KT` -> one_letter=`K`)"""
        return self.letter[0]

    @property
    def as_tsv(self) -> str:
        """Return the fields as tsv"""
        return "\t".join(
            (
                self.id,
                self.letter,
                self.cog_name,
                self.gene_name,
                self.func_pathway,
                ";".join(self.pubmed_id_list),
                ";".join(self.pdb_id_list),
            )
        )


class CogDefinitionRecord:
    """COG Definition Record Class"""

    def __init__(self, cog_def_file: str | Path):
        cog_defs: list[CogDefinition] = []
        with open(cog_def_file, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                # COG definition file does not have a fixed number of columns per line
                cog_id, letter, cog_name, gene_name = row[0:4]
                func_pathway = row[4] if len(row) > 4 else ""
                pubmed_id_list = row[5].split(";") if len(row) > 5 else []
                pdb_id_list = row[6].split(";") if len(row) > 6 else []
                cog_defs.append(
                    CogDefinition(
                        id=cog_id,
                        letter=letter,
                        cog_name=cog_name,
                        gene_name=gene_name,
                        func_pathway=func_pathway,
                        pubmed_id_list=pubmed_id_list,
                        pdb_id_list=pdb_id_list,
                    )
                )

        self._id_list = [cd.id for cd in cog_defs]
        self._cog_defs = cog_defs
        self._id2cog_def = {cd.id: cd for cd in cog_defs}

    def get(self, cog_id: str) -> CogDefinition | None:
        """Get target ID COG definition info"""
        return self[cog_id]

    def get_all(self) -> list[CogDefinition]:
        """Get all COG definition info"""
        return self._cog_defs

    def get_id_list(self) -> list[str]:
        """Get all COG ID"""
        return self._id_list

    def __str__(self) -> str:
        return "\n".join([cd.as_tsv for cd in self.get_all()])

    def __len__(self) -> int:
        return len(self.get_all())

    def __getitem__(self, cog_id: str) -> CogDefinition | None:
        return self._id2cog_def.get(cog_id)


class CogCddIdTable:
    """COG ID & CDD ID table for ID conversion"""

    def __init__(self, cddid_table_file: str | Path):
        cdd_id2cog_id, cog_id2cdd_id = dict(), dict()
        xopen = gzip.open if Path(cddid_table_file).suffix == ".gz" else open
        with xopen(cddid_table_file, mode="rt", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                cdd_id, acc_id = row[0], row[1]
                if acc_id.startswith("COG"):
                    cdd_id2cog_id[cdd_id] = acc_id
                    cog_id2cdd_id[acc_id] = cdd_id
        self._cdd_id2cog_id: dict[str, str] = cdd_id2cog_id
        self._cog_id2cdd_id: dict[str, str] = cog_id2cdd_id

    def to_cog_id(self, cddid: str) -> str:
        """Convert CDD ID to COG ID"""
        return self._cdd_id2cog_id[cddid]

    def to_cdd_id(self, cogid: str) -> str:
        """Convert COG ID to CDD ID"""
        return self._cog_id2cdd_id[cogid]


class CogClassifyStats:
    """COG Classify Result Statistics Class"""

    def __init__(
        self,
        query: str | Path,
        blast_rec: BlastAlignmentRecord,
        cog_fc_rec: CogFuncCategoryRecord,
        cog_def_rec: CogDefinitionRecord,
        cog_cdd_id_table: CogCddIdTable,
    ):
        self._query = query
        self.blast_rec = blast_rec
        self.cog_fc_rec = cog_fc_rec
        self.cog_def_rec = cog_def_rec
        self.cog_cdd_id_table = cog_cdd_id_table

    @cached_property
    def classify_count(self) -> int:
        """Number of COG classified sequence"""
        return len(self.query_classify_df)

    @cached_property
    def query_count(self) -> int:
        """Number of query fasta sequence"""
        with open(self._query) as f:
            return len(list(filter(lambda line: line.startswith(">"), f.readlines())))

    @cached_property
    def classify_ratio(self) -> float:
        """Ratio of COG classified sequence"""
        return self.classify_count / self.query_count

    @cached_property
    def query_classify_df(self) -> pd.DataFrame:
        """COG classified query dataframe"""
        df_rows = []
        for aln in self.blast_rec.top_hit_alignments:
            # Get query & CDD ID from rpsblast hits
            query_id, cdd_id = aln.qaccver, aln.saccver.replace("CDD:", "")
            # Convert CDD ID to COG ID
            cog_id = self.cog_cdd_id_table.to_cog_id(cdd_id)
            # Get COG definition by COG ID (Some COG ID not found in definition)
            cog_def = self.cog_def_rec[cog_id]
            if cog_def is None:
                logger = logging.getLogger(__name__)
                logger.debug(
                    f"{cog_id=} is not found in COG definition ({query_id=}, {cdd_id=})"
                )
                continue
            # Get COG functional category by COG letter
            cog_fc = self.cog_fc_rec[cog_def.one_letter]
            df_rows.append(
                (
                    query_id,
                    cog_id,
                    cdd_id,
                    aln.evalue,
                    aln.pident,
                    cog_def.gene_name,
                    cog_def.cog_name,
                    cog_def.one_letter,
                    cog_fc.desc,
                ),
            )
        return pd.DataFrame(
            df_rows,
            columns=[
                "QUERY_ID",
                "COG_ID",
                "CDD_ID",
                "EVALUE",
                "IDENTITY",
                "GENE_NAME",
                "COG_NAME",
                "COG_LETTER",
                "COG_DESCRIPTION",
            ],
        )

    @cached_property
    def count_summary_df(self) -> pd.DataFrame:
        """Summary COG classification count result dataframe"""
        df_rows = []
        for cog_fc in self.cog_fc_rec.get_all():
            count = (
                self.query_classify_df["COG_LETTER"]
                .value_counts()
                .get(cog_fc.letter, 0)
            )
            df_rows.append(
                (
                    cog_fc.letter,
                    count,
                    cog_fc.group,
                    cog_fc.color,
                    cog_fc.desc,
                )
            )
        return pd.DataFrame(
            df_rows,
            columns=[
                "LETTER",
                "COUNT",
                "GROUP",
                "COLOR",
                "DESCRIPTION",
            ],
        )
