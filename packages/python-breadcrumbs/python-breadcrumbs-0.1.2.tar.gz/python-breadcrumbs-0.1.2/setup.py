"""Setup configuration.
"""

import setuptools


setuptools.setup(
    name="python-breadcrumbs",
    version="0.1.2",
    author="Pierre Jaury",
    author_email="pierre@jaury.eu",
    description="Store breadcrumbs for later accessing an object internals",
    long_description=open('README.txt').read(),
    license="GPLv3",
    url="https://github.com/kaiyou/python-breadcrumbs",
    py_modules=["breadcrumbs"],
    test_suite="tests"
)
