import platform
from setuptools import setup

requirements = ['python-daemon', 'pyyaml']
tests_require = ['mock']
(major, minor, rev) = platform.python_version_tuple()
if float('%s.%s' % (major, minor)) < 2.7:
    requirements.append('argparse')
    requirements.append('logutils')
    tests_require.append('unittest2')

console_scripts = ['clihelper-init=clihelper.initialize:main']

setup(name='clihelper',
      version='1.7.3',
      description='Internal Command-Line Application Wrapper',
      long_description=('clihelper is a wrapper for command-line daemons '
                        'providing a core Controller class and methods for '
                        'starting the application and setting configuration.'),
      author='Gavin M. Roy',
      author_email='gmr@meetme.com',
      url='https://clihelper.readthedocs.org',
      packages=['clihelper'],
      install_requires=requirements,
      tests_require=tests_require,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: BSD License'],
      entry_points={'console_scripts': console_scripts},
      zip_safe=True)
