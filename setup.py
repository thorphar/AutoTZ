import re
import os
from setuptools import setup, find_packages

# Read the version dynamically from src/__init__.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "src", "__init__.py")
    with open(version_file, "r") as f:
        match = re.search(r'__version__ = "(.*?)"', f.read())
        if match:
            return match.group(1)
        raise RuntimeError("Version not found in src/__init__.py")

setup(
    name="autotz",
    version=get_version(),  # Dynamically set version
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "autotz=main:main"
        ]
    },
    author="Harry Thorpe",
    author_email="info@harrythorpe.co.uk",
    description="A simple tool to update the system timezone based on IP geolocation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/thorphar/autotz",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
)
