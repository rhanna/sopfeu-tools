
#Description
Tools to generate raster map layer for SOPFEU grid and labels.
The tool generates a file in the MBTiles format which can be directly imported into ForeFlight.

#External dependencies
	- ImageMagick
	- Docker

#How it works :
	1. Generate a blank canvas in TIFF format
	2. Using the list of cells in the file grid.csv it draws a rectangle and a lebsl for each cell using ImageMagick
	3. Using GDal (running inside a docker containr), it adds geo-tagging to the TIFF.
	4. Using GDal (in docker), it converts the geo-tagged TIFF to MBTiles format

#To run :

	- php generate.grid.php

	- Rename the output.mbtiles file to something more useful and copy it to ForeFlight
