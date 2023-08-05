#This file is part of Tryton & Nereid. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from setuptools import setup

setup(
    name='Nereid',
    version='2.8.0.2',
    url='http://nereid.openlabs.co.in/docs/',
    license='GPLv3',
    author='Openlabs Technologies & Consulting (P) Limited',
    author_email='info@openlabs.co.in',
    description='Tryton - Web Framework',
    long_description=__doc__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Tryton',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'distribute',
        'flask',
        'wtforms',
        'wtforms-recaptcha',
        'babel',
        'speaklater',
        'Flask-Babel',
    ],
    packages=[
        'nereid',
        'nereid.contrib',
        'nereid.tests',
    ],
    package_dir={
        'nereid': 'nereid',
        'nereid.contrib': 'nereid/contrib',
        'nereid.tests': 'tests',
    },
    zip_safe=False,
    platforms='any',
)
