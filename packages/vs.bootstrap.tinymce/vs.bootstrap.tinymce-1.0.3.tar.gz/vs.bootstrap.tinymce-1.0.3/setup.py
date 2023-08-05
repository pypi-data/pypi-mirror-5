from setuptools import setup, find_packages
import os

version = '1.0.3'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='vs.bootstrap.tinymce',
      version=version,
      description="Bootstrap css classes for TinyMCE",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone tinymce bootstrap',
      author='Veit Schiele',
      author_email='kontakt@veit-schiele.de',
      url='https://github.com/veit/vs.bootstrap.tinymce',
      license='GPL version 2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['vs', 'vs.bootstrap'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
  	  [z3c.autoinclude.plugin]
  	  target = plone
      """,
      )
