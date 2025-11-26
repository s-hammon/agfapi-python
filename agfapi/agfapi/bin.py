import os
from pathlib import Path
import platform
import stat
import tarfile
import tempfile
from typing import Tuple
import urllib
import warnings
import zipfile


def get_platform_info() -> Tuple[str, str, str, str]:
    system = platform.system()
    machine = platform.machine()

    match system:
        case "Linux":
            if machine == "aarch64":
                return "linux", "arm64", "sling_linux_arm64.tar.gz", "agfapi"
            else:
                return "linux", "amd64", "sling_linux_amd64.tar.gz", "agfapi"
        case "Windows":
            if machine == "ARM64":
                return "windows", "arm64", "sling_windows_arm64.tar.gz", "agfapi.exe"
            else:
                return "windows", "amd64", "sling_windows_amd64.tar.gz", "agfapi.exe"
        case _:
            raise RuntimeError(f"Unsupported platform: {system} {machine}")

def get_binary_cache_dir(version: str) -> Path:
    agfapi_home = os.getenv("AGFAPI_HOME_DIR")
    if agfapi_home:
        home_dir = Path(agfapi_home)
    else:
        home_dir = Path.home() / ".agfapi"

    cache_dir = home_dir / "bin" / "agfapi" / version
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def download_binary(version: str) -> str:
    system, arch, archive_name, binary_name = get_platform_info()
    if version != "latest" and not version.startswith("v"):
        version = "v" + version

    cache_dir = get_binary_cache_dir(version)
    binary_path = cache_dir / binary_name
    if binary_path.exists():
        return str(binary_path)

    if version == "latest":
        gh_url = f"https://github.com/s-hammon/agfapi/releases/latest/download/{archive_name}"
    else:
        gh_url = f"https://github.com/s-hammon/agfapi/releases/download/{version}/{archive_name}"

    try:
        print(f"Downloading agfapi binary ({version}) for {system}/{arch}...")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as tmp_file:
            import ssl
            context = ssl.create_default_context()

            try:
                with urllib.request.urlopen(gh_url, context=context) as response:
                    tmp_file.write(response.read())
            except (ssl.SSLError, urllib.error.URLError) as e:
                if isinstance(e, urllib.error.URLError) and "SSL" not in str(e):
                    raise
                print("SSL certificate verification failed, trying without verification...")
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(gh_url, context=context) as response:
                    tmp_file.write(response.read())

            tmp_file_path = tmp_file.name

        try:
            if archive_name.endswith(".tar.gz"):
                with tarfile.open(tmp_file_path, "r:gz") as tar:
                    for member in tar.getmembers():
                        if member.name == binary_name or member.name.endswith(f"/{binary_name}"):
                            member.name = binary_name
                            tar.extract(member, cache_dir)
                            break
                    else:
                        raise RuntimeError(f"Binary {binary_name} not found in archive.")

            elif archive_name.endswith(".zip"):
                with zipfile.ZipFile(tmp_file_path, "r") as zip_file:
                    for name in zip_file.namelist():
                        if name == binary_name or name.endswith(f"/{binary_name}"):
                            with zip_file.open(name) as source:
                                with open(binary_path, "wb") as tgt:
                                    tgt.write(source.read())
                            break
                    else:
                        raise RuntimeError(f"Binary {binary_name} not found in archive")

        finally:
            os.unlink(tmp_file_path)

        if binary_path.exists():
            binary_path.chmod(binary_path.stat().st_mode | stat.S_IEXEC)
            return str(binary_path)
        else:
            raise RuntimeError("Failed to extract binary from archive")


    except Exception as e:
        warnings.Warn(f"Failed to download agfapi binary: {e}")
        raise RuntimeError(f"Could not download agfapi binary for {system}/{arch}: {e}")

