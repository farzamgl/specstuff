
import sys
import math
import heapq
import argparse
import os.path
import numpy as np

def subset(arr, n):
    heap = [(0, i) for i in range(n)]
    res = [[] for _ in range(n)]
    for each in sorted(arr, reverse=True):
        val, idx = heapq.heappop(heap)
        total = val + each
        res[idx].append(each)
        heapq.heappush(heap, (total, idx))
    return res

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('-i', dest='filename', required=True, metavar="FILE",
                    type=lambda x: is_valid_file(parser, x),
                    help='File including benchmark names and runtime')
  parser.add_argument('-n', dest='K', required=True, type=int, metavar='PARTS')
  args = parser.parse_args()

  lines = args.filename.readlines()
  A = []
  for line in lines:
    line = line.rstrip()
    if line[0] == '#':
      continue
    elif line == 'END':
      break
    words = line.split()
    A.append((int(words[1].replace(',','')), words[0]))

  values = [i[0] for i in A]
  sets = subset(values,args.K)
  names = [[] for _ in range(args.K)]

  d = dict(A)
  for i in xrange(len(sets)):
    names[i] = [0] * len(sets[i])
    for j in xrange(len(sets[i])):
      names[i][j] = d[sets[i][j]]

  for i in xrange(len(sets)):
    print(' '.join(str(x) for x in names[i]))
    print sum(sets[i])
