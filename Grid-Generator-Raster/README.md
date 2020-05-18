
# Description
Tools to generate raster map layer for SOPFEU grid and labels.
The tool generates a file in the MBTiles format which can be directly imported into ForeFlight.

# External dependencies
	- ImageMagick
	- Docker

# How it works
	1. Generate a blank canvas in TIFF format
	2. Using the list of cells in the file grid.csv it draws a rectangle and a lebsl for each cell using ImageMagick
	3. Using GDal (running inside a docker containr), it adds geo-tagging to the TIFF.
	4. Using GDal (in docker), it converts the geo-tagged TIFF to MBTiles format

# To run

	- php generate.grid.php

	- Rename the output.mbtiles file to something more useful and copy it to ForeFlight

# References

https://imagemagick.org/script/convert.php
https://imagemagick.org/script/command-line-options.php#draw
https://www.maptiler.com/
https://qgis.org/en/site/forusers/alldownloads.html
http://www.fmwconcepts.com/imagemagick/grid/index.php
https://github.com/UrbanSystemsLab/raster-to-mbtiles
https://tilemill-project.github.io/tilemill/docs/mac-install/
https://github.com/ecometrica/gdal2mbtiles
https://github.com/mapbox/mapbox-studio-classic
https://github.com/joe-akeem/gdal2mbtiles-docker
https://github.com/ecometrica/gdal2mbtiles
https://gdal.org/programs/gdal_translate.html
https://gis.stackexchange.com/questions/159004/creating-geotiff-from-tiff-using-gdal
https://gis.stackexchange.com/questions/307933/how-to-create-geotiff-from-image-and-utm-coordinates
https://gdal.org/programs/gdaladdo.html
https://github.com/OSGeo/gdal/tree/master/gdal/docker
https://gdal.org/drivers/raster/mbtiles.html

