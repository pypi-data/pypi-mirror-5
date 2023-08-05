from distutils.core import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='ledgertools',
    version='0.3',
    description='Ledger accounting system utilities',
    author='Fraser Tweedale',
    author_email='frase@frase.id.au',
    url='https://github.com/frasertweedale/ledgertools',
    packages=['ltlib', 'ltlib.readers'],
    scripts=['bin/lt-stmtproc', 'bin/lt-transact', 'bin/lt-chart'],
    data_files=[
        ('doc/ledgertools', ['doc/.ltconfig.sample']),
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial :: Accounting',
    ],
    long_description=long_description,
)
