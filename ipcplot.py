
import sys
import argparse
import math
import os.path
import struct
import matplotlib.pyplot as plt

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, "rb")

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("-i", dest="filename", required=True,
                      help="input binary file", metavar="FILE",
                      type=lambda x: is_valid_file(parser, x))

  args = parser.parse_args()

  data = args.filename.read()
  args.filename.close()
  benchmark = os.path.splitext(os.path.basename(args.filename.name))[0]

  mcycle = []
  minstret = []
  for i in xrange(len(data)/8):
    if (i % 2) == 0:
      mcycle.append(struct.unpack_from("<Q", data, 8*i)[0])
    else:
      minstret.append(struct.unpack_from("<Q", data, 8*i)[0])

  plt.plot(mcycle, minstret)
  plt.xlabel('mcycle')
  plt.ylabel('minstret')
  plt.title(benchmark)
  #plt.show()
  plt.savefig(benchmark + '.png', dpi=300)
