tell application "ASDictionary"
	export dictionaries {"/Applications/Mail.app" as POSIX file, �
		"/Applications/TextEdit.app" as POSIX file, �
		"/Applications/Chess.app" as POSIX file} �
		to ("/Users/has/test" as POSIX file) �
		using file formats {plain text, single file HTML, frame based HTML} �
		using styles {AppleScript, Python appscript, Ruby appscript, ObjC appscript} �
		with compacting classes, showing hidden items and exporting to subfolders
end tell
