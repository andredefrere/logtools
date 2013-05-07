import pprint
import json
from collections import OrderedDict

class BaseOutput:
	def __init__(self, commandLineArgs):
		self.commandLineArgs = commandLineArgs
		self.active = False
	def output(self, aggregate):
		"""output goes here"""

class RawOutput(BaseOutput):
	def __init__(self, commandLineArgs):
		BaseOutput.__init__(self, commandLineArgs)

		if 'output' in self.commandLineArgs and self.commandLineArgs['output'] == 'RAW':
			self.active = True
		else:
			self.active = False
	def output(self, aggregateObj):
		pprint.pprint(aggregateObj)

class ShellOutput(BaseOutput):
	def __init__(self, commandLineArgs):
		BaseOutput.__init__(self, commandLineArgs)
		if 'output' in self.commandLineArgs and self.commandLineArgs['output'] == 'SHELL':
			self.active = True
		else:
			self.active = False
	def output(self, aggregateObj):
		print "***"
		print aggregateObj['NAME']['desc']
		print "***"
		for a in aggregateObj:
			if a != 'NAME':
				if a.isupper():
					#for k,v in aggregateObj[a].items():
					#	print "%-20s%s%20i"%(a, k, v)
					print "%-40s%5s%20i"%(aggregateObj[a]['desc'], " ", aggregateObj[a]['count'])
				elif isinstance(aggregateObj[a], dict):
					for k,v in aggregateObj[a].items():
						if hasattr(v, 'items'):
							print "%-40s%5s%20i"%(v['desc'], " ", v['count'])
						else:
							print "%-40s%s%20i"%(a, k, v)

class JiraOutput(BaseOutput):
	ou = []
	def __init__(self, commandLineArgs):
		BaseOutput.__init__(self, commandLineArgs)
		if 'output' in self.commandLineArgs and self.commandLineArgs['output'] == 'JIRA':
			self.active = True
		else:
			self.active = False
	def output(self, aggregateObj):
		self.ou = []
		self.ou.append('{panel:title=%s}'%aggregateObj['NAME']['desc'])
		self.pretty_items(self.ou, aggregateObj)
		self.ou.append('{panel}')

		for a in self.ou:
			print a

	def pretty_items(self, r, d, nametag="%s: ", itemtag='|%s',
             valuetag="%s|", blocktag=('', '')):
		if isinstance(d, dict):
			#r.append(blocktag[0])
			for k, v in d.iteritems():
				if(k!='NAME'):
					name = nametag % k
					if isinstance(v, dict) or isinstance(v, list):
						r.append(itemtag % k)
						self.pretty_items(r, v)
					else:
						value = valuetag % v
						r.append(itemtag % (name + value))
			#r.append(blocktag[1])
		elif isinstance(d, list):
			r.append(blocktag[0])
			for i in d:
				if isinstance(i, dict) or isinstance(i, list):
					r.append(itemtag % " - ")
					self.pretty_items(r, i)
				else:
					r.append(itemtag % i)
			#r.append(blocktag[1])

class HTMLOutput(BaseOutput):
	ou = []
	hideEle = 0
	bScriptBlock = True

	def __init__(self, commandLineArgs):
		BaseOutput.__init__(self, commandLineArgs)

		if 'output' in self.commandLineArgs and self.commandLineArgs['output'] == 'HTML':
			self.active = True
		else:
			self.active = False
	def setScriptBlock(self):
		if self.bScriptBlock:
				self.ou.append('<head>')
				self.ou.append('<link rel="stylesheet" href="report.css">')
				self.ou.append('</head>')
				self.ou.append('<script language="javascript">')
				self.ou.append('function toggle(showHideDiv) {')
				self.ou.append('var ele = document.getElementById(showHideDiv);')
				self.ou.append('if(ele.style.display == "block") {')
				self.ou.append('ele.style.display = "none";')
				self.ou.append('}')
				self.ou.append('else {')
				self.ou.append('ele.style.display = "block";')
				self.ou.append('}')
				self.ou.append('}')
				self.ou.append('</script>')

	def output(self, aggregateObj):
		self.ou = []
		self.setScriptBlock()
		self.bScriptBlock = False
		self.hideEle+=1
		self.ou.append('<table><tr><td>')
		self.ou.append('<div id="headerDiv">')
		self.ou.append('<div id="titleText"><a id="hd%i" style="header" href="javascript:toggle(\'ct%i\');">%s</a></div>'%(self.hideEle,self.hideEle,aggregateObj['NAME']['desc']))
		self.ou.append('</div>')
		self.ou.append('</td></tr><tr><td>')
		self.ou.append('<div style="clear:both;"></div>')
		self.ou.append('<div id="contentDiv">')
		self.ou.append('<div id="ct%i" style="display: block;">'%(self.hideEle))
		self.pretty_items(self.ou, aggregateObj)
		self.ou.append("</div>")
		self.ou.append("</div>")
		self.ou.append('</td></tr></table>')
		self.ou.append("</div>")

		for a in self.ou:
			print a

	def pretty_items(self, r, d, nametag="<strong>%s: </strong>", itemtag='<li>%s</li>',
             valuetag="%s", blocktag=('<ul>', '</ul>')):
		if isinstance(d, dict):
			r.append(blocktag[0])
			for k, v in d.iteritems():
				if(k!='NAME'):
					name = nametag % k
					if isinstance(v, dict) or isinstance(v, list):
						r.append(itemtag % name)
						self.pretty_items(r, v)
					else:
						value = valuetag % v
						r.append(itemtag % (name + value))
			r.append(blocktag[1])
		elif isinstance(d, list):
			r.append(blocktag[0])
			for i in d:
				if isinstance(i, dict) or isinstance(i, list):
					r.append(itemtag % " - ")
					self.pretty_items(r, i)
				else:
					r.append(itemtag % i)
			r.append(blocktag[1])