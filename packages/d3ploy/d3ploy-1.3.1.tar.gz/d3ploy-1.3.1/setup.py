from distutils.core import setup
from setuptools import find_packages

setup(
    name                    =   'd3ploy',
    version                 =   '1.3.1',
    description             =   'Script for uploading files to S3 with multiple environment support.',
    long_description        =   'See http://dryan.github.io/d3ploy for more information.',
    author                  =   'Daniel Ryan',
    author_email            =   'dryan@dryan.com',
    url                     =   'http://dryan.github.io/d3ploy',
    license                 =   'BSD 3 Clause License',
    packages                =   find_packages(exclude=["d","3","p","l","o","y"]),
    zip_safe                =   True,
    include_package_data    =   True,
    install_requires        =   "boto",
    entry_points            =   """[console_scripts]
d3ploy = d3ploy.d3ploy:main
"""
)
