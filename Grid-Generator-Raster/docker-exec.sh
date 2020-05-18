gdal_translate -a_nodata 0 -of GTiff -a_Srs EPSG:4326 -a_ullr -80 57 -55 44 label.tiff label-geo.tiff 
gdalinfo label-geo.tiff 
rm output.mbtiles 2>/dev/null 
gdal_translate label-geo.tiff output.mbtiles -of MBTILES 
gdaladdo -r average output.mbtiles 2 4 8 16 32 
