#!/usr/bin/env python

import sys
import xml.etree.ElementTree
from xml.dom.minidom import parse, parseString
import xml.parsers.expat
import sys
from datetime import datetime, timedelta

xml_file1 = sys.argv[1]
xml_file2 = sys.argv[2]

class GPXParser:
	_data = {}
	_filename = None
	_current_element = None
	_current_datetime = None
	_current_datastring = ""

	def __init__(self, filename):
		self._data = {}
		self._filename = None
		self._current_element = None
		self._current_datetime = None
		self._current_datastring = ""
		self._filename = filename

	def parse(self):
		p = xml.parsers.expat.ParserCreate()
		p.StartElementHandler = self._start_element
		p.EndElementHandler = self._end_element
		p.CharacterDataHandler = self._char_data
		with open(self._filename, 'r') as f:
			p.ParseFile(f)
		return self._data

	def _start_element(self, name, attrs):
		self._current_element = name

	def _end_element(self, name):
		data = self._current_datastring.strip()

		if name == "time":
			if data:
				try:
					self._current_datetime = datetime.strptime(data, "%Y-%m-%dT%H:%M:%SZ")
				except ValueError:
					self._current_datetime = data
					print data

		if name == "tp1:hr":
			if data:
				self._data[self._current_datetime] = data

		self._current_datastring = ""

	def _char_data(self, data):
		self._current_datastring = self._current_datastring + data

parser = GPXParser(xml_file1)
hr_info1 = parser.parse()

parser2 = GPXParser(xml_file2)
hr_info2 = parser2.parse()

if hr_info1 and hr_info2:
	print "Nothing todo"
	sys.exit(0)

if hr_info1:
	tree = ET.parse(xml_file2)
	root = tree.getroot()

	for child in root:
		 print child.tag, child.attrib

	for trkpt in doc.getElementsByTagName("trkpt"):
		extensions = doc.createElement("extensions")
		trackpointextention = doc.createElementNS("http://www.garmin.com/xmlschemas/TrackPointExtension/v1","tp1:TrackPointExtension")
		hr = doc.createElementNS("http://www.garmin.com/xmlschemas/TrackPointExtension/v1","tp1:hr")
		time = trkpt.getElementsByTagName('time')[0].firstChild.nodeValue
		time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
		index = min(hr_info1, key=lambda date : abs(time-date))

		hrValue = doc.createTextNode(hr_info1[index]);
		hr.appendChild(hrValue)
		trackpointextention.appendChild(hr)
		extensions.appendChild(trackpointextention)
		trkpt.appendChild(extensions)

	print doc.toxml()
#         <extensions>
#           <tp1:TrackPointExtension>
#             <tp1:hr>102</tp1:hr>
#           </tp1:TrackPointExtension>
#         </extensions>

if hr_info2:
	pass






