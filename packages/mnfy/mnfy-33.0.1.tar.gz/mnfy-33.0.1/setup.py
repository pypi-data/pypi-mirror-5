from distutils.core import setup
import sys

with open('docs/index.rst') as file:
    index_text = file.read()

long_description = index_text.partition('.. END README')[0]
long_description += index_text.rpartition('.. LINKS')[2]

version = '33.0.1'
assert version.startswith('{}{}'.format(*sys.version_info))

setup(
    name='mnfy',
    # First digit is the Massive/feature version of Python, rest are
    # feature/bugfix for mnfy.
    version=version,
    author='Brett Cannon',
    author_email='brett@python.org',
    url='http://mnfy.rtfd.org/',
    py_modules=['mnfy'],  # Don't install test code since not in a package
    license='Apache Licence 2.0',
    description='Minify/obfuscate Python 3 source code',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.3',
    ],
)
