from distutils.core import setup

setup(
	name='ormchair',
	version='0.1.1',
	long_description=open('README.md').read(),
	author='Will Ogden',
	url='https://github.com/willogden/ormchair',
	py_modules=['ormchair'],
	packages=['tests',],
	install_requires=['requests>=1.2.0']
)