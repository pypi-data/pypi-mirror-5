import sys
import os.path

from setuptools import setup, find_packages

import sqlacodegen


extra_requirements = ()
dependency_links = []
if sys.version_info < (2, 7):
    extra_requirements = ('argparse',)
elif sys.version_info > (3,):
    dependency_links = ['https://github.com/benthor/inflect.py/archive/master.zip#egg=inflect-0.2.4']

here = os.path.dirname(__file__)
readme_path = os.path.join(here, 'README.rst')
readme = open(readme_path).read()

setup(
    name='sqlacodegen',
    description='Automatic model code generator for SQLAlchemy',
    long_description=readme,
    version=sqlacodegen.version,
    author='Alex Gronholm',
    author_email='sqlacodegen@nextday.fi',
    url='http://pypi.python.org/pypi/sqlacodegen/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Topic :: Database',
        'Topic :: Software Development :: Code Generators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3'
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=(
        'SQLAlchemy >= 0.6.0',
        'inflect >= 0.2.0'
    ) + extra_requirements,
    dependency_links=dependency_links,
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'sqlacodegen=sqlacodegen.main:main'
        ]
    }
)
