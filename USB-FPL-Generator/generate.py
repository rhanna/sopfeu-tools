import io
import os
import csv
import time
import s3fs
from datetime import datetime

#input_archive_folder = "input_archive"
#to_process_folder = "to_process"

# S3 bucket info
s3 = s3fs.S3FileSystem(anon=False)

def lambda_handler(event, context):
	log1("Received event: \n" + str(event))

	for record in event['Records']:
		bucket = record['s3']['bucket']['name']
		key = record['s3']['object']['key']
		input_file = os.path.join(bucket,key)
		
		#print(f"File = {input_file}")
		#return

		#archive_path = os.path.join(bucket,input_archive_folder,os.path.basename(key))
		#folder =  os.path.split(key)[0]
		#s3_url = os.path.join(bucket,folder)
		#output_file_template = os.path.splitext(os.path.basename(key))[0] + "__part"
		#output_path = os.path.join(bucket,to_process_folder)

		patrols = []
		#patrols += parse_patrol_file( s3.open( os.path.join( bucket, 'PATSORG.TXT'), 'r'), key )
		#patrols += parse_patrol_file( s3.open( os.path.join( bucket, 'PATSJOUR.TXT'), 'r'), key )
		patrols += parse_patrol_file( s3.open( input_file, 'r'), key )
		generate_html_file( s3.open( os.path.join( bucket, 'index.html' ), 'w'), patrols )

		# Send the unchanged input file to an archive folder.
		#archive(input_file,archive_path)

	    #return {
	    #	'statusCode': 200,
	    #	'body': json.dumps('Hello from Lambda!')
    	#}


# Move the original input file into an archive folder.
#def archive(input_file, archive_path):
#    s3.copy_basic(input_file,archive_path)
#    print("Moved " + input_file + " to " + archive_path)
#    s3.rm(input_file)

def process_local():
	patrols = []
	patrols += parse_patrol_file( open('PATSORG.TXT', 'r', newline='', encoding='utf-8-sig'),  '')
	patrols += parse_patrol_file( open('PATSJOUR.TXT', 'r', newline='', encoding='utf-8-sig'),  'M')
	#log1( f"{patrols}")
	generate_html_file( open("out/index.html", 'w', newline="\n", encoding='utf-8-sig'), patrols)

def parse_patrol_file(input_file, pat_name_suffix):
	startTime = datetime.now()

	log1( f"Parsing file {input_file}" )
	with input_file as inFile:
		fileReader = csv.reader(inFile)

		patCount=0
		patrols = []
		for row in fileReader:
			# Sleep to prevent throttling errors.
			time.sleep(.025)

			#print(row)

			patrolRaw = row
			patName = patrolRaw[0] + pat_name_suffix
			patSize = ( len(patrolRaw) - 1 ) // 2
			patWayPoints = parse_patrol(patName, patSize, patrolRaw)

			patrols.append( [ patName, patSize, patWayPoints ])

			patCount += 1

	# Calculate the amount of time the script ran.
	duration = datetime.now() - startTime

	# Print the number of records processed. Subtract 1 to account for the header.
	log1( f"Processed {(patCount - 1)} patrols in {duration}" )

	# Delete the input file
	#s3.rm(input_file)

	return patrols

def parse_patrol(patName, patSize, patrol):
	log2( f"Parsing Patrol {patName} ({patSize} Waypoints)" )

	p = 1
	wayPoints = []
	while p < patSize * 2:
		wpLat = patrol[p]
		wpLong = patrol[p+1]
		wayPoint = [wpLat,wpLong]
		wayPoints.append( wayPoint )
		p += 2
	# Add first wayPoint to end of patrol
	wayPoints.append( wayPoints[0] )

	return wayPoints

def generate_html_file( output_file, patrols ):
	log2( f"Generating HTML File for ")


	htmlHeader = """
	<!doctype html>
	<html lang="en">
	  <head>
	    <!-- Required meta tags -->
	    <meta charset="utf-8">
	    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

	    <!-- Bootstrap CSS -->
	    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">

		<title>SOPFEU Patrouilles</title>

  	  </head>
	  <body>

		<div class="container">
		  <!-- Content here -->
			<table class="table">
			  <thead>
			    <tr>
			      <th scope="col">#</th>
			      <th scope="col">Patrol</th>
			      <th scope="col"># WPs</th>
			      <th scope="col">WayPoints</th>
			      <th scope="col">FPL File</th>
			    </tr>
			  </thead>
			  <tbody>
	"""

	htmlFooter = """
			  </tbody>
			</table>
		</div>

	    <!-- Optional JavaScript -->
	    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
	    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
	    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
	    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
	  </body>
	</html>
	"""
	with output_file as outFile:
		outFile.write( htmlHeader )

		patCount = 1
		for patrol in patrols:
			patName = patrol[0]
			patSize = patrol[1]
			patWayPoints = patrol[2]

			patCoordinates = "<figure class=\"highlight\"><pre><code class=\"language-html\" data-lang=\"html\">"
			for wayPoint in patWayPoints:
				patCoordinates += f"{wayPoint[0]}/{wayPoint[1]} "
			patCoordinates += "</code></pre></figure>"
			outFile.write( f"<tr><th scope=\"row\">{patCount}</th><td>{patName}</td><td>{patSize}</td><td>{patCoordinates}</td><tr>" )
			patCount += 1

		outFile.write( htmlFooter )

def log1(msg):
	log( "* ", msg )

def log2(msg):
	log( "** ", msg )

def log(prefix, msg):
	print( prefix + msg )

#process()
