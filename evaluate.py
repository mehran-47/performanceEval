#!/usr/bin/env python3
import psutil as ps, sys, logging, pdb

def byName(names):
	logging.debug(names)
	allProcsOfName = [p for p in map(lambda n: ps.Process(n), ps.pids()) if p.name() in names]
	logging.debug(allProcsOfName)
	return listByPsProcs(allProcsOfName)

def dictByPid(pids):
	procs = [ps.Process(int(p)) for p in pids]
	return dict((p.pid,{p} | set(p.children(recursive=True))) for p in procs)

def listByPsProcs(ps_procs):
	listOfSets = [{p}|set(p.children(recursive=True)) for p in ps_procs]
	return [proc for aSet in listOfSets for proc in aSet]

if __name__ == '__main__':
	logging.basicConfig(format= '%(asctime)s %(levelname)s - %(name)s\n%(message)s', level=logging.INFO)
	#logging.info("%r,\n%d" %(listByPsProcs([ps.Process(int(sys.argv[1]))]), len(listByPsProcs([ps.Process(int(sys.argv[1]))])) ) )	

	if sys.argv[1:]:
		if sys.argv[1]=='-pid':
			logging.info("%r,\n%d" %(listByPsProcs([ps.Process(int(sys.argv[2]))]), len(listByPsProcs([ps.Process(int(sys.argv[2]))])) ) )
		elif sys.argv[1]=='-name':
			logging.info(byName(sys.argv[2:]))
	else:
		print("Please provide process name/ID to evaluate. Usage:\n./evaluate.py -id <pid> or ./evaluate.py -name <name>")