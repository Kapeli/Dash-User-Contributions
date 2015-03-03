WaxSealCore [![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/TongG/WaxSealCore?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
===========

### What's WaxSealCore

WaxSealCore is a modern and full feature Objective-C wrapper for Keychain Services [*Keychain Services*](https://developer.apple.com/library/mac/documentation/Security/Reference/keychainservices/index.html) API.

### Why WaxSealCore

Computer users typically have to manage multiple accounts that require logins with user IDs and passwords. Secure FTP servers, database servers, secure websites, instant messaging accounts, and many other services require authentication before they can be used. Users often respond to this situation by making up very simple, easily remembered passwords, by using the same password over and over, or by writing passwords down where they can be easily found. Any of these cases compromises security.

The *Keychain Services* API provides a solution to this problem. By making a single call to this API, an application can store login information on a keychain where the application can retrieve the information—also with a single call—when needed. A **keychain** is an encrypted container that holds passwords for multiple applications and secure services. Keychains are secure storage containers, which means that when the keychain is locked, no one can access its protected contents. In OS X, users can unlock a keychain—thus providing trusted applications access to the contents—by entering a single master password.

*Keychain Services* is powerful, **HOWEVER**:

 * *Keychain Services*'s API is pure C, it's very ugly and hard to use
 * *Keychain Services* doesn't support Unicode
 * *Keychain Services* is based on *Core Foundation*, so you have to manage memory manually
 * The Apple official documentation of *Keychain Services* is **old** and **riddled with errors**

we need a OOP wrapper of this API to make life easier. There are some repos about this, like [EMKeychain](https://github.com/irons/EMKeychain) and [SSKeychain](https://github.com/soffes/sskeychain). I admit, they are cool. But they aren't **full feature** (in other words, too simple). We need a full feature wrapper of *Keychain Services* which can create and delete a keychain or passphrase item quickly, while can also take advantage of the advanced feature of *Keychain Services* such as **Access Control List**. Therefore, I wrote WaxSealCore.

### Comparison Between Keychain Services and WaxSealCore

**Create an empty keychain with given passphrase:**

* using pure C API of *Keychain Services*:

```objective-c
OSStatus resultCode = errSecSuccess;
SecKeychainRef secEmptyKeychain = NULL;
NSURL* URL = [ [ [ NSBundle mainBundle ] bundleURL ] URLByAppendingPathComponent: @"EmptyKeychainForWiki.keychain" ];
char* passphrase = "waxsealcore";

// Create an empty keychain with given passphrase
resultCode = SecKeychainCreate( URL.path.UTF8String
                              , ( UInt32 )strlen( passphrase )
                              , ( void const* )passphrase
                              , ( Boolean )NO
                              , NULL
                              , &secEmptyKeychain
                              );

NSAssert( resultCode == errSecSuccess, @"Failed to create new empty keychain" );

resultCode = SecKeychainDelete( secEmptyKeychain );
NSAssert( resultCode == errSecSuccess, @"Failed to delete the given keychain" );

if ( secEmptyKeychain )
    // Keychain Services is based on Core Foundation,
    // you have to manage the memory manually
    CFRelease( secEmptyKeychain );
```

* using *WaxSealCore*:

```objective-c
NSError* error = nil;

// Create an empty keychain with given passphrase
WSCKeychain* emptyKeychain = [ [ WSCKeychainManager defaultManager ]
    createKeychainWithURL: [ [ [ NSBundle mainBundle ] bundleURL ] URLByAppendingPathComponent: @"EmptyKeychainForWiki.keychain" ]
               passphrase: @"waxsealcore"
           becomesDefault: NO
                    error: &error ];
                           
// You have no need for managing the memory manually,
// emptyKeychain will be released automatically.
```

**Find the following Internet passphrase then print its Account Name, Passphrase and Comment**

<img src="http://i.imgbox.com/eeiU5Ymr.png" title="IMDb Passphrase" border="0" height="498" width="501" />

* using pure C API of *Keychain Services* (OMG! Give me a break!😲🔫):

```objective-c
OSStatus resultCode = errSecSuccess;

// Attributes that will be used for constructing search criteria
char* label = "secure.imdb.com";
SecProtocolType* ptrProtocolType = malloc( sizeof( SecProtocolType ) );
*ptrProtocolType = kSecProtocolTypeHTTPS;

SecKeychainAttribute attrs[] = { { kSecLabelItemAttr, ( UInt32 )strlen( label ), ( void* )label }
                               , { kSecProtocolItemAttr, ( UInt32 )sizeof( SecProtocolType ), ( void* )ptrProtocolType }
                               };

SecKeychainAttributeList attrsList = { sizeof( attrs ) / sizeof( attrs[ 0 ] ), attrs };

// Creates a search object matching the given list of search criteria.
SecKeychainSearchRef searchObject = NULL;
if ( ( resultCode = SecKeychainSearchCreateFromAttributes( NULL
                                                         , kSecInternetPasswordItemClass
                                                         , &attrsList
                                                         , &searchObject
                                                         ) ) == errSecSuccess )
    {
    SecKeychainItemRef matchedItem = NULL;

    // Finds the next keychain item matching the given search criteria.
    while ( ( resultCode = SecKeychainSearchCopyNext( searchObject, &matchedItem ) ) != errSecItemNotFound )
        {
        SecKeychainAttribute theAttributes[] = { { kSecAccountItemAttr, 0, NULL }
                                               , { kSecCommentItemAttr, 0, NULL }
                                               };

        SecKeychainAttributeList theAttrList = { sizeof( theAttributes ) / sizeof( theAttributes[ 0 ] ), theAttributes };
        UInt32 lengthOfPassphrase = 0;
        char* passphraseBuffer = NULL;
        if ( ( resultCode = SecKeychainItemCopyContent( matchedItem
                                                      , NULL
                                                      , &theAttrList
                                                      , &lengthOfPassphrase
                                                      , ( void** )&passphraseBuffer
                                                      ) ) == errSecSuccess )
            {
            NSLog( @"\n==============================\n" );
            NSLog( @"Passphrase: %@", [ [ [ NSString alloc ] initWithBytes: passphraseBuffer length: lengthOfPassphrase encoding: NSUTF8StringEncoding ] autorelease ] );

            for ( int _Index = 0; _Index < theAttrList.count; _Index++ )
                {
                SecKeychainAttribute attrStruct = theAttrList.attr[ _Index ];
                NSString* attributeValue = [ [ [ NSString alloc ] initWithBytes: attrStruct.data length: attrStruct.length encoding: NSUTF8StringEncoding ] autorelease ];

                if ( attrStruct.tag == kSecAccountItemAttr )
                    NSLog( @"IMDb User Name: %@", attributeValue );
                else if ( attrStruct.tag == kSecCommentItemAttr )
                    NSLog( @"Comment: %@", attributeValue );
                }

            NSLog( @"\n==============================\n" );
            }

        SecKeychainItemFreeContent( &theAttrList, passphraseBuffer );
        CFRelease( matchedItem );
        }
    }

if ( ptrProtocolType )
    free( ptrProtocolType );

if ( searchObject )
    CFRelease( searchObject );
```

* using *WaxSealCore* (Just a few lines of Objective-C code):

```objective-c
NSError* error = nil;

WSCPassphraseItem* IMDbLoginPassphrase = ( WSCPassphraseItem* )[ [ WSCKeychain login ]
    findFirstKeychainItemSatisfyingSearchCriteria: @{ WSCKeychainItemAttributeLabel : @"secure.imdb.com"
                                                    , WSCKeychainItemAttributeProtocol : WSCInternetProtocolCocoaValue( WSCInternetProtocolTypeHTTPS )
                                                    , WSCKeychainItemAttributeComment : @"👺👹👺👹"
                                                    }
                                        itemClass: WSCKeychainItemClassInternetPassphraseItem
                                            error: &error ];
                                            
// WaxSealCore supports Unicode-based search, so you can use Emoji or Chinese in your search criteria.
// One step. So easy, is not it?
```

Print its Account Name, Passphrase and Comment:

```objective-c
if ( IMDbLoginPassphrase )
    {
    NSLog( @"==============================" );
    // Use the `account` property
    NSLog( @"IMDb User Name: %@", IMDbLoginPassphrase.account );

    // Use the `passphrase` property
    NSLog( @"Passphrase: %@", [ [ [ NSString alloc ] initWithData: IMDbLoginPassphrase.passphrase encoding: NSUTF8StringEncoding ] autorelease ] );

    // Use the `comment` property
    NSLog( @"Comment: %@", IMDbLoginPassphrase.comment );
    NSLog( @"==============================" );

    // -setComment:
    IMDbLoginPassphrase.comment = @"👿👿👿👿👿👿";
    }
else
    NSLog( @"I'm so sorry!" );
```

Batch Search:

```objective-c
// Find all the Internet passphrases that met the given search criteria
NSArray* passphrases = [ [ WSCKeychain login ]
    // Batch search
    findAllKeychainItemsSatisfyingSearchCriteria: @{ WSCKeychainItemAttributeLabel : @"secure.imdb.com"
                                                   , WSCKeychainItemAttributeProtocol : WSCInternetProtocolCocoaValue( WSCInternetProtocolTypeHTTPS )
                                                   , WSCKeychainItemAttributeComment : @"👿👿👿👿👿👿"
                                                   }
                                       itemClass: WSCKeychainItemClassInternetPassphraseItem
                                           error: &error ];
if ( passphrases.count != 0 )
    {
    for ( WSCPassphraseItem* _Passphrase in passphrases )
        {
        NSLog( @"==============================" );
        NSLog( @"IMDb User Name: %@", IMDbLoginPassphrase.account );
        NSLog( @"Passphrase: %@", [ [ [ NSString alloc ] initWithData: IMDbLoginPassphrase.passphrase encoding: NSUTF8StringEncoding ] autorelease ] );
        NSLog( @"Comment: %@", IMDbLoginPassphrase.comment );
        NSLog( @"==============================" );

        _Passphrase.comment = @"👺👹👺👹";
        }
    }
else
    NSLog( @"I'm so sorry!" );
```

### Documentation

* [Read online](https://tongg.github.io/WaxSealCore-Doc)

* [Download the offline docset for Dash or Xcode Documentation Viewer](https://github.com/TongG/WaxSealCore-Doc)

### Minimum System Requirements

* Xcode 5.x or greater for compiling

* OS X 10.7 for compiling and running

### Contact Me
If you encounter any issue, you can: 

 * Email me: <Tong-G@outlook.com>
 * DM me on Twitter: [@NSTongG]( https://twitter.com/NSTongG )
 * If you are using S/MIME, you can send me encrypted email by retrieving my S/MIME certificate and its related intermediate certificates in [here](https://www.dropbox.com/sh/hicq0v0hhepqvdg/AAB7hLeZRg1XPw9cGea1rtkla?dl=0)
 * If you are using GnuPG, you can send me encrypted email, my GnuPG pub key is **0x5604FA90**, you can retrieve it from keyserver.

### License
> Copyright (c) 2015 Tong Guo

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
