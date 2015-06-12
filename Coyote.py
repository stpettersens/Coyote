#!/usr/bin/env python
"""
Coyote

A simple web server for serving static content with 
supported MIME types and headers configured via XML.

Copyright (c) 2015 Sam Saint-Pettersen.
Released under the MIT/X11 License.

Use -h switch for usage information.
"""
import sys
import argparse
import datetime
from os import path, curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import xml.etree.ElementTree as ET

# This class handles the web serving.
class Coyote:

	stderr = False # Use stdout by default, rather than stderr.
	verbose = False # Not verbose by default.
	webserver_str = 'Coyote/1.0' # Short identifier for web server.
	exts = [] # List for file extensions.
	mimes = [] # List for MIME types.
	descs = [] # List for file descriptions.
	headers = [] # List for optional headers.

	def __init__(self, directory, port, verbose, version, info, stderr, mimes, headers):
		if len(sys.argv) == 1 or info:
			print(__doc__) # Display program information.
		elif version:
			print(Coyote.webserver_str) # Print web server string, which conains version (1.0).
		else:
			if verbose: Coyote.verbose = True # Set to be verbose.
			if port == None: port = 80 # Use port 80 when port is unspecified.
			if mimes == None: mimes = 'mimes.xml' # Default mimes configuration is mimes.xml
			if headers == None: headers = 'headers.xml' # Default headers configuration is...
			# headers.xml
			self.loadMimes(mimes)
			self.loadHeaders(headers)
			self.serve(directory, port)

	# Load MIME types.
	def loadMimes(self, mimes_file):
		if path.isfile(mimes_file):
			tree = ET.parse(mimes_file)
			root = tree.getroot()
			for child in root.findall('mime'):
				Coyote.exts.append(child.get('ext'))
				Coyote.mimes.append(child.get('type'))
				Coyote.descs.append(child.find('description').text)
		else:
			print('MIMES file required ({0}). Not found.'.format(mimes_file))
			sys.exit(1)

	# Load optional response headers.
	def loadHeaders(self, headers_file):
		if path.isfile(headers_file):
			tree = ET.parse(headers_file)
			root = tree.getroot()
			for child in root.findall('header'):
				Coyote.headers.append('{0}-->{1}'.format(child.get('name'), child.get('value')))

	# Serve content forever.
	def serve(self, directory, port):
		try:
			if directory == None: directory = ''
			server = HTTPServer(('', int(port)), CoyoteHandler)
			_print('Started {0} at {1}.\nServing /{2}...'.format(
				Coyote.webserver_str, 
				datetime.datetime.now(),
				directory
			))
			server.serve_forever()
		except KeyboardInterrupt:
			_print('^C received. Terminating the server...')
			server.socket.close()
			sys.exit(0)

class CoyoteHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			self.send_response(200);
			self.send_header('Server', Coyote.webserver_str)

			# Load optional headers.
			for header in Coyote.headers:
				h = header.split('-->')
				self.send_header(h[0], h[1])

			root, ext = path.splitext(self.path)
			i = 0
			if ext in Coyote.exts:
				i = Coyote.exts.index(ext)

			if self.path.endswith(Coyote.exts[i]):
					f = open(curdir + sep + self.path)
					self.send_header('Content-type', Coyote.mimes[i])
					self.end_headers()
					self.wfile.write(f.read())
					f.close()
					return

			elif self.path.startswith('/'):
					f = open(curdir + sep + 'index.html');
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					self.wfile.write(f.read())
					f.close()
					return

			return

		except IOError:
			self.send_error(404, 'File not found: {0}'.format(self.path))

# Print to stdout or stderr as applicable.
def _print(message):
	if Coyote.stderr and Coyote.verbose:
		sys.stderr.write(message + '\n')
	
	elif Coyote.verbose:
		print(message)

# Handle any command line arguments.
parser = argparse.ArgumentParser(description='Coyote: A simple web server for serving static'
+ ' content with supported MIME types and headers configured via XML.')
parser.add_argument('-d', '--directory', action='store', dest='directory', metavar="DIRECTORY")
parser.add_argument('-p', '--port', action='store', dest='port', metavar="PORT")
parser.add_argument('-l', '--verbose', action='store_true', dest='verbose')
parser.add_argument('-v', '--version', action='store_true', dest='version')
parser.add_argument('-i', '--info', action='store_true', dest='info')
parser.add_argument('-s', '--std-err', action='store_true', dest='stderr')
parser.add_argument('-m', '--mimes', action='store', dest='mimes', metavar="MIMES")
parser.add_argument('-x', '--headers', action='store', dest='headers', metavar="HEADERS")
argv = parser.parse_args()

Coyote(argv.directory, argv.port, argv.verbose, argv.version, argv.info, argv.stderr, 
argv.mimes, argv.headers)
