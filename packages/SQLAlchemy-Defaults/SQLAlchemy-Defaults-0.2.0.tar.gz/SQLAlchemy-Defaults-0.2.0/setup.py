"""
sqlalchemy-defaults
-------------------

Smart SQLAlchemy defaults for lazy guys, like me.
"""

from setuptools import setup, Command
import subprocess


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['py.test'])
        raise SystemExit(errno)

setup(
    name='SQLAlchemy-Defaults',
    version='0.2.0',
    url='https://github.com/kvesteri/sqlalchemy-defaults',
    license='BSD',
    author='Konsta Vesterinen',
    author_email='konsta@fastmonkeys.com',
    description=(
        'Smart SQLAlchemy defaults for lazy guys, like me.'
    ),
    long_description=__doc__,
    packages=['sqlalchemy_defaults'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'psycopg2>=2.4.6',
        'SQLAlchemy>=0.7.8',
    ],
    cmdclass={'test': PyTest},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
