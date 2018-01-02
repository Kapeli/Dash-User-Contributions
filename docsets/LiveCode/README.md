
LiveCode Docset
=======================


Complete Dash compatible version of the LiveCode API and Guides.

**Author:** [James Hale](https://github.com/jameshale)

## Description
The 9 release of LC is going through quite a reorganisation with respect to the documentation format and arrangement. 

However each entry within the 
documentation clearly states with the version of LC from which it applies as well as the Edition (Community, Community Plus, Indy or Business) of LC to which it applies. 

This documentation set will be updated with each release of the LC 9 dp series.

It will also be updated for bug fixes (mainly in formatting) as they become know to me.

The current version(1.4) has been compiled from the 9 Dp11 release using "Make docset" V2.2" (see below)
 Hopefully this now captures all entries associated with libraries and widgets. 

## To generate your own docset

### Requirements


Copy of the [Make docset](http://livecodeshare.runrev.com/stack/845/Make-DocSet) stack

(Also available via "Sample Stacks" from within LiveCode.)

Copy of [LiveCode](http://downloads.livecode.com/livecode/) (Version 8.1.5 or higher, I suggest you use the very latest release whether dp or rc as these will have the most up to date documentation resources.)



### Instructions
Simply run the stack (instructions included) within LiveCode. Once completed a "LiveCode.docset" will be available to import into Dash.

### Note
The current docset version was ran against LC 9 dp11. There are still some anomalies with the docs. Properties and messages associated with the android native button and field as well as the iOS button are incorrectly typed as widgets. They thus appear under the widget category.

Please report any discrepancies or misiing items.