from setuptools import setup, find_packages

#next time:
#python setup.py register
#python setup.py sdist upload

version = '0.4.3'

long_desc = """
Cassandra CQL 3 Object Mapper for Python

[Documentation](https://cqlengine.readthedocs.org/en/latest/)

[Report a Bug](https://github.com/bdeggleston/cqlengine/issues)

[Users Mailing List](https://groups.google.com/forum/?fromgroups#!forum/cqlengine-users)

[Dev Mailing List](https://groups.google.com/forum/?fromgroups#!forum/cqlengine-dev)
"""

setup(
    name='cqlengine',
    version=version,
    description='Cassandra CQL 3 Object Mapper for Python',
    long_description=long_desc,
    classifiers = [
        "Environment :: Web Environment",
        "Environment :: Plugins",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='cassandra,cql,orm',
    install_requires = ['cql'],
    author='Blake Eggleston',
    author_email='bdeggleston@gmail.com',
    url='https://github.com/cqlengine/cqlengine',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
)

