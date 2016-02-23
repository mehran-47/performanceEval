#!/usr/bin/env python3
import psutil as ps, sys, logging, pdb, time, base64
from subprocess import Popen, PIPE
from pexpect import spawn
from threading import Thread

class evaluate():
	def __init__(self):
		pass

	def byName(self, names):
		logging.debug(names)
		allProcsOfName = [p for p in map(lambda n: ps.Process(n), ps.pids()) if p.name() in names]
		#logging.debug(allProcsOfName)
		#logging.debug(len(allProcsOfName))
		return self.listByPsProcs(allProcsOfName)

	def dictByName(self, names):
		listByNames = self.byName(names)
		return dict((name, {x for x in listByNames if name in x.name()}) for name in names)

	def dictByPid(self, pids):
		procs = [ps.Process(int(p)) for p in pids]
		return dict((p.pid,{p} | set(p.children(recursive=True))) for p in procs)

	def listByPsProcs(self, ps_procs):
		listOfSets = [{p}|set(p.children(recursive=True)) for p in ps_procs]
		return [proc for aSet in listOfSets for proc in aSet]

	def dictOfConnectionsByPid(self, ps_procs):
		return dict((p.pid, [p.name(), p.connections()]) for p in ps_procs if p.connections()[0:])

	def updateWith(self):
		pass

def testDef():
	child = spawn('bash')
	child.sendline('nethogs -t | grep '+sys.argv[1] +' --colour=never')
	for line in child:
		print(line.decode('utf-8').splitlines()[-1])
		#print([l for l in line.decode('UTF-8').splitlines()])
		#print([l for l in base64.b32decode(line).splitlines() if sys.argv[1] in l])
		#base64.b64decode
		time.sleep(1)


if __name__ == '__main__':
	logging.basicConfig(format= '%(asctime)s %(levelname)s - %(name)s\n%(message)s', level=logging.DEBUG)
	e = evaluate()
	if sys.argv[1:]:
		if sys.argv[1]=='-pid':
			logging.info("%r,\n%d" %(e.listByPsProcs(map(ps.Process, map(int, sys.argv[2:]))), len(e.listByPsProcs(map(ps.Process, map(int, sys.argv[2:])) ) ) ) )
		elif sys.argv[1]=='-name':
			logging.info(e.dictByName(sys.argv[2:]))
			logging.debug("%r" %(dict((k,len(v)) for k,v in e.dictByName(sys.argv[2:]).items() ) ) )
		elif sys.argv[1]=='-connections':
			logging.info(e.dictOfConnectionsByPid(e.byName(sys.argv[2:])))
		else:
			Thread(target=testDef).start()
	else:
		print("Please provide process name/ID to evaluate. Usage:\n./evaluate.py -id <pid> or ./evaluate.py -name <name>")