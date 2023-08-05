"""
Attest
======

Attest is a unit testing framework built from the ground up with idiomatic
Python in mind. Unlike others, it is not built on top of unittest though it
provides compatibility by creating TestSuites from Attest collections.

It has a functional API inspired by `Flask`_ and a class-based API that
mimics Python itself. The core avoids complicated assumptions leaving you
free to write tests however you prefer.

.. _Flask: http://pypi.python.org/pypi/Flask/

::

    from attest import Tests
    math = Tests()

    @math.test
    def arithmetics():
        assert 1 + 1 == 2

    if __name__ == '__main__':
        math.run()

"""

from setuptools import setup, find_packages


setup(
    name='Attest-latest',
    version='0.6.1',
    description='Modern, Pythonic unit testing.',
    long_description=__doc__,

    author='Dag Odenhall',
    author_email='dag.odenhall@gmail.com',
    license='Simplified BSD',
    url='https://github.com/dag/attest',

    packages=find_packages(),

    install_requires=[
        'progressbar-latest>=2.4',
        'Pygments',
        'six',
    ],

    entry_points={
        'attest.reporters': [
            'xml = attest:XmlReporter',
            'xunit = attest:XUnitReporter',
            'quickfix = attest:QuickFixReporter',
            'plain = attest:PlainReporter',
            'fancy = attest:FancyReporter',
            'auto = attest:auto_reporter',
        ],
        'pygments.styles': [
            'attest = attest.pygments:Attest',
        ],
        'console_scripts': [
            'attest = attest.run:main',
        ],
    },

    test_loader='attest:auto_reporter.test_loader',
    test_suite='attest.tests',
    use_2to3=True,
    zip_safe=False,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development :: Testing',
    ],
)
