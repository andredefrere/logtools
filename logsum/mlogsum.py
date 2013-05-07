#!/usr/bin/python

import argparse, re
import sys
import pprint
from aggregates import ConnexAggregate, OpsAggregate, SocketExceptionAggregate
from outifier import RawOutput, ShellOutput, HTMLOutput, JiraOutput

class MongoLogSum(object):
	def __init__(self):
		self.aggregates = []
		self.outputs = []

	def addAggregate(self, aggregateClass):
		if not aggregateClass in self.aggregates:
			self.aggregates.append(aggregateClass)

	def addOutput(self, outputClass):
		if not outputClass in self.outputs:
			self.outputs.append(outputClass)

	def _arrayToString(self, arr):
		""" if arr is of type list, join elements with space delimiter. """
		if isinstance(arr, list):
			return " ".join(arr)
		else:
			return arr

	def parseArgs(self):
		parser = argparse.ArgumentParser(description='mongodb log file summariser')
		
		parser.add_argument('--verbose', action='store_true', help='outputs information about the parser and arguments')
		parser.add_argument('--logfile', action='store', nargs='?', help='logfile to parse')
		parser.add_argument('--from', action='store', nargs='*', help='output starting at FROM', default='start')
		parser.add_argument('--to', action='store', nargs='*', help='output up to TO', default='end')
		parser.add_argument('--output', action='store', nargs='*', default = 'SHELL', choices=['RAW', 'SHELL', 'HTML', 'JIRA'])

		for a in self.aggregates:
			for aa in a.filterArgs:
				parser.add_argument(aa[0], **aa[1])

		self.args = vars(parser.parse_args())
		self.args = dict((k, self._arrayToString(self.args[k])) for k in self.args)

	def parse(self):

		self.aggregates = [a(self.args) for a in self.aggregates]
		self.aggregates = [a for a in self.aggregates if a.active]

		logfile = open(self.args['logfile'], 'r')
		
		for line in logfile:
			for a in self.aggregates:
				if(a.accept(line)):
					a.addAggregateLine(line)

	def output(self, outputType):
		self.outputs = [o(self.args) for o in self.outputs]
		self.outputs = [o for o in self.outputs if o.active]
		for b in self.outputs:
			for a in self.aggregates:
				b.output(a.aggregateObj)

if __name__ == '__main__':

	# create MongoLogSum instance
	mlogsum = MongoLogSum()

	# add aggregates
	mlogsum.addAggregate(ConnexAggregate)
	mlogsum.addAggregate(OpsAggregate)
	mlogsum.addAggregate(SocketExceptionAggregate)

	#add output classes
	mlogsum.addOutput(RawOutput)
	mlogsum.addOutput(ShellOutput)
	mlogsum.addOutput(HTMLOutput)
	mlogsum.addOutput(JiraOutput)

	# get arguments
	mlogsum.parseArgs()

	# start parsing
	mlogsum.parse()

	#output aggregateobjs
	mlogsum.output(mlogsum.args['output'])