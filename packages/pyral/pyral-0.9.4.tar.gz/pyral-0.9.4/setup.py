#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from distutils2.core import setup
except:
    try:
        from distutils.core import setup
    except:
        from setuptools import setup

PACKAGE       = 'pyral'
VERSION       = '0.9.4'
OFFICIAL_NAME = 'Python toolkit for Rally REST API'
PKG_URL_NAME  = 'python-toolkit-rally-rest-api'
AUTHOR        = 'Kip Lehman (Rally Software Development)'
AUTHOR_EMAIL  = 'klehman@rallydev.com'
RALLY_DEVELOPER_SITE = 'http://developer.rallydev.com'
RALLY_DEVELOPER_DOWNLOAD_FILES = '%s/sites/default/files/multimedia' % RALLY_DEVELOPER_SITE
DOWNLOADABLE_ZIP = '%s/%s-%s.zip' % (RALLY_DEVELOPER_DOWNLOAD_FILES, PACKAGE, VERSION)

MINIMUM_REQUESTS_VERSION = '0.9.3'

setup(name=PACKAGE,
      version=VERSION,
      description=OFFICIAL_NAME,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url='%s/help/%s' % (RALLY_DEVELOPER_SITE, PKG_URL_NAME),
      download_url=DOWNLOADABLE_ZIP,
      long_description=open('README.rst').read(),
      packages=[PACKAGE],
      license='BSD',
      requires=["python (< 3.0)"],
      #install_requires=['requests>=%s' % MINIMUM_REQUESTS_VERSION],
      classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Libraries',
        ],
      #documentation='http://readthedocs.org/docs/pyral'
    )
        
