from setuptools import setup, find_packages

setup(
    name='dou-blockchain',
    version='0.1.0',
    packages=find_packages(where='.', include=['src', 'src.*']),
    package_dir={'': '.'},
    description='Decentralized Messaging and Reward Blockchain System',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/dou-blockchain',
    install_requires=[
        'cryptography',
        'pytest',
        'mypy'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
