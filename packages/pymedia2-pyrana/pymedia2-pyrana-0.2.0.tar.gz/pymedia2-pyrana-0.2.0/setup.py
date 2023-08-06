from distutils.core import setup


def dependencies():
    try:
        with open('requirements.txt', 'rt') as reqs:
            return reqs.read().splitlines()
    except IOError:
        return []


def description():
    return """
Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg (http://ffmpeg.org)
libraries, but provides an independent API.
"""


setup(name='pymedia2-pyrana',
      version='0.2.0',
      description='Package for simple manipulation of multimedia files',
      long_description=description(),
      platforms = [ 'posix' ],
      license = 'zlib',
      author = 'Francesco Romani',
      author_email = 'fromani@gmail.com',
      url='http://bitbucket.org/mojaves/pyrana',
      packages=[ 'pyrana' ],
      package_data={'pyarana': ['hfiles/*.*']},
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

