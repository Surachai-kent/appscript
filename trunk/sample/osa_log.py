#!/usr/local/bin/python

from aemreceive.sfba import *


def f(val):
	print 'LOG', `val`

installeventhandler(f, 'ascrcmnt', ('----', 'val', kAE.typeWildCard))


from Carbon.Cm import OpenDefaultComponent
from osascript.osa import OSAComponentInstance
from aem.kae import *
from aem.ae import *
from aem import Codecs, Application

codecs = Codecs()

osac = OSAComponentInstance(OpenDefaultComponent('osa ', 'ascr'))

scriptDesc = codecs.pack('''
--continue foo()
log 42
99
''')


fn = osac.OSAGetSendProc()

def c(ae, m, p, t):
	print
	print 'EVT', `ae.type, ae.data[:64] + (ae.data[64:] and '...' or '')`
	
	try:
		r=fn(ae, m, p, t)
	except Exception, e:
		print 'ERROR', e
		r = Application().event('aevtansr', {'errn':e[0]}).AEM_event
	print 'RES', `r.type, r.data[:64] + (r.data[64:] and '...' or '')`
	print
	
	return r


osac.OSASetSendProc(c)



def m():
	return `codecs.unpack(osac.OSADoScript(scriptDesc, 0, typeChar, 0))`

installeventhandler(m, 'abcdefgh')




starteventloop()
