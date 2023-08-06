from setuptools import setup

setup(name='bart_api',
    version='0.1-1',
    description='a python client that interacts with the bay area rapid transit api',
    url='http://github.com/projectdelphai/bart_api',
    author='Reuben Castelino',
    author_email='projetdelphai@gmail.com',
    license='MIT',
    packages=['bart_api', 'bart_api.test'],
    long_description=open('README.md').read())
