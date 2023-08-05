#! /usr/bin/env python

import os
from setuptools import setup
import invewrapper

setup(
	name='invewrapper',
	version='0.1.2',
	description='tools to manage multiple virtualenv written in pure python',
	keywords=[],
	author='Dario Bertini',
	author_email='berdario+pypi@gmail.com',
	url='https://github.com/berdario/invewrapper',
	license='MIT License',
    packages=['invewrapper'],
	#py_modules=['invewrapper'],
	install_requires=['virtualenv'],
	package_data={'': ['inve']},
	#data_files=[('duh', ['inve'])],  # XXX
	entry_points={
		'console_scripts':
			["{0} = invewrapper.invewrapper:{0}_cmd".format(cmd[:-4])
			for cmd in dir(invewrapper.invewrapper) if cmd.endswith("_cmd")]}
)
