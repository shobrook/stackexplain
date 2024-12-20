import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

if sys.version_info[:3] < (3, 0, 0):
    print("Requires Python 3 to run.")
    sys.exit(1)

setup(
    name="wut-cli",
    version="1.0.8",
    description="CLI that explains the output of your last command",
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
        "Programming Language :: Python",
    ],
    keywords="openai claude cli commandline error stack-trace explain assistant terminal",
    include_package_data=True,
    packages=find_packages(),
    entry_points={"console_scripts": ["wut = wut.wut:main"]},
    install_requires=["openai", "anthropic", "ollama", "rich", "psutil"],
    requires=["openai", "anthropic", "ollama", "rich", "psutil"],
    python_requires=">=3",
    license="MIT",
)
