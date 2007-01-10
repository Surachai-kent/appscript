#!/usr/bin/env python

"""textdoc -- Render application terminology as plain text.

(C) 2006 HAS
"""

# TO DO: tidy

# TO DO: add option flag allowing overlapped definitions to be ignored when rendering collapsed/full definitions

# __all__ = ['IndexRenderer', 'SummaryRenderer', 'FullRenderer']

import sys

from typerenderers import gettyperenderer


######################################################################


class _Out:
	def write(self, v):
		sys.stdout.write(v.encode('utf8'))

_out = _Out()



######################################################################


class IndexRenderer:
	def __init__(self, style='appscript', options=[], out=_out):
		self._out = out
		self._sort = 'sort' in options
		self._collapse = 'collapse' in options
	
	def draw_dictionary(self, o):
		print >> self._out, o.name, 'Dictionary\n'
		print >> self._out, '  Suites:'
		for name in o.suites().names():
			print >> self._out, '    %s' % name
		print >> self._out
		for title, items in [('Commands', o.commands()), ('Classes', o.classes())]:
			print >> self._out, '  %s:' % title
			names = items.names()
			if self._sort:
				names.sort(lambda a, b: cmp(a.lower(), b.lower()))
			if self._collapse:
				unique = []
				for name in names:
					if name not in unique:
						unique.append(name)
				names = unique
			for name in names:
				print >> self._out, '    %s' % name
			print >> self._out
	
	def draw(self, o):
		getattr(self, 'draw_' + o.kind.replace('-', ''), self.draw_nothing)(o)
	
	def draw_nothing(self, o):
		pass



######################################################################


class SummaryRenderer:
	def __init__(self, style='appscript', options=[], out=_out):
		self.typerenderer = gettyperenderer(style)
		self._out = out
		self._in = ''
		self.collapse = 'collapse' in options
		self.full = 'full' in options
		self.code = 'codes' in options and (
				lambda o:'<%s> ' % self.typerenderer.escapecode(o.code)) or (lambda o:'')
	
	def indent(self):
		self._in += '  '
	
	def dedent(self):
		self._in = self._in[2:]
	
	def desc(self, o):
		s = o.description
		return s and ' -- '+s or ''
	
	##
	
	def draw(self, o):
		getattr(self, 'draw_' + o.kind.replace('-', ''), self.draw_nothing)(o)
	
	def draw_nothing(self, o):
		pass
	
	def draw_documentation(self, o):
		if o.documentation and 0:
			print >> self._out, '='*80
			print >> self._out, o.documentation
			print >> self._out, '='*80
	
	##
	
	def draw_dictionary(self, o):
		print >> self._out, o.name, 'Dictionary\n'
		self.draw_documentation(o)
		o.suites().map(self.draw_suite)
	
	##
	
	def draw_suite(self, o):
		print >> self._out, 'Suite: %s%s%s' % (o.name, not o.visible and ' [hidden]' or '', self.desc(o))
		self.draw_documentation(o)
		self.indent()
		for name, nodes, fn in [
				('Commands', o.commands(), self.draw_command),
				('Classes', o.classes(), self.draw_class),
				('Events', o.events(), self.draw_event), 
				('Enumerations', o.enumerations(), self.draw_enumeration), 
				('Record types', o.recordtypes(), self.draw_recordtype),
				('Value types', o.valuetypes(), self.draw_valuetype)]:
			if nodes and not fn == self.draw_nothing:
				print >> self._out, self._in + '%s:' % name
				self.indent()
				nodes.map(fn)
				self.dedent()
		self.dedent()
		print >> self._out
	
	
	def draw_class(self, o):
		# TO DO: kNormal/kCollapsed/kFull
		if self.full:
			o = o.full()
		elif self.collapse:
			o = o.collapse()
		print >> self._out, self._in + '%s%s%s' % (self.code(o), o.name, self.desc(o))
		self.indent()
		self.draw_classcontent(o)
		self.dedent()
		print >> self._out
	
	draw_classcontent = draw_nothing
	
	def draw_command(self, o):
		print >> self._out, self._in + '%s%s%s' % (self.code(o), o.name, self.desc(o))
		self.indent()
		self.draw_documentation(o)
		if o.directparameter:
			self.draw_directparameter(o.directparameter)
		o.parameters.map(self.draw_parameter)
		if o.result:
			self.draw_result(o.result)
		self.dedent()
		print >> self._out
	
	draw_event = draw_command
	draw_directparameter = draw_parameter = draw_result = draw_nothing
	
	def draw_recordtype(self, o):
		print >> self._out, self._in + '%s%s%s' % (self.code(o), o.name, self.desc(o))
		self.indent()
		self.draw_documentation(o)
		o.properties.map(self.draw_recordproperty)
		self.dedent()
		print >> self._out
	
	draw_enumeration = draw_recordproperty = draw_valuetype = draw_nothing



######################################################################


class FullRenderer(SummaryRenderer):
	
	# class
	
	def draw_classcontent(self, o):
		self.draw_documentation(o)
		if o.pluralname != o.name:
			print >> self._out, self._in + 'Plural:'
			self.indent()
			print >> self._out, self._in + '%s' % o.pluralname
			self.dedent()
		if not o.isunique():
			print >> self._out, self._in + 'See also:'
			suitenames = o.suitenames()[:]
			suitenames.remove(o.suitename)
			self.indent()
			print >> self._out, self._in + '%s' % ', '.join(suitenames)
			self.dedent()
		# TO DO: contents
		for name, nodes, fn in [
				('Inherits from', o.parents(), self.draw_parent),
				('Properties', o.properties(), self.draw_property),
				('Elements', o.elements(), self.draw_element),
				('Responds to', o.respondsto(), self.draw_respondsto)]:
			if nodes:
				print >> self._out, self._in + '%s:' % name
				self.indent()
				nodes.map(fn)
				self.dedent()
	
	def draw_parent(self, o):
		if o.kind == 'class': # compensate for faulty dictionaries
			print >> self._out, self._in + '%s%s (in %s)' % (self.code(o), o.name, o.suitename) # TO DO: add 'suite' if suitename doesn't end in 'Suite' or 'suite'?
		else: # bad superclass; an AE type instead of an application class (e.g. Mail) # TO DO: add error description?
			print >> self._out, self._in + '%s' % o.name
	
	def draw_property(self, o):
		print >> self._out, self._in + '%s%s%s : %s%s' % (self.code(o), o.name,
				o.access == 'r' and ' (r/o)' or o.access == 'w' and ' (w/o)' or '',
				self.typerenderer.render(o.types),
				self.desc(o))
		self.draw_documentation(o)
		
	def draw_element(self, o):
		print >> self._out, self._in + '%s%s -- by %s' % (self.code(o.type), 
				self.typerenderer.elementname(o.type),
				', '.join(o.accessors()))
		self.draw_documentation(o)
		
	def draw_respondsto(self, o):
		print >> self._out, self._in + '%s' % o.name
		self.draw_documentation(o)
	
	# command
	
	def draw_directparameter(self, o):
		print >> self._out, self._in + '%s%s%s%s' % (o.optional and '[' or '', 
				self.typerenderer.render(o.types), o.optional and ']' or '', self.desc(o))
		self.draw_documentation(o)
	
	def draw_parameter(self, o):
		print >> self._out, self._in + '%s%s%s : %s%s%s' % (o.optional and '[' or '', self.code(o), o.name,
				self.typerenderer.render(o.types), o.optional and ']' or '', self.desc(o))
		self.draw_documentation(o)
	
	def draw_result(self, o):
		print >> self._out, self._in + 'Result: %s%s' % (self.typerenderer.render(o.types), self.desc(o))
		self.draw_documentation(o)
	
	# enum, etc.
	
	def draw_enumeration(self, o):
		code = self.code(o)
		haslabel = code or o.name and o.name != o.code or o.description
		if haslabel:
			print >> self._out, self._in + '%s%s' % (code or o.name, self.desc(o))
			self.indent()
		for enumerator in o.enumerators():
			self.draw_enumerator(enumerator)
		self.draw_documentation(o)
		if haslabel:
			self.dedent()
		print >> self._out
	
	def draw_enumerator(self, o):
		print >> self._out, self._in + '%s%s%s' % (self.code(o), o.name, self.desc(o))
		self.draw_documentation(o)
	
	def draw_valuetype(self, o):
		print >> self._out, self._in + '%s%s%s' % (self.code(o), o.name, self.desc(o))
		self.draw_documentation(o)
	

