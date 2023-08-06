# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '1.4.0'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='wasgehtengine.import',
      version=version,
      description="Import content into wasgehtengine",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Fabian Köster',
      author_email='koesterreich@fastmail.fm',
      url='https://gitorious.org/wasgehtengine',
      license='agpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['wasgehtengine', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'wasgehtengine.contenttypes',
          'collective.transmogrifier',
          'transmogrify.dexterity',
          'transmogrify.xmlsource',
          'transmogrify.pathsorter',
          'plone.app.transmogrifier',
          'html5lib',
          'requests',
          'chardet',
          # -*- Extra requirements: -*-
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["templer.localcommands"],
      )
