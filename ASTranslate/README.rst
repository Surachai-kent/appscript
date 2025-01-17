About ASTranslate
=================

A simple tool for converting application commands written in AppleScript into 
their appscript equivalent.


Usage
-----

1. Launch ASTranslate and type or paste one or more AppleScript commands into 
   the top half of the window, e.g.:

     tell application "TextEdit" to get text of every document

     with timeout of 10 seconds
       tell application "Finder" to folder 1 of home as alias
     end timeout

2. Select Document > Translate. The AppleScript code is compiled and executed, 
   and the bottom pane displays each Apple event sent by AppleScript as 
   appscript code, e.g.:

     app('TextEdit').documents.text.get()

     app('Finder').home.folders[1].get(resulttype=k.alias, timeout=10)

Click on the Python and Ruby tabs below the bottom pane to switch translations. 

The 'Send events to app' checkbox can be unchecked to prevent Apple events 
being sent to the target application. This is particularly useful when 
obtaining translations of potentially destructive commands such as 'delete'.


Notes
-----

- ASTranslate only sniffs outgoing Apple events sent by AppleScript; it's 
  not a full-blown AppleScript->Python/Ruby code converter. The output 
  is not intended to be production-ready code, but should be helpful when 
  figuring out how to translate a particular reference or command from 
  AppleScript to Python/Ruby.

- ASTranslate translates application commands only. Standard Additions 
  commands are not translated.

- If the 'Send Apple Events' option is checked, remember that all Apple events 
  sent by AppleScript will be passed to applications to be handled as normal. 
  i.e. Destructive commands (e.g. 'tell "Finder" to delete some file') will 
  still do their destructive thing; unsuccessful commands will cause 
  AppleScript to raise an error, etc.

- Unchecking the 'Send Apple Events' option also prevents application commands
  returning a result. If the AppleScript code expects a command to return a 
  value, this will likely result in an AppleScript error.


Copyright
---------

ASTranslate is released into the public domain.

http://appscript.sourceforge.net/
