#!/usr/local/bin/ruby

require 'test/unit'
require "findapp"


class TC_FindApp < Test::Unit::TestCase

	def test_find
		[
			['/Applications/iCal.app', '/Applications/iCal.app'],
			['ical.app', '/Applications/iCal.app'],
			['ICAL', '/Applications/iCal.app'],
		].each do |val, res|
			assert_equal(res, FindApp.byname(val))
		end
		assert_equal('/Applications/TextEdit.app', FindApp.bycreator('ttxt'))
		assert_equal('/System/Library/CoreServices/Finder.app', FindApp.byid('com.apple.finder'))
		assert_raises(FindApp::ApplicationNotFoundError) { FindApp.byname('NON-EXISTENT-APP') }

		# assert_equal("/Users/has/\306\222\303\270u\314\210.app", FindApp.byname("\306\222\303\270u\314\210.app")) # utf8 paths work ok
	end
end
		