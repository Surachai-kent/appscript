"""osaterminology.tables.tablebuilder -- builds lookup tables similar to those used by appscript itself; modified from py-appscript's terminology module"""

from aem import AEType, AEEnum, EventError, findapp, ae

from tableparser import buildtablesforaetes
import osaterminology.defaultterminology

__all__ = ['kType', 'kEnum', 'kProperty', 'kElement', 'kCommand', 'TerminologyTableBuilder']

######################################################################

kType = 't'
kEnum = 'n'
kProperty = 'p'
kElement = 'e'
kCommand = 'c'

######################################################################

class TerminologyTableBuilder:

	def __init__(self, style='py-appscript'):
		self._style = style
		defaultterminology = osaterminology.defaultterminology.getterms(style)
		# default definitions
		self._typebyname = {} # used to encode class and enumerator keywords
		self._referencebycode = {} # used to decode property and element specifiers
		self._referencebyname = {} # used to encode property and element specifiers and Apple events
		self._defaulttypecodebyname = {} # used to check for name collisions
		self._defaultcommandcodebyname = {} # used to check for name collisions
		self._typebycode = {} # used to decode class (typeType) and enumerator (typeEnum) descriptors
		self._terminologycache = {} # cache parsed terminology
		for _, enumerators in defaultterminology.enumerations:
			for name, code in enumerators:
				self._typebyname[name] = (kEnum, code) # AEEnum(code)
				self._typebycode[code] = name # Keyword(name)
				self._defaulttypecodebyname[name] = code
		for defs in [defaultterminology.types, defaultterminology.properties]:
			for name, code in defs:
				self._typebyname[name] = (kType, code) # AEType(code)
				self._typebycode[code] = name # Keyword(name)
				self._defaulttypecodebyname[name] = code
		for name, code in defaultterminology.properties:
			self._referencebycode[kProperty + code] = (kProperty, name)
			self._referencebyname[name] = (kProperty, code)
		for name, code in defaultterminology.elements:
			self._referencebycode[kElement + code] = (kElement, name)
			self._referencebyname[name] = (kElement, code)
		for name, code, params in defaultterminology.commands:
			self._referencebyname[name] = (kCommand, (code, dict(params)))
			self._referencebycode[kCommand + code] = (kCommand, (name, dict([(v, k) for k, v in params])))
			self._defaultcommandcodebyname[name] = code


	# Translation table parsers
	
	def _maketypetable(self, classes, enums, properties):
		typebycode = self._typebycode.copy()
		typebyname = self._typebyname.copy()
		for kind, table in [(kType, properties), (kEnum, enums), (kType, classes)]:
			for i, (name, code) in enumerate(table):
				if self._defaulttypecodebyname.get(name, code) != code:
					name += '_'
				typebycode[code] = name # Keyword(name)
				name, code = table[-i - 1]
				if self._defaulttypecodebyname.get(name, code) != code:
					name += '_'
				typebyname[name] = (kind, code) # klass(code)
		return typebycode, typebyname
	
	
	def _makereferencetable(self, properties, elements, commands):
		referencebycode = self._referencebycode.copy()
		referencebyname = self._referencebyname.copy()
		for kind, table in [(kElement, elements), (kProperty, properties)]:
			for i, (name, code) in enumerate(table):
				if self._defaulttypecodebyname.get(name, code) != code:
					name += '_'
				referencebycode[kind+code] = (kind, name)
				name, code = table[-i - 1]
				if self._defaulttypecodebyname.get(name, code) != code:
					name += '_'
				referencebyname[name] = (kind, code)
		if 'text' in referencebyname:
			referencebyname['text'] = (kElement, referencebyname['text'][1])
		for name, code, args in commands[::-1]:
			if code != self._defaultcommandcodebyname.get(name, code):
				name += '_'
			referencebyname[name] = (kCommand, (code, dict(args)))
			referencebycode[kCommand+code] = (kCommand, (name, dict([(v, k) for k, v in args])))
		return referencebycode, referencebyname
	

	def defaulttables(self):
		return (self._typebycode.copy(), self._typebyname.copy(), 
				self._referencebycode.copy(), self._referencebyname.copy())
	
	
	def aetesforapp(self, app):
		"""Get aetes from local/remote app via an ascrgdte event; result is a list of byte strings."""
		try:
			aetes = app.event('ascrgdte', {'----':0}).send(120 * 60)
		except Exception, e: # (e.g.application not running)
			if isinstance(e, EventError) and e.number == -192:
				aetes = []
			else:
				raise RuntimeError, "Can't get terminology for application (%r): %s" % (app, e)
		if not isinstance(aetes, list):
			aetes = [aetes]
		return [aete for aete in aetes if isinstance(aete, ae.AEDesc) and aete.type == 'aete' and aete.data]
	
	
	def tablesforaetes(self, aetes):
		"""Build terminology tables from a list of unpacked aete byte strings.
			Result : tuple of dict -- (typebycode, typebyname, referencebycode, referencebyname)
		"""
		classes, enums, properties, elements, commands = buildtablesforaetes(aetes, self._style)
		return self._maketypetable(classes, enums, properties) + \
				self._makereferencetable(properties, elements, commands)
	
	
	def tablesformodule(self, terms):
		"""Build terminology tables from a dumped terminology module.
			Result : tuple of dict -- (typebycode, typebyname, referencebycode, referencebyname)
		"""
		return self._maketypetable(terms.classes, terms.enums, terms.properties) \
				+ self._makereferencetable(terms.properties, terms.elements, terms.commands)
		
	
	def tablesforapp(self, app):
		"""Build terminology tables for an application.
			app : aem.Application
			Result : tuple of dict -- (typebycode, typebyname, referencebycode, referencebyname)
		"""
		if app.AEM_identity not in self._terminologycache:
			self._terminologycache[app.AEM_identity] = self.tablesforaetes(self.aetesforapp(app))
		return self._terminologycache[app.AEM_identity]

