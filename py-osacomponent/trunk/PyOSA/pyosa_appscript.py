
#
# pyosa_appscript.py
# PyOSA
#
# Copyright (C) 2007 HAS
#
#
# Defines AppscriptServices class, whch is responsible for installing PyOSA customisations
# into standard aem/appscript modules, packing and unpacking AEDescs passed to and from
# osafunctions.c
#

from sys import stderr # debug

from CarbonX.kOSA import *
import aem
import appscript, appscript.reference, appscript.terminology

from pyosa_hostcallbacks import *

__all__ = ['aem', 'appscript', 'AppscriptServices']


# TO DO: need to replace following method in appscript.reference.AppData:
#
# 	def pack(self, data):
#		if isinstance(data, GenericReference):
#			data = data.AS_resolve(Reference, self)
#		if isinstance(data, Reference):
#			data = data.AS_aemreference
#		elif isinstance(data, Keyword):
#			try:
#				data = self.typebyname[data.AS_name]
#			except KeyError:
#				raise KeyError, "Unknown Keyword: k.%s" % data.AS_name
#		return aem.Codecs.pack(self, data)
#
# New method will need following enhancements:
#
# - when packing references, need a way to optionally pack references as fully qualified:
#		data = aem.qualifyreference(data.AS_aemreference, data.AS_appdata.target)
#
# - when packing references, make sure the reference's own appdata is used (maybe add AS_packself() method to appscript.reference.Reference?):
#		data = data.AS_appdata.pack(data)


# TO DO: appscriptservices.pack needs following enhancements:
#
# - need to deal with generic references belonging to external apps somehow (some may resolve against host app ok, but most will fail, so need an intelligent error message when that happens)
#
# - keywords will need some special handling since they're also generic: those found in host dictionary will translate to AEDescs okay, but  those defined in other apps' dictionaries may cause 'unknown keyword' errors. Note: without robust handling of keywords, Script Editor, etc. may not display results correctly.

#######


class AppscriptServices:
	
	_kEventAttributes = [
			keyTransactionIDAttr,
			keyReturnIDAttr,
			keyEventClassAttr,
			keyEventIDAttr,
			keyAddressAttr,
			keyOptionalKeywordAttr,
			keyTimeoutAttr,
			keyInteractLevelAttr,
			keyEventSourceAttr,
			keyOriginalAddressAttr,
			keyAcceptTimeoutAttr,
			keyReplyRequestedAttr,
			keySubjectAttr,
			enumConsiderations, # deprecated (superceded by enumConsidsAndIgnores)
			enumConsidsAndIgnores,
			]
	
			
	#######
	
	def __init__(self, osacallbacks, terminologycache):
	#	appscript.terminology._terminologyCache = terminologycache # TO DO: single shared cache throughout component
	
		print >> stderr, 'initing AppscriptServices: (%r %r)' %(osacallbacks, terminologycache) # debug
		# TO DO: build eventhandlerbycode table (another option is to use existing commandbyname tables) - get script's callables, and put the ones whose names match dictionary commands into a by-code table;
		#	or wait for events to arrive, then look up individual definitions in prebuilt eventhandlerbycode
		# note: should support synonyms (same code, different names?)
		hostapp = appscript.app()
		self.codecs = hostapp.AS_appdata.connect()
		self.pack = self.codecs.pack
		self.unpack = self.codecs.unpack
		#######
		def createappleevent(self, eventclass, eventid, target, returnid, transactionid):
			print >> stderr, '****createappleevent %r (%r %r)' % (osacallbacks, eventclass, eventid) # debug
			return invokecreateproc(eventclass, eventid, target, returnid, transactionid, osacallbacks)
		self.createappleevent = createappleevent
		def sendappleevent(self, flags, timeout):
			print >> stderr, '****sendappleevent' # debug
			return invokesendproc(self.AEM_event, flags, timeout, osacallbacks)
		self.sendappleevent = sendappleevent
	
	
	def installcallbacks(self): # note: modifying aem module in-situ will be a bit unsafe if there's only a single interpreter supporting multiple component instances; should work ok when there's separate interpreters though
		aem.Event._createAppleEvent = self.createappleevent
		aem.Event._sendAppleEvent = self.sendappleevent
	
	#######
	# unpack Apple events
	
	def unpackappleevent(self, desc):
		# TO DO: when unpacking references, use keyAddressAttr as the reference root
		# TO DO: when unpacking keyAddressAttr, really need to convert AEAddressDesc into appscript.app path/url parameter for readability
		attributes, parameters = {}, {}
		for key in self._kEventAttributes:
			try:
				attributes[key] = self.unpack(desc.AEGetAttributeDesc(key, typeWildCard))
			except:
				pass
		for i in range(desc.AECountItems()):
			key, value = desc.AEGetNthDesc(i + 1, typeWildCard)
			parameters[key] = self.unpack(value)
		code = attributes[keyEventClassAttr].code + attributes[keyEventIDAttr].code
		return code, attributes, parameters


#######