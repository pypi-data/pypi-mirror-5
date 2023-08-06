#!/usr/bin/env python
# coding=utf8

from setuptools import setup, find_packages

required_modules = [
	'argparse',
	'audiogen',
	'bitarray',
	]
extras_require = {
	'soundcard_output': ['PyAudio'],
}

with open("README.rst", "rb") as f:
	readme = f.read()

setup(
	name="afsk",
	version="0.0.1",
	description="AFSK – Bell 202 Audio Frequency Shift Keying encoder",
	author="Christopher H. Casebeer",
	author_email="",
	url="https://github.com/casebeer/afsk",

	packages=find_packages(exclude='tests'),
	install_requires=required_modules,
	extras_require=extras_require,

	tests_require=["nose", "crc16"],
	test_suite="nose.collector",

	entry_points={
		"console_scripts": [
			"aprs = afsk.ax25:main"
		]
	},

	long_description=readme,
	classifiers=[
		"Environment :: Console",
		"License :: OSI Approved :: BSD License",
		"Intended Audience :: Developers",
		"Topic :: Multimedia :: Sound/Audio",
		"Topic :: Communications :: Ham Radio",
	]
)

