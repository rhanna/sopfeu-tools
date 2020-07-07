
#Description
SOPFEU USB Key to Flight Plan Generator
This tool converts the data files from the SOPFEU USB key into the FPL file format for import into Flight Planning software such as ForeFlight. The FPL files are uploaded to a publicly accessible Amazon S3 bucket for import / download.

#External dependencies
	- Python 3.7
	- Docker

#How it works
	1. Obtain the latest data files by using the USB Updater tool from the SOPFEU (or any other means)
	2. Upload the data files to an Amazon S3 bucket
	3. An Amazon Lambda function automatically gets triggered when the upload is performed.
	4. The file is processed and converted to individual .FPL files per patrol.
	5. The files are uploaded to the publicly accessible bucket

#How to Setup

	- Install Python 3.7
	- python3 -m pip install virtualenv
	- cd USB-FPL-Generator
	- create and initialize a virtual environment called venv:
		- python3 -m virtualenv venv

#To Build the Tool

Enter the following command to activate the virtual environment
	- source venv/bin/activate
	- pip3 install s3fs s3transfer
	- deactivate
	- cd venv/lib/python3.7/site-packages
	- zip -r ../../../../sopfeu-python-libs.zip dateutil docutils jmespath s3fs s3transfer fsspec six.py
	- cd -
	- 

#To Run and Test Locally

python3 -c "from generate import process_local ; process_local();"

#References

https://docs.aws.amazon.com/pinpoint/latest/developerguide/tutorials-importing-data-create-python-package.html
