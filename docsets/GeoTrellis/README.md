# [GeoTrellis](http://geotrellis.io) Docset

### Author

- Teo Stocco
	- [Github](https://github.com/zifeo)

### Instructions

- prerequisites
	- cross project documentation generator (*Intellij IDEA* or *[sbt-unidoc](https://github.com/sbt/sbt-unidoc)*)
	- *[mkscaladocset](https://bitbucket.org/inkytonik/mkscaladocset)* (requires *greadlink* and *make*)
- steps
	- generate full scaladoc
	- use *mkscaladocset* (do not forget to call `make` before) to create a docset: `mkScalaDocset GeoTrellis scaladoc-path/ icon=this-folder-path/icon.png`
	- follow other intructions on this main repo `README.md` file
- notes
	- there might be parsing errors but they can easily be removed by changing `name='<span class="name"><a href="RegionGroupOptions$.html">RegionGroupOptions.default.connectivity</a></span>'` to `name="RegionGroupOptions.default.connectivity"` in each of the following scaladoc files
		- `geotrellis/raster/op/global/GlobalMethods.html`
		- `geotrellis/raster/op/global/package$$GlobalMethodExtensions.html`
		- `geotrellis/raster/op/global/ToVector$.html`

### Various

Additional documentation (i.e. exemples and code-through) can be found [here](http://geotrellis.io/geotrellis-docs/).

As the project is moving forward fast, please get support and report bugs [here](https://github.com/geotrellis/geotrellis/issues). 
