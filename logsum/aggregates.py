from datetime import date, time, datetime, timedelta, MINYEAR, MAXYEAR
import re
from collections import defaultdict

class NestedDict(dict):
	def __getitem__(self,key):
		if key in self: return self.get(key)
		return self.setdefault(key,NestedDict())

class BaseAggregate:
	""" Base Aggregate, all other Aggregates inherit this class """

	filterArgs = []

	def __init__(self, commandLineArgs):
		""" constructor """
		self.commandLineArgs = commandLineArgs

		# set true individually
		self.active = False
	
	def aggregate(self, logfile):
		print "summary goes here"
	

class ConnexAggregate(BaseAggregate):
	""" For all "connection accepted" and "end connection" strings """
	filterArgs = [
		('--connex', { 'action' : 'store_true', 'default' : False, 'help' : 'output aggregate for connections'} ) 
	]

	def __init__(self, commandLineArgs):
		BaseAggregate.__init__(self, commandLineArgs)

		self.active = self.commandLineArgs['connex']

	def aggregate(self, logfile):
		#totalConnex = defaultdict(lambda: defaultdict(dict))
		totalConnex = NestedDict()
		totalConnex["OPEN"] = {'desc' : 'Total Connections Opened', 'count' : 0}
		totalConnex["CLOSED"] = {'desc' : 'Total Connections Closed', 'count' : 0}
		for line in logfile:
			tokens = line.split()
			if re.search('connection accepted', line):
				ip = tokens[8].split(':',1)[0]
				totalConnex["OPEN"]["count"] +=1
				if totalConnex[ip]["open"]["count"]:
					totalConnex[ip]["open"]["count"] +=1
				else:
					totalConnex[ip]["open"]["count"] = 1
				totalConnex[ip]["open"]["desc"] = 'connections opened from '+ip
			if re.search('end connection', line):
				ip = tokens[7].split(':',1)[0]
				totalConnex["CLOSED"]["count"] +=1
				if totalConnex[ip]["closed"]["count"]:
					totalConnex[ip]["closed"]["count"] +=1
				else:
					totalConnex[ip]["closed"]["count"] =1
				totalConnex[ip]["closed"]["desc"] = 'connection closed from '+ip
		return totalConnex