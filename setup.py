import sys
from setuptools import setup, find_packages

if sys.version_info[:3] < (3, 0, 0):
    print("Requires Python 3 to run.")
    sys.exit(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wut-cli",
    version="1.0.5",
    description="CLI that explains the output of your last command",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shobrook/wut",
    author="shobrook",
    author_email="shobrookj@gmail.com",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Debuggers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python"
    ],
    keywords="openai claude gemini cli commandline error stack-trace explain assistant terminal",
    include_package_data=True,
    packages=find_packages(),
    entry_points={"console_scripts": ["wut = wut.wut:main"]},
    install_requires=[
        "openai",
        "anthropic",
        "ollama",
        "rich",
        "psutil",
        "google-genai",
    ],
    python_requires=">=3.6",
    license="MIT",
    project_urls={
        "Bug Tracker": "https://github.com/shobrook/wut/issues",
        "Documentation": "https://github.com/shobrook/wut#readme",
        "Source Code": "https://github.com/shobrook/wut",
    },
)
