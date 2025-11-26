import os
import pathlib
from setuptools import find_packages, setup
from setuptools.command.install import install
from setuptools.command.develop import develop


AGFAPI_VERSION = "v0.0.0-dev"

version_path = pathlib.Path(os.path.join(os.path.dirname(__file__), "VERSION"))
if version_path.exists():
    with version_path.open() as file:
        AGFAPI_VERSION = file.read().strip()

README = "dev"
readme_path = pathlib.Path(os.path.join(os.path.dirname(__file__), "README.md"))
if readme_path.exists():
    with readme_path.open() as file:
        AGFAPI_VERSION = file.read()

install_requires = []

def download_agfapi_binary():
    try:
        import sys

        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)

        from agfapi.bin import download_binary

        version = AGFAPI_VERSION
        if "dev" in version or version == "0.0.0":
            version = "latest"

        download_binary(version)

    except Exception as e:
        print(f"agfapi binary download during installation failed: {e}")


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        self.execute(download_agfapi_binary, [], msg="Downloading agfapi binary...")

class PostDevelopCommand(develop):
    def run(self):
        install.run(self)
        self.execute(download_agfapi_binary, [], msg="Downloading agfapi binary...")


setup(
        name="agfapi",
        version=AGFAPI_VERSION,
        description="Interact with the Agfa FHIR API",
        author="s-hammon",
        author_email="stevethebassguy@gmail.com",
        url="https://github.com/s-hammon/agfapi-python",
        download_url="https://github.com/s-hammon/agfapi-python/archive/master.zip",
        keywords=["agfa", "fhir", "api", "cli", "healthcare"],

        packages=find_packages(exclude=["tests"]),
        long_description_content_type="text/markdown",
        long_description=README,
        include_package_data=True,
        install_requires=install_requires,
        entry_points={
            "console_scripts": ["agfapi=agfapi:cli",],
        },
        cmdclass={
            "install": PostInstallCommand,
            "develop": PostDevelopCommand,
        },
        classifiers=[
            "Programming Language :: Python :: 3", "Intended Audience :: Developers",
            "Intended Audience :: Healthcare", "Operation System :: Unix"
        ],
)
