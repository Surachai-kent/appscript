try:
	from setuptools import setup, Extension
except ImportError:
	print("Note: couldn't import setuptools so using distutils instead.")
	from distutils.core import setup, Extension


setup(
		name = "py3-appscript",
		version = "0.19.0",
		description = "Modules for controlling scriptable Mac OS X applications and scripting additions from Python 3.0+.",
		author = "HAS",
		author_email='',
		url='http://appscript.sourceforge.net',
		license='MIT',
		platforms=['Mac OS X'],
		ext_modules = [
			Extension('aem.ae',
				sources=['ext/ae.c'],
				extra_compile_args=['-DMAC_OS_X_VERSION_MIN_REQUIRED=MAC_OS_X_VERSION_10_3'],
				extra_link_args=[
						'-framework', 'CoreFoundation', 
						'-framework', 'ApplicationServices',
						'-framework', 'Carbon'],
			),
		],
		packages = [
			'aem',
			'appscript',
		],
		py_modules=[
			'mactypes',
			'osax',
		],
		extra_path = "aeosa",
		package_dir = { '': 'lib' }
)
