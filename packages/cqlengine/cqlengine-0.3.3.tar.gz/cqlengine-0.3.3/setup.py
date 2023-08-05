from setuptools import setup, find_packages

#next time:
#python setup.py register
#python setup.py sdist upload

version = '0.3.3'

long_desc = """
cqlengine is a Cassandra CQL Object Mapper for Python in the style of the Django orm and mongoengine

[Documentation](https://cqlengine.readthedocs.org/en/latest/)

[Report a Bug](https://github.com/bdeggleston/cqlengine/issues)

[Users Mailing List](https://groups.google.com/forum/?fromgroups#!forum/cqlengine-users)

[Dev Mailing List](https://groups.google.com/forum/?fromgroups#!forum/cqlengine-dev)
"""

setup(
    name='cqlengine',
    version=version,
    description='Cassandra CQL ORM for Python in the style of the Django orm and mongoengine',
    dependency_links = ['https://github.com/bdeggleston/cqlengine/archive/{0}.tar.gz#egg=cqlengine-{0}'.format(version)],
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
    url='https://github.com/bdeggleston/cqlengine',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
)

