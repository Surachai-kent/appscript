"""typedefs -- Used by client in installeventhandler() to specify the required type(s) of each parameter of an Apple event handler. These classes are also responsible for coercing and unpacking event parameters on behalf of unpackevent.py.

(C) 2005 HAS
"""

from aem import ae, kae, AEType
import struct

from handlererror import EventHandlerError

# TO DO: build decent error messages pinpointing problem.

if struct.pack("h", 1) == '\x00\x01': # host is big-endian
	fourCharCode = lambda code: code
else: # host is small-endian
	fourCharCode = lambda code: code[::-1]
	
######################################################################
# PUBLIC
######################################################################

class ArgDef: 
	"""Abstract base class, used internally for typechecking."""
	
	def AEM_unpack(self, desc, codecs):
		try:
			return self._unpack(desc, codecs)
		except ae.MacOSError, e:
			number, message = e[0], e.args[1:] and e[1] or None
			if number == -1700: # coercion error
				return False, EventHandlerError(number, message, object=desc, coercion= AEType(self.AEM_code))
			else:
				return False, EventHandlerError(number, message, object=desc)


#######
# Concrete classes

class ArgDesc(ArgDef):
	"""
		Describes a raw AEDesc. Clients shouldn't instantiate directly; use kArgDesc instead.
		
		- aemreceive will pass CarbonX.AEDesc directly to callback as-is.
	"""
	
	AEM_code = kae.typeWildCard
	
	def AEM_unpack(self, desc, codecs):
		return True, desc

kArgDesc = ArgDesc()


class ArgMissingValue(ArgDef):
	"""
		Describes a 'missing value' constant. Clients shouldn't instantiate directly; use kArgMissingValue instead.
		
		May be supplied in ArgMultiChoice to indicate that aem.AEType('msng') is an acceptable parameter value, 
		e.g. ArgMultiChoice(kae.typeUnicodeText, kArgMissingValue')
	"""
	
	AEM_code = kae.typeType
	
	_cMissingValue = fourCharCode(kae.cMissingValue)
	
	def AEM_unpack(self, desc, codecs):
		if desc.type == kae.typeType and desc.data == self._cMissingValue:
			return True, codecs.unpack(desc)
		else:
			return False, EventHandlerError(-1704, "Not a 'missing value' constant.", desc)

kArgMissingValue = ArgMissingValue()


class ArgNull(ArgDef):
	"""
		Describes a typeNull descriptor. Clients shouldn't instantiate directly; use kArgNull instead.
		
		May be supplied in ArgMultiChoice to indicate that None is an acceptable parameter value, 
		e.g. ArgMultiChoice(kae.typeUnicodeText, kArgNull)
	"""
	
	AEM_code = kae.typeNull
	
	def AEM_unpack(self, desc, codecs):
		if desc.type == kae.typeNull:
			return True, None
		else:
			return False, EventHandlerError(-1704, "Not a typeNull descriptor.", desc)

kArgNull = ArgNull()


class ArgAny(ArgDef):
	"""
		Describes any value. Clients shouldn't instantiate directly; use kArgAny instead.
	"""
	
	AEM_code = kae.typeWildCard
	
	def AEM_unpack(self, desc, codecs):
		return True, codecs.unpack(desc)

kArgAny = ArgAny()


class ArgType(ArgDef):
	"""
		Describes a simple AE type, e.g. ArgType('utxt') = a value of typeUnicodeText
		
		- aemreceive will attempt to coerce descriptors of other types to the specified type before unpacking.
	"""
	def __init__(self, code):
		"""
			code : str -- a 4-character AE code
		"""
		if not isinstance(code, str) and len(code) == 4:
			raise TypeError, "Invalid AE type code: %r" % code
		self.AEM_code = code
	
	def _unpack(self, desc, codecs):
		if desc.type == self.AEM_code or self.AEM_code == kae.typeWildCard:
			return True, codecs.unpack(desc)
		else:
			return True, codecs.unpack(desc.AECoerceDesc(self.AEM_code))


class ArgEnum(ArgDef):
	"""
		Describes an AE enumeration, taking one or more enumerator codes in its constructor, 
			e.g. ArgEnum('yes ', 'no  ', 'ask ') = AEEnum('yes ') | AEEnum('no  ') | AEEnum('ask ')
		
		- aemreceive will attempt to coerce descriptors of other types to typeEnumerated before unpacking.
		- aemreceive will raise error -1704 if the given enum if not one of those specified.
	"""
	AEM_code = kae.typeEnumerated
	
	def __init__(self, *codes):
		"""
			*codes : str -- one or more 4-character AE codes
		"""
		if not codes:
			raise TypeError, "__init__() requires at least 2 arguments"
		for code in codes:
			if not isinstance(code, str) and len(code) == 4:
				raise TypeError, "Invalid AE enum code: %r" % code
		self._codes = [fourCharCode(code) for code in codes]
	
	def _unpack(self, desc, codecs):
		desc = desc.AECoerceDesc(kae.typeEnumerated)
		if desc.data not in self._codes:
			return False, EventHandlerError(-1704, "Bad enumerator.", desc, AEType(kae.typeEnumerated))
		return True, codecs.unpack(desc)


class ArgListOf(ArgDef):
	"""
		Describes a list of values of given type(s). Takes a single ArgType/ArgEnum or list of ArgTypes/ArgEnums as its only argument.
	"""
	
	def __init__(self, datatype):
		"""
			datatype : ArgType | ArgEnum | ArgMultiChoice -- (strings/lists will be converted to ArgType/ArgMultiChoice automatically)
		"""
		self._datatype = buildDefs(datatype)
	
	def _unpack(self, desc, codecs):
		desc = desc.AECoerceDesc(kae.typeAEList)
		result = []
		for i in range(1, desc.AECountItems() + 1):
			succeeded, value = self._datatype.AEM_unpack(desc.AEGetNthDesc(i, kae.typeWildCard)[1], codecs)
			if not succeeded:
				return False, value
			result.append(value)
		return True, result


class ArgMultiChoice(ArgDef):
	"""
		Used to encapsulate multiple acceptable types. If event parameter's type matches one of those given, will unpack exactly; otherwise will attempt to coerce and upack with each in turn until one succeeds or all fail.
	"""
	AEM_code = '????'

	def __init__(self, *datatypes):
		# datatypes = a list of ArgDef subclasses
		self._exactTypeDefs = {} # When unpacking an AEDesc, if its type exactly matches one of the unpackers provided then use that
		self._exactEnumDefs = [] # (all enums share same type, typeEnumerated, so we store them in this list instead of dict above)
		self._datatypesByOrder = [] # If no exact match exists, try coercing and unpacking with each unpacker provided until one succeeds
		if not datatypes:
			raise TypeError, "No argument type definitions given."
		for datatype in datatypes:
			datatype = buildDefs(datatype)
			self._datatypesByOrder.append(datatype)
			if datatype.AEM_code == kae.typeEnumerated:
				self._exactEnumDefs.append(datatype)
			else:
				self._exactTypeDefs[datatype.AEM_code] = datatype
	
	def AEM_unpack(self, desc, codecs):
		# If AEDesc's type exactly matches one of the supplied unpackers (not including typeEnumerated), use that
		if self._exactTypeDefs.has_key(desc.type):
			succeeded, value = self._exactTypeDefs[desc.type].AEM_unpack(desc, codecs)
			if succeeded:
				return True, value
		# If AEDesc is an enumerator, try to unpack it exactly
		if desc.type == kae.typeEnumerated:
			for datatype in self._exactEnumDefs:
				succeeded, value = datatype.AEM_unpack(desc, codecs)
				if succeeded:
					return True, value
		# No exact conversion, so apply each unpacker in turn until one of them manages to coerce and unpack the value
		for datatype in self._datatypesByOrder:
			succeeded, value = datatype.AEM_unpack(desc, codecs)
			if succeeded:
				return True, value
		# Unable to unpack value as any of the desired types
		return False, value # returns last failed coercion details


#######


def buildDefs(datatype):
	if isinstance(datatype, ArgDef):
		return datatype
	elif isinstance(datatype, list): # user may supply ArgMultiChoice as list for convenience
		return ArgMultiChoice(*datatype)
	else: # user may supply ArgType as 4-char code string for convenience
		return ArgType(datatype)


