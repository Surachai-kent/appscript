#import <Foundation/Foundation.h>
#import "Appscript/Appscript.h"

int main(int argc, char *argv[]) {
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    AEMApplication *textedit;
    AEMEvent *evt;
    id result;
    
    textedit = [[AEMApplication alloc]
                 initWithPath: @"/Applications/TextEdit.app"];
    NSLog(@"textedit:\n%@\n\n", textedit);
    
    // tell application "TextEdit" to \
    //     make new document with properties {text:"Hi!"}
    
	NSLog(@"make new document:\n");
    evt = [textedit eventWithEventClass: 'core' eventID: 'crel'];
    [evt setParameter: [AEMType typeWithCode: 'docu'] forKeyword: 'kocl'];
    [evt setParameter: [NSDictionary dictionaryWithObjectsAndKeys:
                        @"Hi!", [AEMType typeWithCode: 'ctxt']]
           forKeyword: 'prdt'];
    result = [evt send];
    if (result) 
        NSLog(@"result:\n%@\n\n", result);
    else
        NSLog(@"error:\nnumber: %i\nmessage: %@\n\n",
		      [evt errorNumber], [evt errorString]);

    // tell application "TextEdit" to get text of document 1
	
	NSLog(@"get text of document 1:\n");
    evt = [textedit eventWithEventClass: 'core' eventID: 'getd'];
    [evt setParameter: [[[AEMApp elements: 'docu'] at: 1] property: 'ctxt']
           forKeyword: keyDirectObject];
    result = [evt send];
    if (result) 
        NSLog(@"result:\n%@\n\n", result);
    else
        NSLog(@"error:\nnumber: %i\nmessage: %@\n\n",
		      [evt errorNumber], [evt errorString]);

    // tell application "TextEdit" to get document 100
	
	NSLog(@"get document 100:\n");
    evt = [textedit eventWithEventClass: 'core' eventID: 'getd'];
    [evt setParameter: [[AEMApp elements: 'docu'] at: 100] forKeyword: keyDirectObject];
    result = [evt send];
    if (result) 
        NSLog(@"result:\n%@\n\n", result);
    else
        NSLog(@"error:\nnumber: %i\nmessage: %@\n\n",
		      [evt errorNumber], [evt errorString]);
	
    // tell application "TextEdit" to get every document

	NSLog(@"get every document:\n");
    evt = [textedit eventWithEventClass: 'core' eventID: 'getd'];
    [evt setParameter: [AEMApp elements: 'docu'] forKeyword: keyDirectObject];
    result = [evt send];
    if (result) 
        NSLog(@"result:\n%@\n\n", result);
    else
        NSLog(@"error:\nnumber: %i\nmessage: %@\n\n",
		      [evt errorNumber], [evt errorString]);

    [textedit release];
    [pool release];
    return 0;
}