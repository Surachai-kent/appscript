"""connect - Creates Apple event descriptor records of typeProcessSerialNumber and typeApplicationURL, used to specify the target application in aemsend.send.Event() constructor.

(C) 2005 HAS
"""

from CarbonX.AE import AECreateDesc, AECreateAppleEvent
from CarbonX import kAE
import MacOS, struct

import PSN
from send import Event
from aem.types import Codecs
from time import sleep

__all__ = ['launchapp', 'isrunning', 'currentapp', 'localapp', 'remoteapp']

######################################################################
# PRIVATE
######################################################################

_launchContinue = 0x4000
_launchNoFileFlags = 0x0800
_launchDontSwitch = 0x0200

_kNoProcess = 0
_kCurrentProcess = 2

_defaultCodecs = Codecs()

_nullAddressDesc = AECreateDesc(kAE.typeProcessSerialNumber, struct.pack('LL', 0, _kNoProcess)) # CarbonX complains if you pass None as address in AECreateAppleEvent, so we give it one to throw away

_launchEvent = Event(_nullAddressDesc, 'ascrnoop').AEM_event
_runEvent = Event(_nullAddressDesc, 'aevtoapp').AEM_event

#######

def _psnForApplicationPath(path):
	# Search through running processes until one with matching path is found. Raises MacOS error -600 if app isn't running.
	path = path.lower()
	highPSN, lowPSN, fsRef = PSN.GetNextProcess(0, 0) # kNoProcess
	while 1:
		try:
			fsRef.FSCompareFSRefs(path) # raises errors unless paths match, or if fsref is None
			break
		except:
			highPSN, lowPSN, fsRef = PSN.GetNextProcess(highPSN, lowPSN) # error -600 if no more processes left
	return highPSN, lowPSN


def _makePSNAddressDesc(psn):
	return AECreateDesc(kAE.typeProcessSerialNumber, struct.pack('LL', *psn))


######################################################################
# PUBLIC
######################################################################

def launchapp(path):
	"""Send a 'launch' event to an application. If application is not already running, it will be launched in background first."""
	try:
		# If app is already running, calling LaunchApplication will send a 'reopen' event, so need to check for this first:
		psn = _psnForApplicationPath(path)
	except MacOS.Error, err:
		if err[0] == -600: # Application isn't running, so launch it and send it a 'launch' event:
			sleep(1)
			PSN.LaunchApplication(path, _launchEvent,
					_launchContinue + _launchNoFileFlags + _launchDontSwitch)
		else:
			raise
	else: # App is already running, so send it a 'launch' event:
		AECreateAppleEvent('ascr', 'noop', _makePSNAddressDesc(psn), kAE.kAutoGenerateReturnID, 
				kAE.kAnyTransactionID).AESendMessage(kAE.kAEWaitReply, kAE.kAEDefaultTimeout)


def isrunning(path):
	"""Is a local application running?"""
	try:
		_psnForApplicationPath(path)
		return True
	except MacOS.Error, err:
		if err[0] == -600: 
			return False
		else:
			raise

#######

currentapp = AECreateDesc(kAE.typeProcessSerialNumber, struct.pack('LL', 0, _kCurrentProcess))


def localapp(path):
	"""Make an AEAddressDesc identifying a local application. (Application will be launched if not already running.)
		path : string -- full path to application, e.g. '/Applications/TextEdit.app'
		Result : AEAddressDesc
	"""
	# Always create AEAddressDesc by process serial number; that way there's no confusion if multiple versions of the same app are running
	try:
		psn = _psnForApplicationPath(path)
	except MacOS.Error, err:
		if err[0] == -600: # Application isn't running, so launch it in background and send it a standard 'run' event.
			sleep(1)
			psn = PSN.LaunchApplication(path, _runEvent, 
					_launchContinue + _launchNoFileFlags + _launchDontSwitch)
		else:
			raise
	return _makePSNAddressDesc(psn)


def remoteapp(url):
	"""Make an AEAddressDesc identifying a running application on another machine.
		url : string -- URL for remote application, e.g. 'eppc://user:password@0.0.0.1/TextEdit'
		Result : AEAddressDesc
	"""
	return AECreateDesc(kAE.typeApplicationURL, url)

