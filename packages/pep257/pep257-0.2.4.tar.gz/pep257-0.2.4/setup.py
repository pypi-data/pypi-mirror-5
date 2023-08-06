"""`pep257` lives on `GitHub <http://github.com/GreenSteam/pep257/>`_."""
from distutils.core import setup

def get_version():
    with open('pep257.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


setup(name='pep257',
      version=get_version(),
      description="Python docstring style checker",
      long_description=__doc__,
      license='MIT',
      author='Vladimir Keleshev, GreenSteam A/S',
      url='https://github.com/GreenSteam/pep257/',
      classifiers=['Intended Audience :: Developers',
                   'Environment :: Console',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Operating System :: OS Independent',
                   'License :: OSI Approved :: MIT License'],
      keywords='PEP 257, pep257, PEP 8, pep8, docstrings',
      py_modules=['pep257'],
      scripts=['pep257'],
      tests_require=['mock==0.8'])
