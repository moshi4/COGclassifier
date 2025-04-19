from __future__ import annotations

import csv
import logging
import re
import shlex
import shutil
import subprocess as sp
import tempfile
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from cogclassifier import const


class RpsBlast:
    """RPS-BLAST Run Class"""

    def __init__(
        self,
        query: str | Path,
        db: str | Path,
        *,
        outfile: str | Path | None = None,
        evalue: float = 1e-2,
        thread_num: int = 1,
    ):
        self._query = query
        self._db = db
        self._outfile = outfile
        self._evalue = evalue
        self._thread_num = thread_num

    def run(self) -> BlastAlignmentRecord:
        """Run RPS-BLAST"""
        self.check_installation()
        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = self._outfile
            if outfile is None:
                outfile = Path(tmpdir) / "rpsblast.tsv"
            cmd = f"{self.get_binary_name()} -query {self._query} -db {self._db} -outfmt 6 -out {outfile} -evalue {self._evalue} -num_threads {self._thread_num} -mt_mode 1"  # noqa: E501
            version = self.get_version()
            logger = logging.getLogger(__name__)
            logger.info(f"{'*' * 10} Start RPS-BLAST(v{version}) Search {'*' * 10}")
            self._run_cmd(cmd, logger)
            logger.info(f"{'*' * 10} Finished RPS-BLAST Search {'*' * 10}")
            return BlastAlignmentRecord(outfile)

    @classmethod
    def check_installation(cls, raise_error: bool = True) -> bool:
        """Check tool installation"""
        if shutil.which("rpsblast") is None and shutil.which("rpsblast+") is None:
            if raise_error:
                raise RuntimeError("rpsblast is not installed!!")
            return False
        return True

    @classmethod
    def get_version(cls) -> str:
        """Get tool version"""
        try:
            cmd = f"{cls.get_binary_name()} -version"
            cmd_args = shlex.split(cmd)
            cmd_res = sp.run(cmd_args, capture_output=True, text=True)
            output = cmd_res.stderr if cmd_res.stdout == "" else cmd_res.stdout
            version = re.findall(r"blast (\d+.\d+.\d+)", output, re.MULTILINE)[0]
            return version
        except Exception:
            return const.UNKNOWN_VERSION

    @classmethod
    def get_binary_name(cls) -> str:
        """Binary name"""
        return "rpsblast+" if shutil.which("rpsblast") is None else "rpsblast"

    def _run_cmd(
        self,
        cmd: str,
        logger: logging.Logger,
        stdout_file: str | Path | None = None,
    ) -> None:
        """Run command

        Parameters
        ----------
        cmd : str
            Command to run
        logger : logging.Logger
            Logger object
        stdout_file : str | Path | None, optional
            Write stdout result if file is set
        """
        logger.info(f"$ {cmd}")
        cmd_args = shlex.split(cmd)
        try:
            cmd_res = sp.run(cmd_args, capture_output=True, text=True, check=True)
            # Write stdout result if stdout_file is set
            if stdout_file:
                logger.info(f"> Save cmd stdout results to '{stdout_file}'")
                with open(stdout_file, "w", encoding="utf-8") as f:
                    f.write(cmd_res.stdout)
        except sp.CalledProcessError as e:
            returncode, stdout, stderr = e.returncode, str(e.stdout), str(e.stderr)
            logger.error(f"Failed to run command below ({returncode=})")
            logger.error(f"$ {cmd}")
            stdout_lines = stdout.splitlines()
            if len(stdout_lines) > 0:
                logger.error("STDOUT:")
                for line in stdout_lines:
                    logger.error(f"> {line}")
            stderr_lines = stderr.splitlines()
            if len(stderr_lines) > 0:
                logger.error("STDERR:")
                for line in stderr_lines:
                    logger.error(f"> {line}")
                logger.error("Failed to run 'RPS-BLAST'!!")
                raise
        except FileNotFoundError:
            raise


class BlastAlignment(BaseModel):
    """Blast Alignment Class"""

    qaccver: str  # Query Accession Version
    saccver: str  # Subject Accession Version
    pident: float  # Percent Identity
    length: int  # Alignment Length
    mismatch: int
    gapopen: int
    qstart: int
    qend: int
    sstart: int
    send: int
    evalue: float
    bitscore: float

    model_config = ConfigDict(frozen=True)

    @property
    def as_tsv(self) -> str:
        """Return the fields as tsv"""
        return "\t".join(map(str, self.model_dump().values()))


class BlastAlignmentRecord:
    def __init__(self, blast_outfile: str | Path):
        """Parse tsv format blast result file

        Parameters
        ----------
        blast_outfile : str | Path
            TSV format blast result file

        Returns
        -------
        blast_results : list[BlastResult]
            List of BlastResult
        """
        blast_alns: list[BlastAlignment] = []
        with open(blast_outfile, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                # Ignore header line
                if row[0].startswith("#"):
                    continue
                keys = BlastAlignment.model_fields
                blast_alns.append(BlastAlignment(**dict(zip(keys, row))))  # type: ignore

        self._blast_alns = blast_alns

    @property
    def alignments(self) -> list[BlastAlignment]:
        """Blast alignment results"""
        return self._blast_alns

    @cached_property
    def top_hit_alignments(self) -> list[BlastAlignment]:
        """Top hit blast alignment results"""
        top_hits = []
        top_hit_blast_results = []
        for br in self._blast_alns:
            if br.qaccver in top_hits:
                continue
            top_hits.append(br.qaccver)
            top_hit_blast_results.append(br)
        return top_hit_blast_results

    def __str__(self) -> str:
        return "\n".join([aln.as_tsv for aln in self.alignments])
