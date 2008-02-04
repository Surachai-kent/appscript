#!/usr/local/bin/python

from Carbon.Cm import OpenDefaultComponent
from osascript.osa import OSAComponentInstance
from aem.kae import *
from aem import Codecs

codecs = Codecs()

osac = OSAComponentInstance(OpenDefaultComponent('osa ', 'ascr'))

script = '''tell app "Finder" to get folder 1 of home'''

scriptDesc = codecs.pack(script)

scriptID = osac.OSACompile(scriptDesc, kOSAModeNull, kOSANullScript)
resultID = osac.OSAExecute(scriptID, kOSANullScript, kOSAModeNull)


print `codecs.unpack(osac.OSAGetSource(scriptID, typeWildCard))`
print
print `codecs.unpack(osac.OSADisplay(resultID, typeWildCard, kOSAModeNull))`
print
print `codecs.unpack(osac.OSACoerceToDesc(resultID, typeWildCard, 0))`

osac.OSADispose(scriptID)
osac.OSADispose(resultID)