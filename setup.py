from setuptools import setup, find_packages
import os

version = '2.0dev'

setup(name='plone.app.multilingual',
      version=version,
      description="Multilingual Plone UI package, enables maintenance of translations for both Dexterity types and Archetypes",
      long_description=open("README.rst").read() + "\n\n" +
                       open(os.path.join("docs", "CREDITS.txt")).read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      url='https://github.com/plone/plone.app.multilingual',
      license='GPL',
      author='Ramon Navarro, Victor Fernandez de Alba, awello et al',
      author_email='r.navarro@iskra.cat',
      packages=find_packages('devel'),
      package_dir={'': 'devel'},
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'z3c.relationfield',
        'plone.app.z3cform',
        'plone.app.registry',
        'plone.directives.form',
        'plone.formwidget.contenttree',
        'Products.PloneLanguageTool',
      ],
      extras_require={
          'archetypes': ['archetypes.multilingual'],
          'test': [
              'plone.app.testing[robot]>=4.2.2',
              'archetypes.multilingual',
              'decorator',  # BBB
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
 )
