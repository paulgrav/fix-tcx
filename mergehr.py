#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
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
	_current_loc = {}

	def __init__(self, filename):
		self._data = {}
		self._filename = None
		self._current_element = None
		self._current_datetime = None
		self._current_datastring = ""
		self._filename = filename
		self._current_loc = {}

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
		if name == "trkpt":
			self._current_loc = {"lon": attrs['lon'], "lat": attrs['lat']}

	def _end_element(self, name):
		data = self._current_datastring.strip()

		if name == "time":
			if data:
				try:
					self._current_datetime = datetime.strptime(data, "%Y-%m-%dT%H:%M:%SZ")
				except ValueError:
					self._current_datetime = data

				self._data[self._current_datetime] = self._current_loc

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
	ns = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
	ET.register_namespace('', ns)
	root = tree.getroot()

	for child in root.iter("{%s}Trackpoint" % ns):
		time = child.find('{%s}Time' % ns).text
		time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
		index = min(hr_info1, key=lambda date : abs(time-date))
		loc = hr_info1[index]

		lat_ele  = child.find("{{{0}}}Position/{{{0}}}LatitudeDegrees".format(ns))
		lon_ele  = child.find("{{{0}}}Position/{{{0}}}LongitudeDegrees".format(ns))

		if lat_ele is not None and lon_ele is not None:
			lat_ele.text = loc['lat']
			lon_ele.text = loc['lon']

	tree.write(sys.stdout,  xml_declaration=True,encoding="utf-8", method="xml")


if hr_info2:
	pass






