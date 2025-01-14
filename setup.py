from setuptools import setup, find_packages


def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f
                if line.strip() and not line.startswith('#')]


setup(
    name="ipv6_ddns",
    version="0.1.1",
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
)
