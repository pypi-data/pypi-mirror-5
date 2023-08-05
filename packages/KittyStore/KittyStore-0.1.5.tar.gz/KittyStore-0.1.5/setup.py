#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

def filetolist(filepath):
    """Turns a text file into a list (one element per line)"""
    result = []
    with open(filepath, "r") as f:
        for line in f:
            if "#" in line:
                line = line[:line.index("#")]
            line = line.strip()
            if not line:
                continue
            result.append(line)
    return result


setup(
    name="KittyStore",
    version="0.1.5",
    description="A storage engine for GNU Mailman v3 archives",
    long_description=open('README.rst').read(),
    author='HyperKitty Developers',
    author_email='hyperkitty-devel@lists.fedorahosted.org',
    url="https://fedorahosted.org/hyperkitty/",
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Communications :: Email :: Mailing List Servers",
        "Programming Language :: Python :: 2",
        ],
    keywords='email',
    #packages=find_packages(exclude=["*.test", "test", "*.test.*"]),
    packages=find_packages(),
    include_package_data=True,
    install_requires=filetolist("requirements.txt"),
    test_suite = "kittystore.test",
    entry_points={
        'console_scripts': [
            'kittystore-import = kittystore.import:main',
            'kittystore-updatedb = kittystore.scripts:updatedb',
            'kittystore-download21 = kittystore.scripts:dl_archives',
            ],
        },
    )
