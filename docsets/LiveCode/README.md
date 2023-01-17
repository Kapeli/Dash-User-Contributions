
LiveCode Docset
=======================


Complete Dash compatible version of the LiveCode API and Guides.

**Author:** [James Hale](https://github.com/jameshale)

## Description

Fixes a regression (not sure when this happened) where the image files for the guide docs were not copied due to an unannounced chage in the documentation structure within the  LiveCode package.

The 10.0.0 dp4 release of LC has a few dictionary updates. This version of the documentation includes these updates.

Each entry within the 
documentation clearly states with the version of LC from which it applies. 

This documentation set will be updated with each release of the LC 10 series where a significant documentation change occurs.

It will also be updated for bug fixes (mainly in formatting) as they become know to me.

The current version(2.1.0) has been compiled from the 10.0.0 dp4 using "Make docset V3.8" (see below)

Please report any discrepancies or omissions in the DocSet relative to the dictionary included with LiveCode to me.

Please report any errors or omissions in the actual docs to [Livecode](https://quality.livecode.com).


## To generate your own docset

### Requirements


Copy of the [Make docset](http://livecodeshare.runrev.com/stack/845/Make-DocSet) stack

(Also available via "Sample Stacks" from within LiveCode.)

Copy of [LiveCode](http://downloads.livecode.com/livecode/) (Version 9.6.8 or higher, I suggest you use the very latest release whether dp or rc as these will have the most up to date documentation resources.)



### Instructions
Simply run the stack (instructions included) within LiveCode. Once completed a "LiveCode.docset" will be available for import into Dash.

### Note
The current docset version was ran against LC10.0.0 dp4 
Documentation for LiveCode is continually being updated. As such there may still be some failings in the docs or some other type of error.

