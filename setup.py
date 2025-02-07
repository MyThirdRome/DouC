from setuptools import setup, find_packages

setup(
    name='dou-blockchain',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'cryptography',
        'pytest',
        'mypy'
    ],
)
