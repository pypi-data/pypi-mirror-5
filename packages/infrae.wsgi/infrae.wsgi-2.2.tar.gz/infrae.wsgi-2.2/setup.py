# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '2.2'

tests_require = [
    'infrae.testing',
    'zope.site',
    ]
intercept_require = [
    'wsgi_intercept',
    'zope.testbrowser',
    ]

setup(name='infrae.wsgi',
      version=version,
      description="WSGI support for Zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          ],
      keywords='zope2 wsgi silva infrae',
      author='Sylvain Viollon',
      author_email='info@infrae.com',
      url='http://svn.infrae.com/infrae.wsgi/trunk',
      license='ZPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['infrae'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Zope2 >= 2.12.4',
        'five.grok',
        'setuptools',
        'zope.cachedescriptors',
        'zope.component',
        'zope.event',
        'zope.interface',
        'zope.processlifetime',
        'zope.publisher',
        'zope.security',
        ],
      entry_points={
        'paste.app_factory': [
            'zope2 = infrae.wsgi.paster:zope2_application_factory',
            ],
        'paste.filter_app_factory': [
            'threads = infrae.wsgi.debugging:make_middleware',
            ],
        },
      tests_require = tests_require + intercept_require,
      extras_require = {'test': tests_require, 'intercept': intercept_require},
      )
