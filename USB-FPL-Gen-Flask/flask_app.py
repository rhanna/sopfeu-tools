import os
import io
import csv
import time
import json
import timeago
from datetime import datetime

from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, Response
from werkzeug.utils import secure_filename

DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
PATS_JOUR_FILENAME = 'data/pats_jour.json'
PATS_REF_FILNAME = 'data/pats_ref.json'

app = Flask(__name__)
app.secret_key = "jhasfdiuwaertyiujdksa"

@app.route('/', methods=['GET', 'POST'])
def home():
	if request.method == 'POST':
		return process_upload()

	pats_jour = read_pats_jour()
	pats_ref = read_pats_ref()

	return render_template( 'index.html',
	                        pats_jour = format_patrols( pats_jour ),
	                        pats_ref = format_patrols( pats_ref ) )

@app.route('/patrol/<patName>')
def patrol(patName):
	patrols = {}
	if patName.endswith( 'M' ):
		patrols = read_pats_jour()
	else:
		patrols = read_pats_ref()

	for p in patrols['patrols']:
		if p['patName'] == patName:
			patrol = p
			patrols['last_updated'] = patrols['last_updated']
			request_meta = { 'Content-Type': 'application/octet-stream', 'Content-Disposition': "attachment;filename=\"%s.FPL\"" % patName }
			#request_meta = { 'Content-Type': 'application/xml' }
			return render_template( 'patrol.html', patrol = patrol ), 200, request_meta

	flash( "Error! Patrol %s does not exist" % patName, 'danger' )
	return redirect('/')

def read_pats_jour():
	pats_jour = {}
	if os.path.isfile( PATS_JOUR_FILENAME ):
		with open(PATS_JOUR_FILENAME, 'r') as f:
			pats_jour = json.load(f)
	return pats_jour

def read_pats_ref():
	pats_ref = {}
	if os.path.isfile( PATS_REF_FILNAME ):
		with open(PATS_REF_FILNAME, 'r') as f:
			pats_ref = json.load(f)
	return pats_ref

def process_upload():
	# check if the post request has the file part
	if 'file' not in request.files:
		flash( 'No file part', 'danger' )
		return redirect(request.url)

	file = request.files['file']

	# if user does not select file, browser also submit an empty part without filename
	if file.filename == '':
		flash('No selected file', 'danger')
		return redirect(request.url)

	# if user uploads an illegal file name, reject
	if not allowed_file(file):
		flash('Uploaded file is not a patrols file (PATRJOUR.TXT / PATSORG.TXT) or a fires file (FEUX.DAT). Please upload a valid file.', 'danger')
		app.logger.warning('There was an attempt to upload an invalid file with name %s' % file.filename )
		return redirect(request.url)

	# process file
	file_io = io.StringIO(file.stream.read().decode("UTF8"), newline="\n")
	if is_patrols_file(file):
		patrols = parse_patrol_file( file_io, file.filename )

		with open( pats_json_filename(file.filename), 'w') as f:
			json.dump(patrols, f, default = json_converter)

		flash( 'Successfully processed file %s' % file.filename, 'success' )

		#html_out = generate_html_file( patrols )
		#return json.dumps(patrols, default = json_converter)
		#return render_template( 'index.html', patrols = format_patrols( patrols ) )
		return redirect(request.url)
	elif is_fires_file(file):
		flash( 'Feature not implemented yet!', 'warning' )
		return redirect(request.url)
	else:
		flash( 'Unexpected condition on file name %s' % file.filename, 'danger' )
		return redirect(request.url)

def pats_json_filename(filename):
	if filename == 'PATSJOUR.TXT':
		return PATS_JOUR_FILENAME
	elif filename == 'PATSORG.TXT':
		return PATS_REF_FILNAME
	else:
		raise Exception("Unexpcted file name " % filename)

def format_patrols( patrols ):
	if not patrols:
		return patrols

	patrols['last_updated_ago'] = timeago.format( datetime.strptime( patrols['last_updated'], DATE_TIME_FORMAT ), datetime.now(), 'fr' )
	for patrol in patrols['patrols']:
		patCoordinates = ""
		for wayPoint in patrol['patWayPoints']:
			patCoordinates += f"{wayPoint[0]}/{wayPoint[1]} "
		patrol['patCoordinates'] = patCoordinates
	return patrols

def parse_patrol_file(inFile, patrol_file_name):

	app.logger.info( f"Parsing file {patrol_file_name}" )
	startTime = datetime.now()

	fileReader = csv.reader(inFile)

	pat_name_suffix = ''
	if ( patrol_file_name == "PATSJOUR.TXT" ) :
		pat_name_suffix = 'M'

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

		patrols.append( { 'patName' : patName, 'patSize': patSize, 'patWayPoints': patWayPoints } )

		patCount += 1

	# Calculate the amount of time the script ran.
	duration = datetime.now() - startTime

	app.logger.info( f"Processed {(patCount - 1)} patrols in {duration}" )

	return { 'last_updated': datetime.now(), 'patrols': patrols }

def parse_patrol(patName, patSize, patrol):
	app.logger.debug( f"Parsing Patrol {patName} ({patSize} Waypoints)" )

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

def json_converter(o):
	if isinstance(o, datetime):
		return o.strftime( DATE_TIME_FORMAT )
 
def is_patrols_file(file):
	return file.filename in { 'PATSJOUR.TXT', 'PATSORG.TXT' }

def is_fires_file(file):
	return file.filename in { 'FEUX.DAT' }

def allowed_file(file):
	return is_patrols_file(file) or is_fires_file(file)

if __name__ == '__main__':
	app.run( debug = True, host= '0.0.0.0' )
