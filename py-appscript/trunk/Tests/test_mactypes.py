#!/usr/local/bin/python

import unittest, os, os.path, MacOS
import mactypes

class TC_MacTypes(unittest.TestCase):

	dir = '/private/tmp'
	
	def setUp(self):
		self.path1 = os.tempnam(self.dir, 'py-mactypes-test.') # tempnam raises a security warning re. security; ignore it
		file(self.path1, 'w').close()
		fname = os.path.split(self.path1)[1]
		self.path2 = os.path.join(self.dir, 'moved-' + fname)
		# print "path: %r" % self.path1 # e.g. /private/tmp/py-mactypes-test.VLrUW7
	
	def test_alias(self):
		# make alias
		self.f = mactypes.Alias(self.path1)
		
		self.assertEqual("mactypes.Alias(u%r)" % self.path1,  repr(self.f))
		
		#print "alias path 1: %s" % f.path # e.g. /private/tmp/py-mactypes-test.VLrUW7
		self.assertEqual(self.path1, self.f.path)
		
		# get desc
		#print `f.desc.type, f.desc.data` # alis, [binary data]
		self.assertEqual('alis', self.f.aedesc.type)

		
		# check alias keeps track of moved file
		os.rename(self.path1, self.path2)
		# print "alias path 2: %r" % f.path # /private/tmp/moved-py-mactypes-test.VLrUW7
		self.assertEqual(self.path2, self.f.path)

		self.assertEqual("mactypes.Alias(u%r)" % self.path2, repr(self.f))
		
		# check a FileNotFoundError is raised if getting path/FileURL for a filesystem object that no longer exists
		os.remove(self.path2)
		self.assertRaises(MacOS.Error, lambda:self.f.path) # File not found.
		self.assertRaises(MacOS.Error, lambda:self.f.file) # File not found.


	def test_fileURL(self):

		g = mactypes.File('/non/existent path')

		self.assertEqual('/non/existent path', g.path)
		
		self.assertEqual('furl', g.aedesc.type)
		self.assertEqual('file://localhost/non/existent%20path', g.aedesc.data)

		self.assertEqual("mactypes.File(u'/non/existent path')", repr(g.file))

		# check a not-found error is raised if getting Alias for a filesystem object that doesn't exist
		self.assertRaises(MacOS.Error, lambda:g.fsalias) # File "/non/existent path" not found.


if __name__ == '__main__':
	unittest.main()
	