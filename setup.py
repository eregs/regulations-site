from setuptools import find_packages, setup


setup(
    name="regulations",
    version="9.0.0-rc",
    packages=find_packages(),
    include_package_data=True,
    python_requires='~=3.6',
    install_requires=[
        'cached-property',
        'django>=3.1,<4',
        'requests',
        'six',
    ],
    extras_require={
        'notice_comment': ['boto3', 'celery', 'requests-toolbelt'],
    },
    classifiers=[
        'License :: Public Domain',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication'
    ]
)
