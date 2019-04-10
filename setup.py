# coding: utf-8
import os
from setuptools import setup


VERSION = '2.1.0'
ROOT_DIR = os.path.dirname(__file__)

REQUIREMENTS = [
    line.strip() for line in
    open(os.path.join(ROOT_DIR, 'requirements.txt')).readlines()
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='timber',
    version=VERSION,
    packages=['timber'],
    include_package_data=True,
    license='MIT',
    description='timber.io client API library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/timberio/timber-python',
    download_url='https://github.com/timberio/timber-python/tarball/%s' % (
        VERSION),
    keywords=['api', 'timber', 'logging', 'client'],
    install_requires=REQUIREMENTS,
    author='Timber Technologies, Inc.',
    author_email='help@timber.io',
    classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
