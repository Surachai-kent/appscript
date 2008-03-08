//
//  referencerenderer.h
//  appscript
//
//   Copyright (C) 2007-2008 HAS
//

#import "reference.h"
#import "utils.h"

/**********************************************************************/
// reference renderer base

@interface ASReferenceRenderer : AEMResolver {
	NSString *prefix;
	NSMutableString *result;
}

- (id)initWithPrefix:(NSString *)prefix_;

+ (NSString *)render:(id)object;

+ (NSString *)render:(id)object withPrefix:(NSString *)prefix_;

- (NSString *)result;

/*******/

- (NSString *)propertyByCode:(OSType)code;
- (NSString *)elementByCode:(OSType)code;

/*******/

- (NSString *)format:(id)object;

@end

