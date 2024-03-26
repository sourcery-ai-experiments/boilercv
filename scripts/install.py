# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "zstandard==0.22.0",
# ]
# ///
#
# Source: https://github.com/astral-sh/uv/blob/5270624b113d13525ef2e5bef92516915497dc50/scripts/bootstrap/install.py
# License: https://github.com/astral-sh/uv/blob/5270624b113d13525ef2e5bef92516915497dc50/LICENSE-MIT
#
# Download required Python versions and install to `bin`
# Uses prebuilt Python distributions from indygreg/python-build-standalone
#
# This script can be run without Python installed via `install.sh`
#
# Requirements
#
#   pip install zstandard==0.22.0
#
# Usage
#
#   python scripts/bootstrap/install.py
#
# Or
#
#   pipx run scripts/bootstrap/install.py
#
# The Python versions are installed from `.python_versions`.
# Python versions are linked in-order such that the _last_ defined version will be the default.
#
# Version metadata can be updated with `fetch-version-metadata.py`

import concurrent.futures
import hashlib
import json
import platform
import shutil
import sys
import sysconfig
import tarfile
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

import zstandard

# Setup some file paths
THIS_DIR = Path(__file__).parent
BIN_DIR = Path("bin")
INSTALL_DIR = BIN_DIR / "versions"
with urllib.request.urlopen(
    "https://raw.githubusercontent.com/astral-sh/uv/5270624b113d13525ef2e5bef92516915497dc50/.python-versions"
) as response:
    versions = response.read().decode("utf-8").splitlines()
with urllib.request.urlopen(
    "https://raw.githubusercontent.com/astral-sh/uv/5270624b113d13525ef2e5bef92516915497dc50/scripts/bootstrap/versions.json"
) as response:
    versions_metadata = json.loads(response.read().decode("utf-8"))

# Map system information to those in the versions metadata
ARCH_MAP = {"aarch64": "arm64", "amd64": "x86_64"}
PLATFORM_MAP = {"win32": "windows"}
PLATFORM = sys.platform
ARCH = platform.machine().lower()
INTERPRETER = "cpython"


def decompress_file(archive_path: Path, output_path: Path):
    if not str(archive_path).endswith(".tar.zst"):
        raise ValueError(f"Unknown archive type {archive_path.suffix}")
    dctx = zstandard.ZstdDecompressor()

    with tempfile.TemporaryFile(suffix=".tar") as ofh:
        with archive_path.open("rb") as ifh:
            dctx.copy_stream(ifh, ofh)
        ofh.seek(0)
        with tarfile.open(fileobj=ofh) as z:
            z.extractall(output_path)  # noqa: S202  # pyright: ignore[reportDeprecated]


def sha256_file(path: Path):
    h = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            if chunk := file.read(h.block_size):
                h.update(chunk)
            else:
                break
    return h.hexdigest()


def get_key(version):
    if platform.system() == "Linux":
        libc = sysconfig.get_config_var("SOABI").split("-")[-1]
    else:
        libc = "none"
    return f"{INTERPRETER}-{version}-{PLATFORM_MAP.get(PLATFORM, PLATFORM)}-{ARCH_MAP.get(ARCH, ARCH)}-{libc}"


def download(version):
    key = get_key(version)
    install_dir = INSTALL_DIR / f"{INTERPRETER}@{version}"
    print(f"Downloading {key}")  # noqa: T201

    url = versions_metadata[key]["url"]

    if not url:
        print(f"No matching download for {key}")  # noqa: T201
        sys.exit(1)

    filename = url.split("/")[-1]
    print(f"Downloading {urllib.parse.unquote(filename)}")  # noqa: T201
    download_path = THIS_DIR / filename
    with (
        urllib.request.urlopen(url) as response,  # noqa: S310
        download_path.open("wb") as download_file,
    ):
        shutil.copyfileobj(response, download_file)

    if sha := versions_metadata[key]["sha256"]:
        print("Verifying checksum...", end="")  # noqa: T201
        if sha256_file(download_path) != sha:
            print(" FAILED!")  # noqa: T201
            sys.exit(1)
        print(" OK")  # noqa: T201

    else:
        print(f"WARNING: no checksum for {key}")  # noqa: T201
    if install_dir.exists():
        shutil.rmtree(install_dir)
    print("Extracting to", install_dir)  # noqa: T201
    install_dir.parent.mkdir(parents=True, exist_ok=True)

    # n.b. do not use `.with_suffix` as it will replace the patch Python version
    extract_dir = Path(f"{install_dir}.tmp")

    decompress_file(THIS_DIR / filename, extract_dir)
    (extract_dir / "python").rename(install_dir)
    (THIS_DIR / filename).unlink()
    extract_dir.rmdir()

    return install_dir


def install(version, install_dir):
    key = get_key(version)

    if PLATFORM == "win32":
        executable = install_dir / "install" / "python.exe"
    else:
        # Use relative paths for links so if the bin is moved they don't break
        executable = (
            "." / install_dir.relative_to(BIN_DIR) / "install" / "bin" / "python3"
        )

    major = versions_metadata[key]["major"]
    minor = versions_metadata[key]["minor"]

    # Link as all version tuples, later versions in the file will take precedence
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    targets = [
        (BIN_DIR / f"python{version}"),
        (BIN_DIR / f"python{major}.{minor}"),
        (BIN_DIR / f"python{major}"),
        (BIN_DIR / "python"),
    ]
    for target in targets:
        target.unlink(missing_ok=True)
        if PLATFORM == "win32":
            target.hardlink_to(executable)
        else:
            target.symlink_to(executable)

    print(f"Installed executables for python{version}")  # noqa: T201


if __name__ == "__main__":
    if INSTALL_DIR.exists():
        print("Removing existing installations...")  # noqa: T201
        shutil.rmtree(INSTALL_DIR)

    # Download in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=len(versions)) as executor:
        futures = [
            (version, executor.submit(download, version)) for version in versions
        ]

    # Install sequentially so overrides are respected
    for version, future in futures:
        install_dir = future.result()
        install(version, install_dir)

    print("Done!")  # noqa: T201
