#!/usr/bin/env python3
import psutil as ps, sys
from subprocess import call
if __name__ == '__main__':
	if sys.argv[1:]:
		allOsafProcs = [p.name() for p in map(lambda n: ps.Process(n), ps.pids()) if 'osaf' in p.name()]
		l = ['./evaluate.py']+allOsafProcs+[sys.argv[-1]]
		print(" ".join(l))
		#call(['./evaluate.py']+allOsafProcs+[sys.argv[-1]])
