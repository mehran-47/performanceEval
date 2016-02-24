#!/usr/bin/env python3
import psutil as ps, sys, logging, pdb, time, base64, json
from subprocess import Popen, PIPE
from pexpect import spawn
from threading import Thread, Event

'''
Dependency installation:
sudo apt-get install libpcap-dev & \
git clone https://github.com/raboof/nethogs.git & \
cd nethogs && make && sudo install
'''

class evaluate():
	def __init__(self, names, interfaceName, updateInterval):
		self.finalDict = dict()
		self.interval = updateInterval
		self.names = names
		self.netUpdaterThreads =  [ThreadInterruptable(target=self.updateWithNetworkUsage, args=(interfaceName, n), name='netUpdaterThread-'+n) for n in names]
		self.allThreads = [ThreadInterruptable(target=self.mergeAndDisplayFinalDict, name='mergeAndDisplayFinalDict')] + self.netUpdaterThreads
		self.inventory = {}


	def start(self):
		try:
			for t in self.allThreads: t.start()
		except KeyboardInterrupt:
			for t in self.allThreads: 
				t.join()
				t.killThreads(self.allThreads)
			call(['killall','nethogs'])

	def byName(self):
		logging.debug(self.names)
		allProcsOfName = [p for p in map(lambda n: ps.Process(n), ps.pids()) if p.name() in self.names]
		return self.listByPsProcs(allProcsOfName)

	def dictByNames(self):
		listByNames = self.byName()
		toRet = {}
		try:
			toRet =  dict((name, {x for x in listByNames if name in x.name()}) for name in self.names)
		except ps.NoSuchProcess:
			logging.warning('A process died during construction of ps-processes-by-name, skipping this dictionary')
		return toRet

	def dictByPid(self, pids):
		procs = [ps.Process(int(p)) for p in pids]
		return dict((p.pid,{p} | set(p.children(recursive=True))) for p in procs)

	def listByPsProcs(self, ps_procs):
		toRet = []
		try:
			listOfSets = [{p}|set(p.children(recursive=True)) for p in ps_procs]
			toRet = [proc for aSet in listOfSets for proc in aSet]
		except ps.NoSuchProcess:
			logging.warning('A process died during construction of ps-processes-by-list, skipping this dictionary')
		return toRet

	def dictOfConnectionsByPid(self, ps_procs):
		return dict((p.pid, [p.name(), p.connections()]) for p in ps_procs if p.connections()[0:])

	
	def updateWithNetworkUsage(self, devName, procName):
		child = spawn('bash', timeout=None)
		child.sendline('nethogs -t '+devName+' | grep '+ procName+' --colour=never')	
		for line in child:
			if not threadsRunning.is_set():
				break
			try:
				logging.debug(line.decode('utf-8'))
				lineSplit = line.decode('utf-8').split('\t')
				pid = lineSplit[0].split('/')[-2]
				up = float(lineSplit[1])
				down = float(lineSplit[2])
				if procName not in self.finalDict: 
					self.finalDict[procName] = {}
				elif 'net_load' not in self.finalDict[procName]:
					self.finalDict[procName]['net_load'] = {}
				else:
					self.finalDict[procName]['net_load']['up'] = up
					self.finalDict[procName]['net_load']['down'] = down			
			except IndexError:
				logging.warning('invalid line format found in output of nethogs')
			except KeyboardInterrupt:
				child.terminate()
			logging.debug("final-dict: %r" %(self.finalDict))
			time.sleep(self.interval)
		child.terminate()

	def mergeAndDisplayFinalDict(self):
		while threadsRunning.is_set():
			procsDictByName = self.dictByNames()
			memoryInfoByName = dict( (k, sum([p.memory_info().rss/10**6 for p in l]) ) for k,l in procsDictByName.items())
			logging.debug("memoryInfoByName %r" %(memoryInfoByName))
			for k in memoryInfoByName:
				if k not in self.finalDict:			
					self.finalDict[k] = {}
				self.finalDict[k]['memory_info'] = memoryInfoByName[k]
			logging.debug("from mergeAndDisplayFinalDict:  %r", self.finalDict)
			for k in self.finalDict:
				if k not in self.inventory:
					self.inventory[k] = {}
					self.inventory[k]['memory_info'] = []
					self.inventory[k]['net_load'] = {}
					self.inventory[k]['net_load']['up'] = []
					self.inventory[k]['net_load']['down'] = []
				if self.finalDict[k].get('memory_info')!=None:
					self.inventory[k]['memory_info'] += [self.finalDict[k].get('memory_info')]
				if self.finalDict[k].get('net_load')!=None:
					logging.debug("%r" %(self.finalDict[k].get('net_load')))
					if 'up' in self.finalDict[k].get('net_load'):
						self.inventory[k]['net_load']['up'] += [self.finalDict[k]['net_load']['up']]
						self.inventory[k]['net_load']['down'] += [self.finalDict[k]['net_load']['down']]
			logging.info("inventory : %r" %(self.inventory))
			time.sleep(self.interval)			



class ThreadInterruptable(Thread):
	'''Extended python thread to be able to terminate them in batch using one 'SIGTERM' '''
	def join(self, timeout=0.1):
		try:
			super(ThreadInterruptable, self).join(timeout)
		except KeyboardInterrupt:
			logging.info('Stopping thread %r' %(self.name))
			try:
				self._tstate_lock = None
				self._stop()
				#The avalanche effect: one 'KeyboardInterrupt' to kill them all.
				threadsRunning.clear()
				with open('dataDump.json', 'w') as df: df.write(json.dumps(e.inventory, indent=4))
				logging.info('Stopping all threads to exit program.')
			except AssertionError:
				logging.warning('Ignored AssertionError in parent (threading.Thread) class.')

	def killThreads(self, tl):
		for aThread in tl:
			aThread._tstate_lock = None
			aThread._stop()

if __name__ == '__main__':
	logging.basicConfig(format= '%(asctime)s %(levelname)s - %(name)s:\t%(message)s', level=logging.INFO)
	if sys.argv[1:]:
		threadsRunning = Event()
		threadsRunning.set()
		e = evaluate(sys.argv[1:-1], sys.argv[-1], 2)
		e.start()
	else:
		print("Please provide process name/ID to evaluate. Usage:\n./evaluate.py -id <pid> or ./evaluate.py -name <name>")