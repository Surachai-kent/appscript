//
//  codecs.h
//  Copyright (C) 2007 HAS
//

#import <Cocoa/Cocoa.h>
#import <Carbon/Carbon.h>


/**********************************************************************/
// convenience macros

#define AEMTrue [AEMBoolean True]
#define AEMFalse [AEMBoolean False]

#define AEMType(code) [NSAppleEventDescriptor descriptorWithTypeCode: code]
#define AEMEnum(code) [NSAppleEventDescriptor descriptorWithEnumCode: code]


/**********************************************************************/


@interface AEMBoolean : NSNumber

+ (id)True;

+ (id)False;

@end


/**********************************************************************/


@interface AEMCodecs : NSObject

//- (void)addUnitTypes:(NSArray *)typeDefs; // TO DO

// main pack methods; subclasses can override to process still-unconverted objects

- (NSAppleEventDescriptor *)packUnknown:(id)data;

- (NSAppleEventDescriptor *)pack:(id)anObject;

- (NSAppleEventDescriptor *)packArray:(NSArray *)anObject;

- (NSAppleEventDescriptor *)packDictionary:(NSDictionary *)anObject;

// main unpack methods; subclasses can override to process still-unconverted objects

- (id)unpackUnknown:(NSAppleEventDescriptor *)desc;

- (id)unpack:(NSAppleEventDescriptor *)desc;

- (id)unpackAEList:(NSAppleEventDescriptor *)desc;

- (id)unpackAERecord:(NSAppleEventDescriptor *)desc;

- (id)unpackAERecordKey:(NSAppleEventDescriptor *)desc;

- (id)fullyUnpackObjectSpecifier:(NSAppleEventDescriptor *)desc;

- (id)unpackObjectSpecifier:(NSAppleEventDescriptor *)desc;

- (id)unpackInsertionLoc:(NSAppleEventDescriptor *)desc;

- (id)app;

- (id)con;

- (id)its;

- (id)unpackCompDescriptor:(NSAppleEventDescriptor *)desc;

- (id)unpackLogicalDescriptor:(NSAppleEventDescriptor *)desc;

@end
