from setuptools import find_packages, setup


setup(
    name="regulations",
    version="7.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'boto3',
        'cached-property',
        'celery',
        'django>=1.8,<1.10',
        'enum34',
        'futures',
        'requests',
        'six',
        'requests-toolbelt',
    ],
    classifiers=[
        'License :: Public Domain',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication'
    ]
)
