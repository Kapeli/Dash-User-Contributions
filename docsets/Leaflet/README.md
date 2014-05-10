leaflet-docset
==============

Documentation for the [Leaflet](http://leafletjs.com/) JavaScript map library in the Dash [docset](http://kapeli.com/docsets) format, ready for offline reading and searching. For source, see https://github.com/drewda/leaflet-docset

To Generate Docs
----------------
The docs are copied from the Leaflet site and indexed using a Ruby script. To set up and run the Ruby script:

````   
   git clone git@github.com:drewda/leaflet-docset.git
   cd leaflet-docset
   bundle install
   rake
   
````

Future Improvements
-------------------
[ ] The [classification of sections](https://github.com/drewda/leaflet-docset/blob/master/Rakefile#L80-110) (into class, method, interface, etc.) is fast and loose. It could use improvement.
