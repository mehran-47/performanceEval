#!/usr/bin/env python3
import sys, json

class consolidate():
	def __init__(self, dump):
		self.dump = dump
		self.result = dict( (k,type(v)()) for k,v in self.dump.items())

	def consolidate(self, aProc):
		self.result[aProc]['memory_MB'] = sum([aTup[1] for aTup in self.dump[aProc]['memory_info']])/len(self.dump[aProc]['memory_info'])
		self.result[aProc]['cpu_percent'] = sum([aTup[1] for aTup in self.dump[aProc]['cpu_info']])/len(self.dump[aProc]['cpu_info'])
		self.result[aProc]['net_load'] = {'up':None, 'down':None}
		self.result[aProc]['net_load']['up'] = sum( [aTup[1] for aTup in self.dump[aProc]['net_load']['up']] )/len(self.dump[aProc]['net_load']['up'])
		self.result[aProc]['net_load']['down'] = sum( [aTup[1] for aTup in self.dump[aProc]['net_load']['down']] )/len(self.dump[aProc]['net_load']['down'])

	def summary(self):
		for aProc in self.dump:	self.consolidate(aProc)
		return self.result

if __name__ == '__main__':
	if sys.argv[1:]:
		with open(sys.argv[1],'r') as f: dump = json.loads(f.read())
		c = consolidate(dump)
		print(c.summary())
