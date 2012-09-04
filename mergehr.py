#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
import lxml.etree as ET2
from xml.dom.minidom import parse, parseString
import xml.parsers.expat
import sys
from datetime import datetime, timedelta
import json

xml_file1 = sys.argv[1] # tcx file with location info
xml_file2 = sys.argv[2] # tcx file with heartrate info
hr_info = {}

output = {"id": None,
		  "type": "json",
		  "data_fields": ["time", "latitude", "longitude", "elevation", "heartrate"],
		  "data": [],
		  "activity_type": "run"}

tcx = """
<TrainingCenterDatabase
  xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
  xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
  xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">
  <Activities>
    <Activity Sport="Running">
      <Id></Id>
      <Lap StartTime="">
        <Track>

		</Track>
      </Lap>
    </Activity>
  </Activities>
	<Author xsi:type="Application_t">
    <Name>Garmin Training Center</Name>
    <Build>
      <Version>
        <VersionMajor>3</VersionMajor>
        <VersionMinor>2</VersionMinor>
        <BuildMajor>1</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
      <Type>Release</Type>
      <Time>Nov 9 2011, 10:09:03</Time>
      <Builder>sqa</Builder>
    </Build>
    <LangID>en</LangID>
    <PartNumber>006-A0183-00</PartNumber>
  </Author>

</TrainingCenterDatabase>
"""

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

		if name == "ele":
			self._current_loc['ele'] = data

		self._current_datastring = ""

	def _char_data(self, data):
		self._current_datastring = self._current_datastring + data

parser = GPXParser(xml_file1)
loc_info = parser.parse()


#################### DO HR

tree = ET.parse(xml_file2)
ns = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
ET.register_namespace('', ns)
root = tree.getroot()

for child in root.iter("{%s}Trackpoint" % ns):
	time = datetime.strptime(child.find('{%s}Time' % ns).text, "%Y-%m-%dT%H:%M:%S.%fZ")
	hr  = child.find("{{{0}}}HeartRateBpm/{{{0}}}Value".format(ns))
	hr_info[time] = hr.text


########################################
root = ET2.fromstring(tcx)
tree = ET2.ElementTree(root)
ns = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
# ET.register_namespace('', ns)

sorted_time = sorted(loc_info.iterkeys()):
start_time = sorted_time.next()
root.find("{{{0}}}Activities/{{{0}}}Activity/{{{0}}}Id".format(ns)).text = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
root.find("{{{0}}}Activities/{{{0}}}Activity/{{{0}}}Lap".format(ns)).set('StartTime', start_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
track = root.find("{{{0}}}Activities/{{{0}}}Activity/{{{0}}}Lap/{{{0}}}Track".format(ns))

for time in sorted_time:
	loc = loc_info[time]
	trackpoint = ET2.SubElement(track, '{%s}Trackpoint' % ns)
	t = ET2.SubElement(trackpoint, '{%s}Time' % ns)
	position = ET2.SubElement(trackpoint, '{%s}Position' % ns)
	lat = ET2.SubElement(position, '{%s}LatitudeDegrees' % ns)
	lon = ET2.SubElement(position, '{%s}LongitudeDegrees' % ns)
	alt = ET2.SubElement(trackpoint, '{%s}AltitudeMeters' % ns)
	hr = ET2.SubElement(trackpoint, '{%s}HeartRateBpm' % ns)
	hrv = ET2.SubElement(hr, '{%s}Value' % ns)
	t.text = time.strftime("%Y-%m-%dT%H:%M:%SZ")
	index = min(hr_info, key=lambda date : abs(time-date))
	hrvalue = hr_info[index]

	hrv.text = hrvalue
	lat.text = loc['lat']
	lon.text = loc['lon']
	alt.text = loc['ele']

print ET2.tostring(root, xml_declaration=True, encoding="utf-8", method='xml', pretty_print=True)