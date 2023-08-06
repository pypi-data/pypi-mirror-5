# coding: utf-8

#===============================================================================
# Sometimes things go wrong, and the setup script doesn’t do what the developer wants.
# Distutils catches any exceptions when running the setup script, and print a simple error message
# before the script is terminated.
# 
# The DISTUTILS_DEBUG environment variable can be set to anything except an empty string,
# and distutils will now print detailed information what it is doing, and prints the full traceback
# in case an exception occurs.
# 
# from http://docs.python.org/distutils/setupscript.html
#
# ALSO:
# see "The Hitchhiker’s Guide to Packaging"
# http://guide.python-distribute.org/
#===============================================================================

from distutils.core import setup #, Extension


version = __import__('ars').get_version()

setup(
	name='ARS',
	version=version,
	# It is recommended that versions take the form major.minor[.patch[.sub]].
	description=(
		'Autonomous Robot Simulator (ARS), a physically-accurate '
		'open-source simulation suite for research and development '
		'of mobile manipulators'),
	long_description=open('README.rst').read(),
	author='German Larrain',
	author_email='glarrain@example.com',
	url='http://bitbucket.org/glarrain/ars',
	#download_url='',
	#platforms='any',
	license='BSD',
	keywords = "simulator robotics physics open-dynamics-engine vtk",

	requires=[
		'numpy',
		'six',
	],  # requires=['ode', 'vtk', 'numpy'],
	#package_dir={}, 
	packages=[
		'ars',
		'ars.app', 'ars.graphics', 'ars.lib', 'ars.model',
		'ars.utils',
		'ars.lib.pydispatch',
		'ars.model.collision', 'ars.model.contrib', 'ars.model.geometry',
		'ars.model.physics', 'ars.model.robot', 'ars.model.simulator',],
	#py_modules=[''],
	#ext_modules=[]
	#libraries=[]
	#scripts=[],
	#package_data={},
	#data_files=[],

	classifiers=[
		'Development Status :: 3 - Alpha',

		#'Environment :: Console', # add when visualization can be disabled
		#'Environment :: MacOS X',
		#'Environment :: Win32 (MS Windows)'
		'Environment :: X11 Applications',

		'Intended Audience :: Science/Research',
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: End Users/Desktop',

		# the FSF refers to it as "Modified BSD License". Other names include
		# "New BSD", "revised BSD", "BSD-3", or "3-clause BSD"
		'License :: OSI Approved :: BSD License',

		#'Operating System :: MacOS :: MacOS X',
		#'Operating System :: Microsoft :: Windows',
		# TODO: what about the OS requirements of VTK and ODE?
		'Operating System :: OS Independent',
		#'Operating System :: POSIX :: Linux',

		'Programming Language :: Python',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',

		# no Robotics topic; Simulation is under Games/Entertainment
		'Topic :: Other/Nonlisted Topic',
		'Topic :: Scientific/Engineering :: Physics',
		'Topic :: Scientific/Engineering :: Visualization',
	],
)
