#!/usr/bin/env python

from setuptools import setup
from subprocess import call

def convert_readme():
    try:
        call(["pandoc", "-f", "markdown_github", "-t",  "rst", "-o",  "README.txt", "readme.md"])
    except OSError:
        pass
    return open('README.txt').read()

setup(name='mongoadmin',
    version='0.2',
    description="A replacement for django's admin that works with mongodb.",
    author='Jan Schrewe',
    author_email='jan@schafproductions.com',
    url='http://www.schafproductions.com/projects/mongo-admin/',
    packages=['mongoadmin', 'mongoadmin.templatetags', 'mongoadmin.contenttypes',],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    license='New BSD License',
    long_description=convert_readme(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools', 'django>=1.3', 'mongoengine>=0.6', 'mongodbforms',],
)