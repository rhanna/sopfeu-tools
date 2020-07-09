from datetime import datetime
from flask import Flask
from flask import render_template

app = Flask( __name__ )

@app.route('/hello/<name>')
def hello_name( name ):
	timestamp = datetime.now().strftime( "%A, %B %d %Y %I:%M%p" )
	return render_template( 'index.html', name = name, timestamp = timestamp )

if __name__ == '__main__':
	app.run( debug = True )

