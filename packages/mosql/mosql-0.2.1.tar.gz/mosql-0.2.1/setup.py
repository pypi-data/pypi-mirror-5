from distutils.core import setup

from mosql import __version__

setup(
    name    = 'mosql',
    description = 'MoSQL is a lightweight Python library which assists programmer to use SQL.',
    long_description = open('README.rst').read(),
    version = __version__,
    author  = 'Mosky',
    author_email = 'mosky.tw@gmail.com',
    url = 'http://mosql.mosky.tw/',
    packages = ['mosql'],
    license = 'MIT',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

