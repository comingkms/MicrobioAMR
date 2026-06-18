

from __future__ import annotations

import importlib
import importlib.metadata as metadata
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd
import pytest



# root detection


THIS_FILE = Path(__file__).resolve()



def _dedupe(paths: Iterable[Path]) -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(rp)
    return out


def _ancestors(start: Path) -> list[Path]:

    start = start.resolve()
    if start.is_file():
        start = start.parent
    return [start, *start.parents]


def _has_mamr_script(root: Path) -> bool:
    return any((root / name).is_file() for name in ["MAMR", "MAMR.py", "MAMR.py", "mamr.py"])


def _has_project_databases(root: Path) -> bool:
    amr_names = ["AMR_database", "AMR_dabase", "amr_database", "AMR_db", "amr_db"]
    emu_names = ["Emu_database", "emu_database", "EMU_database", "emu_datebase", "emu_db", "EMU_db"]
    return any((root / n).is_dir() for n in amr_names) and any((root / n).is_dir() for n in emu_names)


def _find_project_root() -> Path:

    if os.environ.get("MAMR_PROJECT_ROOT"):
        root = Path(os.environ["MAMR_PROJECT_ROOT"]).resolve()
        assert root.exists() and root.is_dir(), f"MAMR_PROJECT_ROOT does not exist: {root}"
        return root

    search_roots = _dedupe(_ancestors(THIS_FILE) + _ancestors(Path.cwd()))


    for root in search_roots:
        if _has_mamr_script(root) and _has_project_databases(root):
            return root


    for root in search_roots:
        if _has_mamr_script(root):
            return root

    pytest.fail(
        "Could not locate project_root. Expected a parent folder containing MAMR_9. "
        "Set MAMR_PROJECT_ROOT=/path/to/project_root if needed."
    )


PROJECT_ROOT = _find_project_root()
DEFAULT_TEST_ROOT = PROJECT_ROOT / "test"
TEST_ROOT = Path(os.environ.get("MAMR_TEST_ROOT", DEFAULT_TEST_ROOT)).resolve()

TIMEOUT = int(os.environ.get("MAMR_TEST_TIMEOUT", "1800"))
THREADS = os.environ.get("MAMR_THREADS", "4")
STRICT_TOOL_VERSION = os.environ.get("STRICT_TOOL_VERSION", "1") not in {
    "0", "false", "False", "no", "NO"
}

AMR_TEST_DIR = Path(os.environ.get("AMR_TEST_DIR", TEST_ROOT / "AMR")).resolve()
BAC_TEST_DIR = Path(os.environ.get("BAC_TEST_DIR", TEST_ROOT / "BAC")).resolve()



# Dependency

REQUIRED_PYTHON_PACKAGES = {
    "pandas": "pandas",
    "numpy": "numpy",
    "scipy": "scipy",
    "termcolor": "termcolor",
    "tqdm": "tqdm",
    "pysam": "pysam",
    #"pstats": "pstats",
    "kneed": "kneed",
    "sklearn": "scikit-learn",
}


REQUIRED_EXTERNAL_TOOLS = [
    "fastp",
    "bwa-mem2",
    "porechop",
    "gunzip",
    "chopper",
    "emu",
]

VERSION_COMMANDS = {
    "fastp": [["fastp", "--version"], ["fastp", "-v"]],
    "bwa-mem2": [["bwa-mem2", "version"], ["bwa-mem2"]],
    "porechop": [["porechop", "--version"], ["porechop", "-v"]],
    "gunzip": [["gunzip", "--version"]],
    "chopper": [["chopper", "--version"], ["chopper", "-V"]],
    "emu": [["emu", "--version"], ["emu", "version"], ["emu"]],
}



# helpers


def _run_command(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=TIMEOUT,
    )
    assert result.returncode == 0, (
        "Command failed:\n"
        f"  {' '.join(cmd)}\n\n"
        f"Working directory: {cwd}\n"
        f"Return code: {result.returncode}\n\n"
        f"STDOUT:\n{result.stdout}\n\n"
        f"STDERR:\n{result.stderr}"
    )
    return result


def _nonempty_file(path: Path) -> None:
    assert path.exists(), f"Expected output file was not created: {path}"
    assert path.stat().st_size > 0, f"Expected output file is empty: {path}"


def _copytree_clean(src: Path, dst: Path) -> Path:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def _find_named_dir(env_var: str, preferred_names: Iterable[str]) -> Path:
    if os.environ.get(env_var):
        path = Path(os.environ[env_var]).resolve()
        assert path.exists() and path.is_dir(), f"{env_var} must be an existing folder: {path}"
        return path

    for name in preferred_names:
        candidate = PROJECT_ROOT / name
        if candidate.exists() and candidate.is_dir():
            return candidate.resolve()

    pytest.fail(
        f"Could not find folder for {env_var}.\n"
        f"Project root detected as: {PROJECT_ROOT}\n"
        f"Tried folder names: {list(preferred_names)}"
    )


def _find_file(
    folder: Path,
    env_var: str,
    preferred_names: Iterable[str],
    fallback_patterns: Iterable[str],
) -> Path:
    if os.environ.get(env_var):
        path = Path(os.environ[env_var]).resolve()
        assert path.exists() and path.is_file(), f"{env_var} must be an existing file: {path}"
        return path

    for name in preferred_names:
        candidate = folder / name
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()

    matches: list[Path] = []
    for pattern in fallback_patterns:
        matches.extend(sorted(folder.glob(pattern)))

    matches = [p for p in matches if p.exists() and p.is_file()]
    if matches:
        return matches[0].resolve()

    pytest.fail(
        f"Could not find file for {env_var} in {folder}.\n"
        f"Tried preferred names: {list(preferred_names)}\n"
        f"Fallback patterns: {list(fallback_patterns)}"
    )


def _find_fastq_dir(base: Path, env_var: str) -> Path:
    if os.environ.get(env_var):
        path = Path(os.environ[env_var]).resolve()
        assert path.exists() and path.is_dir(), f"{env_var} must be an existing folder: {path}"
        assert list(path.glob("*.fastq.gz")), f"{env_var} contains no *.fastq.gz files: {path}"
        return path

    assert base.exists() and base.is_dir(), f"FASTQ test folder does not exist: {base}"


    if list(base.glob("*.fastq.gz")):
        return base.resolve()


    preferred_names = ["query", "queries", "reads", "fastq", "input", "query_files"]
    for name in preferred_names:
        candidate = base / name
        if candidate.is_dir() and list(candidate.glob("*.fastq.gz")):
            return candidate.resolve()

    fastq_dirs = sorted({p.parent for p in base.rglob("*.fastq.gz")})
    if not fastq_dirs:
        pytest.fail(f"No *.fastq.gz files found under {base}. Set {env_var} explicitly.")
    return fastq_dirs[0].resolve()


def _assert_paired_fastqs(query_dir: Path) -> None:
    r1_files = sorted(query_dir.glob("*_R1_001.fastq.gz")) + sorted(query_dir.glob("*_R1.fastq.gz"))
    assert r1_files, f"No R1 FASTQ files found in {query_dir}"

    missing_r2: list[str] = []
    for r1 in r1_files:
        if r1.name.endswith("_R1_001.fastq.gz"):
            r2 = r1.with_name(r1.name.replace("_R1_001.fastq.gz", "_R2_001.fastq.gz"))
        else:
            r2 = r1.with_name(r1.name.replace("_R1.fastq.gz", "_R2.fastq.gz"))
        if not r2.exists():
            missing_r2.append(str(r2))

    assert not missing_r2, "Missing paired R2 FASTQ files:\n" + "\n".join(missing_r2)



#  path fixtures



@pytest.fixture(scope="session")
def mamr_script() -> Path:

    if os.environ.get("MAMR_SCRIPT"):
        script = Path(os.environ["MAMR_SCRIPT"]).resolve()
        assert script.exists() and script.is_file(), f"MAMR_SCRIPT must be an existing file: {script}"
        return script

    for name in ["MAMR", "MAMR.py", "mamr.py", "MicrobioAMR.py", "microbioamr.py"]:
        candidate = PROJECT_ROOT / name
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()

    pytest.fail(
        f"Could not locate the MAMR pipeline script in detected project root: {PROJECT_ROOT}. "
        "Expected project_root/MAMR_9, or set MAMR_SCRIPT=/path/to/MAMR_9."
    )


@pytest.fixture(scope="session")
def amr_database_dir() -> Path:
    return _find_named_dir(
        "AMR_DATABASE_DIR",
        preferred_names=[
            "AMR_database",
            "AMR_dabase",
            "amr_database",
            "AMR_db",
            "amr_db",
        ],
    )


@pytest.fixture(scope="session")
def amr_database_fasta(amr_database_dir: Path) -> Path:
    return _find_file(
        amr_database_dir,
        env_var="AMR_DATABASE",
        preferred_names=[
            "AmpliSeq_amr_database_4.fasta",  # current file name
            "amr_database.fasta",
            "AMR_database.fasta",
        ],
        fallback_patterns=["*.fasta", "*.fa", "*.fna"],
    )


@pytest.fixture(scope="session")
def amr_annotation(amr_database_dir: Path) -> Path:
    annotation = _find_file(
        amr_database_dir,
        env_var="AMR_ANNOTATION",
        preferred_names=[
            "Tax_final_15.csv",
            "annotation.csv",
            "anno_file.csv",
        ],
        fallback_patterns=["*.csv"],
    )

    expected_cols = {"target", "group", "organism", "gene", "family", "class", "mechanism"}
    header = pd.read_csv(annotation, nrows=0).columns
    missing = expected_cols - set(header)
    assert not missing, (
        f"AMR annotation file is missing required columns: {sorted(missing)}\n"
        f"File: {annotation}\nColumns found: {list(header)}"
    )
    return annotation


@pytest.fixture(scope="session")
def emu_database_dir() -> Path:
    emu_db = _find_named_dir(
        "EMU_DATABASE",
        preferred_names=[
            "Emu_database",
            "emu_database",
            "EMU_database",
            "emu_datebase",
            "emu_db",
            "EMU_db",
        ],
    )

    expected_files = ["species_taxid.fasta", "taxonomy.tsv"]
    missing = [name for name in expected_files if not (emu_db / name).exists()]
    assert not missing, (
        f"EMU database folder is missing expected files: {missing}\n"
        f"Folder: {emu_db}"
    )
    return emu_db

@pytest.fixture(scope="session")
def cor_data_dir() -> Path:

    if os.environ.get("COR_DATA_DIR"):
        path = Path(os.environ["COR_DATA_DIR"]).resolve()
    else:
        path = (TEST_ROOT / "COR_data").resolve()

    assert path.exists() and path.is_dir(), (
        f"Missing COR data folder: {path}\n"
        "Expected: project_root/test/cor_data_dir/"
    )

    amr_file = path / "AMR_gene_combined.csv"
    bac_file = path / "emu-combined-genus.tsv"

    _nonempty_file(amr_file)
    _nonempty_file(bac_file)

    return path

# Dependency


def test_layout(
    mamr_script: Path,
    amr_database_dir: Path,
    amr_database_fasta: Path,
    amr_annotation: Path,
    emu_database_dir: Path,
    cor_data_dir: Path,
) -> None:

    assert TEST_ROOT.exists(), f"Missing test root folder: {TEST_ROOT}"
    assert mamr_script.exists(), f"Missing MAMR script: {mamr_script}"
    assert AMR_TEST_DIR.exists(), f"Missing AMR test folder: {AMR_TEST_DIR}"
    assert BAC_TEST_DIR.exists(), f"Missing BAC test folder: {BAC_TEST_DIR}"
    assert amr_database_dir.exists(), f"Missing AMR database folder: {amr_database_dir}"
    assert amr_database_fasta.exists(), f"Missing AMR database FASTA: {amr_database_fasta}"
    assert amr_annotation.exists(), f"Missing AMR annotation CSV: {amr_annotation}"
    assert emu_database_dir.exists(), f"Missing EMU database folder: {emu_database_dir}"
    assert cor_data_dir.exists(), f"Missing correlation data folder: {cor_data_dir}"
    _assert_paired_fastqs(_find_fastq_dir(AMR_TEST_DIR, "AMR_QUERY_DIR"))
    _assert_paired_fastqs(_find_fastq_dir(BAC_TEST_DIR, "BAC_QUERY_DIR"))

    print('')
    print("Project root:", PROJECT_ROOT)
    print("Test root:", TEST_ROOT)
    print("MAMR:", mamr_script)
    print("AMR database:", amr_database_fasta)
    print("AMR annotation:", amr_annotation)
    print("BAC database:", emu_database_dir)
    print("COR data:", cor_data_dir)
    print("AMR input:", _find_fastq_dir(AMR_TEST_DIR, "AMR_QUERY_DIR"))
    print("BAC input:", _find_fastq_dir(BAC_TEST_DIR, "BAC_QUERY_DIR"))


def test_python_dependency() -> None:

    versions: dict[str, str] = {}
    for module_name, dist_name in REQUIRED_PYTHON_PACKAGES.items():
        module = importlib.import_module(module_name)
        try:
            version = metadata.version(dist_name)
        except metadata.PackageNotFoundError:
            version = getattr(module, "__version__", None)

        assert version, f"Could not detect version for Python package: {dist_name}"
        versions[dist_name] = str(version)
    print('')
    print("Python dependencies:", versions)


def _detect_tool_version(tool: str) -> str | None:
    commands = VERSION_COMMANDS.get(tool, [[tool, "--version"], [tool, "-v"], [tool]])
    for cmd in commands:
        try:
            result = subprocess.run(cmd, text=True, capture_output=True, timeout=20)
        except (subprocess.SubprocessError, OSError):
            continue

        text = "\n".join([result.stdout.strip(), result.stderr.strip()]).strip()
        if not text:
            continue

        for line in text.splitlines():
            if re.search(r"\d+(?:\.\d+)+", line):
                return line.strip()
        return text.splitlines()[0].strip()
    return None


def test_external_pipeline() -> None:

    versions: dict[str, str] = {}
    for tool in REQUIRED_EXTERNAL_TOOLS:
        exe = shutil.which(tool)
        assert exe, f"Required external tool not found on PATH: {tool}"

        version = _detect_tool_version(tool)
        if STRICT_TOOL_VERSION:
            assert version, (
                f"Could not detect version for external tool: {tool}. "
                "Use STRICT_TOOL_VERSION=0 if this tool is installed but does not report a version."
            )
        versions[tool] = version or "version-not-detected"
    print('')
    print("External pipelines:", versions)


def test_MAMR(mamr_script: Path) -> None:

    result = _run_command([sys.executable, str(mamr_script), "--version"], cwd=PROJECT_ROOT)
    output = result.stdout + result.stderr
    assert re.search(r"\d+(?:\.\d+)+", output), (
        "MAMR --version ran but did not include a version number. "
        f"Output was: {output}"
    )
    print('')
    print(output.strip())



# AMR module



@pytest.fixture(scope="session")
def amr_run(
    tmp_path_factory: pytest.TempPathFactory,
    mamr_script: Path,
    amr_database_fasta: Path,
    amr_annotation: Path,
) -> Path:
    """Run the AMR module once in a temporary working directory."""
    query_src = _find_fastq_dir(AMR_TEST_DIR, "AMR_QUERY_DIR")
    _assert_paired_fastqs(query_src)

    work_dir = tmp_path_factory.mktemp("mamr_amr")
    query_dir = _copytree_clean(query_src, work_dir / "AMR_query")
    output_dir = work_dir / "AMR_output"

    cmd = [
        sys.executable,
        str(mamr_script),
        "AMR",
        "-amr_db",
        str(amr_database_fasta),
        "-a",
        str(amr_annotation),
        "-amr_q",
        str(query_dir),
        "-amr_o",
        str(output_dir),
        "-t",
        THREADS,
        "-m",
        os.environ.get("AMR_FILTERING_MODE", "2"),
    ]
    _run_command(cmd, cwd=work_dir)
    return output_dir


def test_AMR(amr_run: Path) -> None:

    resistome_dir = amr_run / "Resistomes"
    combined = resistome_dir / "AMR_gene_combined.csv"

    assert resistome_dir.is_dir(), f"AMR Resistomes output folder missing: {resistome_dir}"
    _nonempty_file(combined)

    df = pd.read_csv(combined)
    assert not df.empty, "AMR_gene_combined.csv was created but contains no rows."
    assert "gene" in df.columns, "AMR_gene_combined.csv should include a 'gene' column."

    metadata_cols = {"gene", "target", "group", "organism", "class", "mechanism", "family"}
    sample_cols = [c for c in df.columns if c not in metadata_cols and not c.startswith("Unnamed")]
    assert sample_cols, "AMR_gene_combined.csv should contain at least one sample abundance column."
    print('')
    print("Output:", combined)
    print("Samples:", sample_cols)



# BAC module



@pytest.fixture(scope="session")
def bac_run(
    tmp_path_factory: pytest.TempPathFactory,
    mamr_script: Path,
    emu_database_dir: Path,
) -> Path:

    query_src = _find_fastq_dir(BAC_TEST_DIR, "BAC_QUERY_DIR")
    _assert_paired_fastqs(query_src)

    query_type = os.environ.get("BAC_QUERY_TYPE", "PE").upper()
    assert query_type in {"PE", "ONT"}, "BAC_QUERY_TYPE must be PE or ONT."

    work_dir = tmp_path_factory.mktemp("mamr_bac")
    query_dir = _copytree_clean(query_src, work_dir / "BAC_query")
    output_dir = work_dir / "BAC_output"

    cmd = [
        sys.executable,
        str(mamr_script),
        "BAC",
        "-emu_db",
        str(emu_database_dir),
        "-bac_q",
        str(query_dir),
        "-qt",
        query_type,
        "-bac_o",
        str(output_dir),
        "-t",
        THREADS,
    ]
    _run_command(cmd, cwd=work_dir)
    return output_dir


def test_BAC(bac_run: Path) -> None:

    combined_dir = bac_run / "combined"
    genus = combined_dir / "emu-combined-genus.tsv"
    species = combined_dir / "emu-combined-species.tsv"

    assert combined_dir.is_dir(), f"BAC combined folder missing: {combined_dir}"
    rel_abundance_files = list(combined_dir.glob("*_rel-abundance.tsv"))
    assert rel_abundance_files, "BAC combined folder should contain per-sample *_rel-abundance.tsv files."

    _nonempty_file(genus)
    _nonempty_file(species)

    genus_df = pd.read_csv(genus, sep="\t")
    species_df = pd.read_csv(species, sep="\t")
    assert not genus_df.empty, "emu-combined-genus.tsv contains no rows."
    assert not species_df.empty, "emu-combined-species.tsv contains no rows."
    assert genus_df.shape[1] >= 2, "Genus combined output should contain taxonomy plus sample columns."
    assert species_df.shape[1] >= 2, "Species combined output should contain taxonomy plus sample columns."
    print('')
    print("Genus:", genus)
    print("Species:", species)
    print("Sample files:", [p.name for p in rel_abundance_files])



# COR module


def test_COR(
    tmp_path: Path,
    mamr_script: Path,
    amr_annotation: Path,
    cor_data_dir: Path,
) -> None:

    cor_output = tmp_path / "COR_output"

    cmd = [
        sys.executable,
        str(mamr_script),
        "COR",
        "-cor_amr",
        str(cor_data_dir),
        "-cor_bac",
        str(cor_data_dir),
        "-a",
        str(amr_annotation),
        "-cor_o",
        str(cor_output),
    ]

    _run_command(cmd, cwd=tmp_path)

    copied_amr = cor_output / "AMR_gene_combined.csv"
    copied_bac = cor_output / "emu-combined-genus.tsv"
    gene_corr = cor_output / "correlation_genus_gene.csv"
    family_corr = cor_output / "correlation_genus_family.csv"

    _nonempty_file(copied_amr)
    _nonempty_file(copied_bac)
    _nonempty_file(gene_corr)
    _nonempty_file(family_corr)

    gene_df = pd.read_csv(gene_corr, sep="\t")
    family_df = pd.read_csv(family_corr, sep="\t")

    gene_cols_lower = {c.lower() for c in gene_df.columns}
    family_cols_lower = {c.lower() for c in family_df.columns}

    assert "organism" in gene_cols_lower, (
        f"Gene correlation output should include 'organism' or 'Organism'; "
        f"got {list(gene_df.columns)}"
    )
    assert "gene" in gene_cols_lower, (
        f"Gene correlation output should include 'gene'; got {list(gene_df.columns)}"
    )

    assert "organism" in family_cols_lower, (
        f"Family correlation output should include 'organism' or 'Organism'; "
        f"got {list(family_df.columns)}"
    )
    assert any(c in family_cols_lower for c in ["family", "gene"]), (
        "Family correlation output should include either 'family' or 'gene'; "
        f"got {list(family_df.columns)}"
    )
    print('')
    print("Input dir:", cor_data_dir)
    print("Gene output:", gene_corr)
    print("family output:", family_corr)

