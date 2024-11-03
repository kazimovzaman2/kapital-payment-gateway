from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

with open("VERSION", "r") as f:
    version = f.read().strip()

setup(
    name="kapital",
    version=version,
    description="A simple client for the Kapital payment gateway.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zaman Kazimov",
    author_email="kazimovzaman2@gmail.com",
    maintainer="Fuad Huseynov",
    maintainer_email="fuadhuseynov@gmail.com",
    url="https://github.com/kazimovzaman2/kapital-python",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
)
