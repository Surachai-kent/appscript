
tell application "ASDictionary"
	export {�
		POSIX file "/System/Applications/Mail.app", �
		POSIX file "/System/Applications/TextEdit.app", �
		POSIX file "/System/Applications/Chess.app"} �
		to (POSIX file "/Users/has/test") �
		using file formats {plain text, single file HTML, frame based HTML} �
		using styles {AppleScript, Python appscript, Ruby appscript} �
		with compacting classes, showing hidden items and exporting to subfolders
end tell

