# installation: easy_install filevault

from setuptools import setup

setup( 
    name = 'filevault',
    version = '0.1.2',
    description = 'filevault: manage a hash directory tree and files',
    keywords = 'file vault filevault hashed hash directory tree directories dir obfuscate hex',
    long_description = open('README.rst').read(),

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://bitbucket.org/russellballestrini/filevault/src',

    platforms = ['All'],
    license = 'Public Domain',

    py_modules = ['filevault'],
    include_package_data = True,
)

# setup keyword args: http://peak.telecommunity.com/DevCenter/setuptools

# built and uploaded to pypi with this:
# python setup.py sdist bdist_egg register upload

