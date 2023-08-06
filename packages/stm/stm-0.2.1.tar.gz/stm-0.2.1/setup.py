from setuptools import setup
from subprocess import Popen, PIPE
from time import gmtime, strftime

setup(
    name="stm",
    version="0.2.1",
    description="A software transactional memory library",
    author="Alexander Boyd",
    author_email="alex@opengroove.org",
    packages=["stm"],
    install_requires=["ttftree"]
)
