<?
	// Global Parameters
	$baseLat  = -80;
	$baseLong = 44;
	$sepW = 100;
	$sepH = 150;
	$gridW = 100 * $sepW; 		// pixels
	$gridH = 52 * $sepH; 		// pixels
	$canvasW = $gridW + 1;
	$canvasH = $gridH + 1;

	// Read CSV file and determine grid to generate
	$aGrid = array();
	if (($handle = fopen("grid.csv", "r")) !== FALSE) {
		$row = 1;
	    while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
	    	// num fields in line
	        $num = count($data);
	        $row++;
	        for ($c=0; $c < $num; $c++) {
	        	if ( ! empty( $data[$c] ) ) {
	            	$aGrid[] = $data[$c];
	            }
	        }
	    }
	    fclose($handle);
	}
	sort($aGrid);

	/* 
	W = 25 degrees = 100 15-min grids
	H = 10 degrees = 52  15-min grids
	Grid is 100x50
	Image is factored at 100x = 10000x5000
	Add 1 pixel to get the bounding box all the way around
	*/

	//./grid -s 100 -o 0.7 -c "#FF0000" base.tiff grid.tiff

	for ( $i = 0 ; $i < count($aGrid) ; $i++ )
	{
		/*
		$qLat  = $baseLat  + ( ( $xOffset - 1 ) * $gridW );
		$qLong = $baseLong + ( ( $yOffset - 1 ) * $gridH );

		$qLeft   = $qLat;
		$qMidH   = $qLat + ( $gridW / 2 );
		$qRight  = $qLeft + $gridW;
		$qBottom = $qLong;
		$qMidV   = $qLong + ( $gridW / 2 );
		$qTop    = $qLong + $gridH;

		// Coordinates
		$cBL = "$qLeft,$qBottom";
		$cBR = "$qRight,$qBottom";
		$cTR = "$qRight,$qTop";
		$cTL = "$qLeft,$qTop";

		// Middle Point
		$cMM = "$qMidH,$qMidV";
		*/
		
		$rect = $aGrid[$i];

		$xOffset = substr($rect, 0, 2);
		$yOffset = substr($rect, 2, 2);

		$left   = 1 + ( $xOffset - 1 ) * $sepW;
		$right  = $left + $sepW;
		$top    = $canvasH - ( ( $yOffset ) * $sepH );
		$bottom = $top + $sepH;

		$rectUpperLeft  = "$left,$top";
		$rectUpperRight = "$right,$top";
		$rectLowerRight = "$right,$bottom";
		$rectLowerLeft  = "$left,$bottom";

		// Generate draw string for ImageMagick for the grid
		//$drawStr = "$drawStr rectangle $rectUpperLeft $rectLowerRight";
		$drawStr = "$drawStr M $rectUpperLeft L $rectUpperRight L $rectLowerRight L $rectLowerLeft L $rectUpperLeft";

		$textLeft  = $left + 5;
		$textRight = $top + 20;
		$textStr   = "$textStr text $textLeft,$textRight '$rect'";

		echo "$rect $xOffset $yOffset $left $right $top $bottom \n";
	}

	$opacity = "0.5";
	$gridColor = "#008C8C";
	$textColor = "#FF0000";
	$strokewidth = "3";

	// Generate blank canvas each 100x100 rect represents one grid square
	// The entire canvas maps to the latitudes -80 to -55 and longitude 44 to 57
	echo "Generating blank canvas ...\n";
	$cmd = "convert -size " . $canvasW . "x" . $canvasH . " canvas:none canvas.tiff\n";
	`$cmd`;

	echo "Generating grid ...\n";
	$cmd = "convert canvas.tiff -fill none -stroke \"$gridColor\" -strokewidth $strokewidth -draw \"stroke-opacity $opacity path '$drawStr'\" grid.tiff";
	`$cmd`;

	echo "Generating labels ...\n";
	$cmd = "convert grid.tiff -font Palatino-Roman -pointsize 20 -fill \"$textColor\" -draw \"$textStr\" label.tiff";
	`$cmd`;

	echo "Bounding Box for MapTiler = -80 44 -55 57 \n";

	//$dockerCommands .= "!/bin/sh \n";
	$dockerCommands .= "gdal_translate -a_nodata 0 -of GTiff -a_Srs EPSG:4326 -a_ullr -80 57 -55 44 label.tiff label-geo.tiff \n";
	$dockerCommands .= "gdalinfo label-geo.tiff \n";
	$dockerCommands .= "rm output.mbtiles 2>/dev/null \n";
	$dockerCommands .= "gdal_translate label-geo.tiff output.mbtiles -of MBTILES \n";
	$dockerCommands .= "gdaladdo -r average output.mbtiles 2 4 8 16 32 \n";

	file_put_contents( "docker-exec.sh", $dockerCommands );
	`chmod a+x docker-exec.sh`;

	//$cmd = "eval $(docker-machine env default); docker run --rm -v \$(pwd):/data -w /data/ --entrypoint /data/docker-exec.sh joeakeem/gdal2mbtiles";
	$cmd = "eval $(docker-machine env default); docker run --rm -it -v \$(pwd):/data -w /data/ osgeo/gdal:alpine-small-latest /bin/sh /data/docker-exec.sh";
	echo `$cmd`;
