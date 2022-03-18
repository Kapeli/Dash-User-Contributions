Hammerspoon
===========

### Project Page

https://github.com/Hammerspoon

### Docset generation

git clone git://github.com/Hammerspoon/hammerspoon
cd hammerspoon/scripts/docs/
bundle install
cd ..
make docs

this will trigger various scripts in the scripts/docs/bin directory to extract documentation from the source code, convert it into a json object, then render it as html.
