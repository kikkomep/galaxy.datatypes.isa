# galaxy.datatypes.isa #

This repository supports both ISA-Tab and ISA-JSON data formats as Galaxy datatypes.

### How to install? ###

* Add the following lines to the `datatypes_conf.xml` configuration file:

	- as child of the `datatypes > registration` tag:

		```xml 
		<datatype extension="isa" type="galaxy.datatypes.isa:Isa" mimetype="application/isa-tools"
		                  display_in_upload="true" description="ISA data type." description_url="https://isa-tools.org"/>
		```	
	- as child of the `datatypes > sniffers` tag:

		```xml
<sniffer type="galaxy.datatypes.isa:Isa"/>
```


### Copyrights ###

Code and documentation Copyright © 2017, [CRS4](http://www.crs4.it). 
Code released under the [MIT license](https://opensource.org/licenses/mit-license.php).