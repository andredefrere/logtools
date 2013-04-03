#!/usr/bin/python

import argparse, re
import sys
from aggregates import ConnexAggregate

class MongoLogSum(object):
	def __init__(self):
		self.aggregates = []

	def addAggregate(self, aggregateClass):
		if not aggregateClass in self.aggregates:
			self.aggregates.append(aggregateClass)

	def _arrayToString(self, arr):
		""" if arr is of type list, join elements with space delimiter. """
		if isinstance(arr, list):
			return " ".join(arr)
		else:
			return arr

	def parse(self):
		parser = argparse.ArgumentParser(description='mongodb log file summariser')
		
		parser.add_argument('--verbose', action='store_true', help='outputs information about the parser and arguments')
		parser.add_argument('--logfile', action='store', nargs='?', help='logfile to parse')

		for a in self.aggregates:
			for aa in a.filterArgs:
				parser.add_argument(aa[0], **aa[1])

		args = vars(parser.parse_args())
		args = dict((k, self._arrayToString(args[k])) for k in args)

		self.aggregates = [a(args) for a in self.aggregates]

		self.aggregates = [a for a in self.aggregates if a.active]

		logfile = open(args['logfile'], 'r')
		
		for a in self.aggregates:
			print a.aggregate(logfile)
		"""
		for line in logfile:
			if line.startswith('***'):
				print line,
				continue
			if all([a.accept(line) for a in self.aggregates]):
				print line,"""

if __name__ == '__main__':

	# create MongoLogSum instance
	mlogsum = MongoLogSum()

	# add aggregates
	mlogsum.addAggregate(ConnexAggregate)

	# start parsing
	mlogsum.parse()

