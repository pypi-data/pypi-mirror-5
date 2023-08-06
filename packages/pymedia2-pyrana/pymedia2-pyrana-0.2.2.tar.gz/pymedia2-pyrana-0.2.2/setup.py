import os.path
from distutils.core import setup


def dependencies():
    try:
        with open('requirements.txt', 'rt') as reqs:
            return reqs.read().splitlines()
    except IOError:
        return []


def description():
    try:
        with open(os.path.join('docs', 'pyrana-intro.rst'), 'rt') as desc:
            return desc.read()
    except IOError:
        return """
Pyrana is a pure-python package which provides easy, pythonic and
powerful handling of multimedia files, using the FFmpeg libraries
under the hood.
"""

setup(name='pymedia2-pyrana',
      version='0.2.2',
      description='Package for simple manipulation of multimedia files',
      long_description=description(),
      platforms = [ 'posix' ],
      license = 'zlib',
      author = 'Francesco Romani',
      author_email = 'fromani@gmail.com',
      url='http://bitbucket.org/mojaves/pyrana',
      download_url='http://bitbucket.org/mojaves/pyrana',
      packages=[ 'pyrana' ],
      package_data={'pyrana': ['hfiles/*.*']},
      install_requires=dependencies(),
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: zlib/libpng License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.3',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Graphics :: Capture',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Capture',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])

