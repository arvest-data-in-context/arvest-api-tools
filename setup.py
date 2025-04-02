from setuptools import setup
from setuptools import find_packages

long_description= """
# avest-api-tools
"""

required = []

setup(
    name="arvesttools",
    version="0.0.1",
    description="",
    long_description=long_description,
    author="Jacob Hart",
    author_email="jacob.dchart@gmail.com",
    url="https://github.com/stage-to-data/arvest-api-tools",
    install_requires=required,
    packages=find_packages()
)