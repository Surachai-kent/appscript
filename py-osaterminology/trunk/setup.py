try:
	from setuptools import setup, Extension
except ImportError:
	print "Note: couldn't import setuptools so using distutils instead."
	from distutils.core import setup, Extension


setup(
		name = "osaterminology",
		version = "0.11.0",
		description = "Parse and render aete/sdef resources.",
		author = "HAS",
		author_email='',
		url='http://appscript.sourceforge.net',
		license='MIT',
		platforms=['Mac OS X'],
		packages = [
			'osaterminology',
			'osaterminology/defaultterminology',
			'osaterminology/dom',
			'osaterminology/renderers',
			'osaterminology/sax',
		],
		extra_path = "aeosa",
		package_dir = { '': 'lib' }
)
