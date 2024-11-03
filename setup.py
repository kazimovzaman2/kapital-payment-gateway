from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="kapital",
    version="0.2.2",
    description="A simple client for the Kapital payment gateway.",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zaman Kazimov",
    author_email="kazimovzaman2@gmail.com",
    maintainer="Fuad Huseynov",
    maintainer_email="fuadhuseynov@gmail.com",
)
