from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='unice.portlet.stories',
      version=version,
      description="A Plone portlet that shows a stories item.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "TODO.txt")).read() +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone portlet',
      author='Universite Nice Sophia Antipolis',
      author_email='pi@unice.fr',
      url='https://github.com/unice/unice.portlet.stories',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['unice', 'unice.portlet'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=['Products.LinguaPlone',]
      ),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
