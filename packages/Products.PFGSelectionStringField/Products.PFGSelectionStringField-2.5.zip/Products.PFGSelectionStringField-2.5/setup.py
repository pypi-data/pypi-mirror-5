from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
    read('src', 'Products', 'PFGSelectionStringField', 'docs', 'README.rst') + "\n" +
    read('src', 'Products', 'PFGSelectionStringField', 'docs', 'HISTORY.rst') + "\n" +
    read('src', 'Products', 'PFGSelectionStringField', 'docs', 'CREDITS.rst'))


setup(
    name='Products.PFGSelectionStringField',
    version='2.5',
    description="Adds selection field type with string field to Products.PloneFormGen.",
    long_description=long_description,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"],
    keywords='',
    author='Taito Horiuchi',
    author_email='taito.horiuchi@gmail.com',
    url='https://github.com/collective/Products.PFGSelectionStringField',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.PloneFormGen',
        'setuptools'],
    extras_require={'test': ['hexagonit.testing']},
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """)
