#!/usr/local/bin/ruby
# Copyright (C) 2006 HAS. 
# Released under MIT License.

######################################################################
# TERMINOLOGY PARSER
######################################################################

module TerminologyParser
	
	require "_appscript/reservedkeywords" # names of all existing methods on ASReference::Application
	
	class BigEndianParser
		@@_nameCache = {}
		LegalFirst = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
		LegalRest = LegalFirst + '0123456789'
		
		def initialize
			@enumerators = {}
			@properties = {}
			@commands = {}
			@_pluralClassNames = {}
			@_singularClassNames = {}
		end
		
		def _integer
			@_ptr += 2
			return @_str[@_ptr - 2, 2].unpack('S')[0]
		end
		
		def _word
			@_ptr += 4
			return @_str[@_ptr - 4, 4]
		end
		
		def _name
			count = @_str[@_ptr]
			@_ptr += 1 + count
			s = @_str[@_ptr - count, count]
			if not @@_nameCache.has_key?(s)
				legal = LegalFirst
				res = ''
				s.split(//).each do |c|
					if legal[c]
						res += c
					else
						case c
							when ' ', '-', '/'
								res += '_'
							when '&'
								res += 'and'
						else
							if res == ''
								res = '_'
							end
							res += "0x#{c.unpack('HXh')}"
						end
					end
					legal = LegalRest
				end
				if res[0, 3] == 'AS_' or ReservedKeywords.include?(res) or res[0, 1] == '_'
					res += '_'
				end
				@@_nameCache[s] = res
			end
			return @@_nameCache[s]
		end
		
		##
		
		def parseCommand
			name = _name
			@_ptr += 1 + @_str[@_ptr]
			@_ptr += @_ptr & 1
			code = _word + _word
			# skip result
			@_ptr += 4
			@_ptr += 1 + @_str[@_ptr]
			@_ptr += @_ptr & 1
			@_ptr += 2
			# skip direct
			@_ptr += 4
			@_ptr += 1 + @_str[@_ptr]
			@_ptr += @_ptr & 1
			@_ptr += 2
			#
			currentCommandArgs = []
			@commands[code] = [name, code, currentCommandArgs]
			# args
			_integer.times do
				parameterName = _name
				@_ptr += @_ptr & 1
				parameterCode = _word
				@_ptr += 4
				@_ptr += 1 + @_str[@_ptr]
				@_ptr += @_ptr & 1
				@_ptr += 2
				currentCommandArgs.push([parameterName, parameterCode])
			end
		end
		
		def parseClass
			name = _name
			@_ptr += @_ptr & 1
			code = _word
			@_ptr += 1 + @_str[@_ptr]
			@_ptr += @_ptr & 1
			isPlural = false
			_integer.times do
				propname = _name
				@_ptr += @_ptr & 1
				propcode = _word
				@_ptr += 4
				@_ptr += 1 + @_str[@_ptr]
				@_ptr += @_ptr & 1
				flags = _integer
				if propcode != 'c@#^'
					if flags & 1 == 1
						isPlural = true
					else
						@properties[propcode] = [propname, propcode]
					end
				end
			end
			_integer.times do
				@_ptr += 4
				count = _integer
				@_ptr += 4 * count
			end
			if isPlural
				@_pluralClassNames[code] = [name, code]
			else
				@_singularClassNames[code] = [name, code]
			end
		end
		
		def parseComparison
			@_ptr += 1 + @_str[@_ptr]
			@_ptr += @_ptr & 1
			@_ptr += 4
			@_ptr += 1 + @_str[@_ptr]
			@_ptr += @_ptr & 1
		end
		
		def parseEnumeration
			@_ptr += 4
			_integer.times do
				name = _name
				@_ptr += @_ptr & 1
				code = _word
				@_ptr += 1 + @_str[@_ptr]
				@_ptr += @_ptr & 1
				@enumerators[code + name] = [name, code]
			end
		end
		
		def parseSuite
			@_ptr += 1 + @_str[@_ptr]
			@_ptr += 1 + @_str[@_ptr]
			@_ptr += @_ptr & 1
			@_ptr += 4
			@_ptr += 4
			_integer.times { parseCommand }
			_integer.times { parseClass }
			_integer.times { parseComparison }
			_integer.times { parseEnumeration }
		end
		
		def parse(aetes)
			aetes.each do |aete|
				@_str = aete.data
				@_ptr = 6
				_integer.times { parseSuite }
				if not @_ptr == @_str.length
					raise RuntimeError, "aete was not fully parsed."
				end
			end
			classes = @_pluralClassNames.clone
			classes.update(@_singularClassNames)
			elements = @_singularClassNames.clone
			elements.update(@_pluralClassNames)
			return [classes, @enumerators, @properties, elements, @commands].map! { |d| d.values }
		end
	end
	
	
	class LittleEndianParser < BigEndianParser
		def _word
			return super.reverse
		end
	end
	
	
	#######
	# Public
	
	def TerminologyParser.buildTablesForAetes(aetes)
		if [1].pack('S') == "\000\001"
			return BigEndianParser.new.parse(aetes)
		else
			return LittleEndianParser.new.parse(aetes)
		end
	end

end


######################################################################
# TERMINOLOGY TABLES BUILDER
######################################################################

module Terminology

	require "aem"
	require "_appscript/defaultterminology"

	@@_terminologyCache = {}
	
	def Terminology._makeTypeTable(classes, enums, properties)
		typebycode = DefaultTerminology::TypeByCode.clone
		typebyname = DefaultTerminology::TypeByName.clone
		[[AEM::AEType, properties], [AEM::AEEnum, enums], [AEM::AEType, classes]].each do |klass, table|
			table.each do |name, code|
				if DefaultTerminology::TypeByName.has_key?(name) and \
						DefaultTerminology::TypeByName[name].code != code
					name += '_'
				end
				typebycode[code] = name.intern
				typebyname[name.intern] = klass.new(code)
			end
		end
		return [typebycode, typebyname]
	end
	
	def Terminology._makeReferenceTable(properties, elements, commands)
		referencebycode = DefaultTerminology::ReferenceByCode.clone
		referencebyname = DefaultTerminology::ReferenceByName.clone
		[[:element, elements], [:property, properties]].each do |kind, table|
			# note: if property and element names are same (e.g. 'file' in BBEdit), will pack as property specifier unless it's a special case (i.e. see :text below). Note that there is currently no way to override this, i.e. to force appscript to pack it as an all-elements specifier instead (in AS, this would be done by prepending the 'every' keyword), so clients would need to use aem for that (but could add an 'all' method to Reference class if there was demand for a built-in workaround)
			table.each do |name, code|
				referencebycode[code] = name # TO DO: when rendering references, if singular property name and plural class name have same code, need to use either singular or plural name depending on whether it's a property() or elements() call
				referencebyname[name.intern] = [kind, code]
			end
		end
		if referencebyname.has_key?(:text) # special case: AppleScript always packs 'text of...' as all-elements specifier
			referencebyname[:text][0] = :element
		end
		commands.reverse.each do |name, code, args|
			if DefaultTerminology::DefaultCommands.has_key?(name) and \
					code != DefaultTerminology::DefaultCommands[name]
						name += '_'
			end
			dct = {}
			args.each { |argName, argCode| dct[argName.intern] = argCode }
			referencebyname[name.intern] = [:command, [code, dct]]
		end
		return referencebycode, referencebyname
	end
	
	#######
	# public
	
	def Terminology.defaultTables
		return _makeTypeTable([], [], []) + _makeReferenceTable([], [], [])
	end
	
	def Terminology.tablesForAetes(aetes)
		classes, enums, properties, elements, commands = TerminologyParser.buildTablesForAetes(aetes.delete_if { |aete| aete == nil or aete.type != 'aete' })
		return _makeTypeTable(classes, enums, properties) + _makeReferenceTable(properties, elements, commands)
	end
	
	##
	
	def Terminology.tablesForModule(terms)
		if terms::Version != 1.1
			raise RuntimeError, "Unsupported terminology module version: #{terms::Version} (requires version 1.1)."
		end
		return _makeTypeTable(terms::Classes, terms::Enumerators, terms::Properties) \
			+ _makeReferenceTable(terms::Properties, terms::Elements, terms::Commands)
	end
	
	def Terminology.tablesForApp(path, pid, url)
		if not @@_terminologyCache.has_key?([path, pid, url])
			begin
				if path
					app = AEM::Application.newPath(path)
				elsif pid
					app = AEM::Application.newPID(pid)
				elsif url
					app = AEM::Application.newURL(url)
				else
					app = AEM::Application.current
				end
				begin
					aetes = app.event('ascrgdte', {'----' => 0}).send(30 * 60)
				rescue AEM::CommandError => e
					if  e.number == -192 # aete resource not found
						aetes = []
					else
						raise
					end
				end
				if not aetes.is_a?(Array)
					aetes = [aetes]
				end
			rescue => err
				raise RuntimeError, "Can't get terminology for application (#{path or pid or url}): #{err}"
			end
			@@_terminologyCache[[path, pid, url]] = Terminology.tablesForAetes(aetes)
		end
		return @@_terminologyCache[[path, pid, url]]
	end
end

