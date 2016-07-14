# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='theBrain',
    version='0.2',
    description='the IoT brain of techlab',
    long_description=readme,
    author='Paolo Cavagnolo',
    author_email='paolo.cavagnolo@gmail.com',
    url='https://github.com/paolocavagnolo/tagNFC_DB_server/tree/master/v0.2',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
