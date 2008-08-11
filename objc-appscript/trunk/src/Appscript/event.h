//
//  event.h
//  aem
//
//   Copyright (C) 2007-2008 HAS
//

#import "codecs.h"
#import "sendthreadsafe.h"
#import "utils.h"
#import "objectrenderer.h"


/**********************************************************************/
// NSError constants

NSString *kASErrorDomain; // @"net.sourceforge.appscript.objc-appscript.ErrorDomain"; domain name for NSErrors returned by appscript

/*
 * -sendWithError: will return an NSError containing error code, localized description, and a userInfo dictionary
 * containing kASErrorNumberKey (this has the same value as -[NSError code]) and zero or more other keys:
 */

NSString *kASErrorNumberKey;			// @"ErrorNumber"; error number returned by Apple Event Manager or application
NSString *kASErrorStringKey;			// @"ErrorString"; error string returned by application, if given
NSString *kASErrorBriefMessageKey;		// @"ErrorBriefMessage"; brief error string returned by application, if given
NSString *kASErrorExpectedTypeKey;		// @"ErrorExpectedType"; AE type responsible for a coercion error (-1700), if given
NSString *kASErrorOffendingObjectKey;	// @"ErrorOffendingObject"; value or object specifer responsible for error, if given
NSString *kASErrorFailedEvent;			// @"ErrorFailedEvent"; the AEMEvent object that returned the error


/**********************************************************************/
// typedefs

typedef enum {
	kAEMDontUnpack,
	kAEMUnpackAsItem,
	kAEMUnpackAsList
} AEMUnpackFormat;


typedef OSErr(*AEMCreateProcPtr)(AEEventClass theAEEventClass,
							     AEEventID theAEEventID,
							     const AEAddressDesc *target,
							     AEReturnID returnID,
							     AETransactionID transactionID,
							     AppleEvent *result);


typedef OSStatus(*AEMSendProcPtr)(const AppleEvent *event,
								  AppleEvent *reply,
								  AESendMode sendMode,
								  long timeOutInTicks);


/**********************************************************************/
// Event class
/*
 * Note: clients shouldn't instantiate AEMEvent directly; instead use AEMApplication -eventWith... methods.
 */

@interface AEMEvent : NSObject {
	AppleEvent *event;
	id codecs;
	AEMSendProcPtr sendProc;
	// type to coerce returned value to before unpacking it
	DescType resultType;
	AEMUnpackFormat resultFormat;
}

/*
 * Note: new AEMEvent instances are constructed by AEMApplication objects; 
 * clients shouldn't instantiate this class directly.
 */

- (id)initWithEvent:(AppleEvent *)event_
			 codecs:(id)codecs_
		   sendProc:(AEMSendProcPtr)sendProc_;

/*
 * Get codecs object used by this AEMEvent instance
 */
 - (id)codecs;

/*
 * Get a pointer to the AEDesc contained by this AEMEvent instance
 */
- (const AppleEvent *)aeDesc;

/*
 * Get an NSAppleEventDescriptor instance containing a copy of this event
 */
- (NSAppleEventDescriptor *)descriptor;

// Pack event's attributes and parameters, if any.

- (void)setAttribute:(id)value forKeyword:(AEKeyword)key;

- (void)setParameter:(id)value forKeyword:(AEKeyword)key;

// Get event's attributes and parameters.

- (id)attributeForKeyword:(AEKeyword)key type:(DescType)type error:(NSError **)error;

- (id)attributeForKeyword:(AEKeyword)key; // shortcut for above

- (id)parameterForKeyword:(AEKeyword)key type:(DescType)type error:(NSError **)error;

- (id)parameterForKeyword:(AEKeyword)key; // shortcut for above

// Specify an AE type to coerce the reply descriptor to before unpacking it.
// (Default = unpack as typeWildCard)

- (void)setUnpackFormat:(AEMUnpackFormat)format_ type:(DescType)type_;

- (void)getUnpackFormat:(AEMUnpackFormat *)format_ type:(DescType *)type_;

/*
 * Send event.
 
 * Parameters
 *
 * sendMode
 *    kAEWaitReply
 *
 * timeoutInTicks
 *    kAEDefaultTimeout
 *
 * error
 *    On return, an NSError object that describes an Apple Event Manager or application
 *    error if one has occurred, otherwise nil. Pass nil if not required.
 *
 * Return value
 *
 *    The value returned by the application, or an NSNull instance if no value was returned,
 *    or nil if an error occurred.
 *
 * Notes
 *
 *    A single event can be sent more than once if desired.
 *
 */

- (id)sendWithMode:(AESendMode)sendMode timeout:(long)timeoutInTicks error:(NSError **)error;

// shortcuts for -sendWithMode:timeout:error:

- (id)sendWithError:(NSError **)error;

- (id)send;

@end

