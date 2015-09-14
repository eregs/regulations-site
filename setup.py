from setuptools import setup, find_packages

setup(
    name="regulations",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        'django==1.8',
        'lxml',
        'requests'
    ],
    classifiers=[
        'License :: Public Domain',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication'
    ]
)
