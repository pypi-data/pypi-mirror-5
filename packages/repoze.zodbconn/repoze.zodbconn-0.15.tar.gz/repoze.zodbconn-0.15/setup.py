##############################################################################
#
# Copyright (c) 2008-2010 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__ = '0.15'

import os

from setuptools import setup, find_packages

requires = [
    'setuptools',
    'transaction',
    'persistent',
    'ZConfig',
    'ZODB',
    'ZEO',
]

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='repoze.zodbconn',
      version=__version__,
      description=('Opens ZODB by URI and provides ZODB-related WSGI apps'),
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        ],
      keywords='wsgi zope zodb database',
      author="Chris McDonough, Agendaless Consulting / Shane Hathaway",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze'],
      zip_safe=False,
      tests_require =  requires,
      install_requires = requires,
      test_suite="repoze.zodbconn",
      entry_points = """\
      [paste.filter_app_factory]
      closer = repoze.zodbconn.middleware:make_middleware
      connector = repoze.zodbconn.connector:make_app
      cachecleanup = repoze.zodbconn.cachecleanup:make_app
      transferlog = repoze.zodbconn.transferlog:make_app
      """
     )
