import os
from pathlib import Path
import platform
import stat
from typing import Tuple
import urllib.request
import warnings


def get_platform_info() -> Tuple[str, str, str]:
    system = platform.system()
    machine = platform.machine().lower()

    match system:
        case "Linux":
            if "aarch64" in machine or "arm64" in machine:
                return "linux", "arm64", "agfapi_linux_arm64"
            else:
                return "linux", "x86_64", "agfapi_linux_x86_64"
        case "Windows":
            if "arm64" in machine:
                return "windows", "arm64", "agfapi_windows_arm64.exe"
            else:
                return "windows", "x86_64", "agfapi_windows_x86_64.exe"
        case _:
            raise RuntimeError(f"Unsupported platform: {system} {machine}")

def get_binary_cache_dir(version: str) -> Path:
    home = os.getenv("AGFAPI_HOME_DIR", Path.home() / ".agfapi")
    cache_dir = Path(home) / "bin" / "agfapi" / version
    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir

def download_binary(version: str) -> str:
    system, arch, binary_name = get_platform_info()
    if version != "latest" and not version.startswith("v"):
        version = "v" + version

    cache_dir = get_binary_cache_dir(version)
    binary_path = cache_dir / binary_name

    if binary_path.exists():
        return str(binary_path)

    if version == "latest":
        url = f"https://github.com/s-hammon/agfapi/releases/latest/download/{binary_name}"
    else:
        url = f"https://github.com/s-hammon/agfapi/releases/download/{version}/{binary_name}"

    print(f"Downloading agfapi binary ({version}) for {system}/{arch}...")

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()

        with open(binary_path, "wb") as f:
            f.write(data)

        st = binary_path.stat()
        binary_path.chmod(st.st_mode | stat.S_IEXEC)
        return str(binary_path)

    except Exception as e:
        warnings.warn(f"Failed to download agfapi binary: {e}")
        raise RuntimeError(f"Could not download agfapi binary: {e}")

def get_agfapi_version():
    version = os.getenv("AGFAPI_VERSION")
    if version:
        return version

    try:
        from importlib.metadata import version as pkg_version
        version = pkg_version("agfapi")

        if "dev" in version or version == "0.0.0":
            return "latest"
        if ".post" in version:
            version = version.split(".post")[0]

        return version

    except Exception:
        return "latest"

try:
    VERSION = get_agfapi_version()
    AGFAPI_BIN = download_binary(VERSION)
except Exception as e:
    raise RuntimeError(f"agfapi: cannot initialize binary: {e}")
