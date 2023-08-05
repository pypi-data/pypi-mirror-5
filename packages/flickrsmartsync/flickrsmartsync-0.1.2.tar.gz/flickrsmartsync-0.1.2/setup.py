#! /usr/bin/env python

from setuptools import setup, find_packages
import sys
import os

version = '0.1.2'

def main():
    setup(name='flickrsmartsync',
          version=version,
          description="Sync/backup your photos to flickr easily",
          long_description=open("README.rst").read(),
          classifiers=[],
          keywords='flickr backup photo sync',
          author='Faisal Raja',
          author_email='support@altlimit.com',
          url='http://www.altlimit.com/',
          license='MIT',
          packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
          include_package_data=True,
          zip_safe=False,
          install_requires=['flickrapi>=1.4.2'],
          entry_points={
              "console_scripts": ['flickrsmartsync = flickrsmartsync:main'],
          },
          )

if __name__ == '__main__':
    main()
