"""
Flask Multiconfig
-----------------

A simple extension that adds new possible configuration formats
along with native support for application modes pulled from
setting environment variables.

Currently adds support for YAML and setting an environment variable
for application modes.

"""

from setuptools import setup, find_packages

setup(
	name='flask-multiconfig',
	version='0.1',
	url='http://github.com/petermelias/flask-multiconfig',
	license='BSD',
	author='Peter M. Elias',
	author_email='petermelias@gmail.com',
	description='A simple extension to add advanced configuration source support.',
	long_description=__doc__,
	py_modules=['flask_multiconfig'],
	zip_safe=False,
	include_package_data=True,
	platforms='any',
	install_requires=[
		'Flask',
		'pyyaml'
	],
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