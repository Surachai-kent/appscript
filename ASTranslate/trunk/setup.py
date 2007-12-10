from distutils.core import setup
import py2app

plist = dict(
    CFBundleDocumentTypes = [
        dict(
            CFBundleTypeExtensions=[],
            CFBundleTypeName="Text File",
            CFBundleTypeRole="Editor",
            NSDocumentClass="ASTranslateDocument",
            CFBundleIdentifier="net.sourceforge.appscript.astranslate"
        ),
    ]
)


setup(
    app=["ASTranslate.py"],
    version='0.3.1',
    data_files=["MainMenu.nib", "ASTranslateDocument.nib", "rubyrenderer.rb"],
    options=dict(py2app=dict(plist=plist)),
)
