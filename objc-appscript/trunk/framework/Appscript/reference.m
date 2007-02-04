//
//  reference.m
//  appscript
//
//  Copyright (C) 2007 HAS
//

#import "reference.h"


/**********************************************************************/


@implementation ASAppData

- (id)initWithApplicationClass:(Class)appClass
				 constantClass:(Class)constClass
				referenceClass:(Class)refClass
					targetType:(ASTargetType)type
					targetData:(id)data {
	self = [super init];
	if (!self) return self;
	aemApplicationClass = appClass;
	constantClass = constClass;
	referenceClass = refClass;
	targetType = type;
	targetData = [data retain];
	return self;
}

- (void)dealloc {
	[targetData release];
	[target release];
	[super dealloc];
}

- (void)connect {
	switch (targetType) {
		case kASTargetCurrent:
			target = [[aemApplicationClass alloc] init];
			break;
		case kASTargetName:
			target = [[aemApplicationClass alloc] initWithURL: AEMFindAppWithName(targetData)];
			break;
		case kASTargetPath:
			target = [[aemApplicationClass alloc] initWithPath: targetData];
			break;
		case kASTargetURL:
			target = [[aemApplicationClass alloc] initWithURL: targetData];
			break;
		case kASTargetPID:
			target = [[aemApplicationClass alloc] initWithPID: [targetData unsignedLongValue]];
			break;
		case kASTargetDescriptor:
			target = [[aemApplicationClass alloc] initWithDescriptor: targetData];
	}
}

- (id)target { // returns AEMApplication instance or equivalent
	if (!target)
		[self connect];
	return target;
}

// override pack, various unpack methods

- (NSAppleEventDescriptor *)pack:(id)object {
	if ([object isKindOfClass: [ASReference class]])
		return [object AS_packSelf: self];
	else if ([object isKindOfClass: [ASConstant class]])
		return [object AS_packSelf: self];
	else
		return [super pack: object];
}

- (id)unpackAERecordKey:(AEKeyword)key {
	return [constantClass constantWithCode: key];
}

- (id)unpackType:(NSAppleEventDescriptor *)desc {
	id result;
	
	result = [constantClass constantWithCode: [desc typeCodeValue]];
	if (!result)
		result = [super unpackType: desc];
	return result;
}

- (id)unpackEnum:(NSAppleEventDescriptor *)desc {
	id result;
	
	result = [constantClass constantWithCode: [desc enumCodeValue]];
	if (!result)
		result = [super unpackType: desc];
	return result;
}

- (id)unpackProperty:(NSAppleEventDescriptor *)desc {
	id result;
	
	result = [constantClass constantWithCode: [desc typeCodeValue]];
	if (!result)
		result = [super unpackType: desc];
	return result;
}

- (id)unpackKeyword:(NSAppleEventDescriptor *)desc {
	id result;
	
	result = [constantClass constantWithCode: [desc typeCodeValue]];
	if (!result)
		result = [super unpackType: desc];
	return result;
}

- (id)unpackObjectSpecifier:(NSAppleEventDescriptor *)desc {
	return [referenceClass referenceWithAppData: self
								aemReference: [super unpackObjectSpecifier: desc]];
}

- (id)unpackInsertionLoc:(NSAppleEventDescriptor *)desc {
	return [referenceClass referenceWithAppData: self
								aemReference: [super unpackInsertionLoc: desc]];
}

@end


/**********************************************************************/


@implementation ASCommand

// note: current design doesn't support returnID (TO DO: see if returnID attribute can be set later)

+ (id)commandWithAppData:(id)appData
			  eventClass:(AEEventClass)classCode
				 eventID:(AEEventID)code
		 directParameter:(id)directParameter
		 parentReference:(id)parentReference {
	return [[[[self class] alloc] initWithAppData: appData
									   eventClass: classCode
										  eventID: code
								  directParameter: directParameter
								  parentReference: parentReference] autorelease];
}

- (id)initWithAppData:(id)appData
		   eventClass:(AEEventClass)classCode
			  eventID:(AEEventID)code
	  directParameter:(id)directParameter
	  parentReference:(id)parentReference {
	  
	sendMode = kAEWaitReply + kAECanSwitchLayer;
	AS_event = [[appData target] eventWithEventClass: classCode
											 eventID: code
											  codecs: appData];
	if (directParameter)
		[AS_event setParameter: directParameter forKeyword: keyDirectObject];
	// TO DO: any additional special cases?
	if (parentReference) {
		if (directParameter)
			[AS_event setAttribute: parentReference forKeyword: keySubjectAttr];
		else
			[AS_event setParameter: parentReference forKeyword: keyDirectObject];
	}
	return self;
}


- (id)send {
	return [self sendWithTimeout: kAEDefaultTimeout];
}

- (id)sendWithTimeout:(int)timeout {
	return [AS_event sendWithMode: sendMode timeout: timeout];
}

- (OSErr)errorNumber {
	return [AS_event errorNumber];
}

- (NSString *)errorString {
	return [AS_event errorString];
}

- (void)raise {
	[AS_event raise];
}

// TO DO: attribute methods

@end


/**********************************************************************/

// TO DO: default command classes


/**********************************************************************/


@implementation ASReference

+ (id)referenceWithAppData:(id)appData aemReference:(id)aemReference {
	return [[[self alloc] initWithAppData: appData aemReference: aemReference] autorelease];
}

- (id)initWithAppData:(id)appData aemReference:(id)aemReference {
	self = [super init];
	if (!self) return self;
	AS_appData = [appData retain];
	AS_aemReference = [aemReference retain];
	return self;
}

- (void)dealloc {
	[AS_appData release];
	[AS_aemReference release];
	[super dealloc];
}


- (NSAppleEventDescriptor *)AS_packSelf:(id)codecs {
	return [AS_aemReference packSelf: codecs];
}


// TO DO: hash, isEqual

- (id)AS_appData {
	return AS_appData;
}

// TO DO: AS_newReference

- (id)AS_aemReference {
	return AS_aemReference;
}

// TO DO: default commands, properties

@end

