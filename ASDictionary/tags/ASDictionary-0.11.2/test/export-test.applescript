tell application "ASDictionary"
	export {�
		POSIX file "/Applications/Mail.app", �
		POSIX file "/Applications/TextEdit.app", �
		POSIX file "/Applications/Chess.app"} �
		to (POSIX file "/Users/has/test") �
		using file formats {plain text, single file HTML, frame based HTML} �
		using styles {AppleScript, Python appscript, Ruby appscript, ObjC appscript} �
		with compacting classes, showing hidden items and exporting to subfolders
end tell