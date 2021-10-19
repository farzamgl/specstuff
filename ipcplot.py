
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

  samples = ['mcycle', 'minstret', "load_dep", "mul_dep", "fma_dep", "sb_iraw_dep", "sb_fraw_dep", "sb_iwaw_dep", "sb_fwaw_dep"]

  parser = argparse.ArgumentParser()
  parser.add_argument("-i", dest="filename", required=True,
                      help="input binary file", metavar="FILE",
                      type=lambda x: is_valid_file(parser, x))

  args = parser.parse_args()

  data = args.filename.read()
  args.filename.close()
  benchmark = os.path.splitext(os.path.basename(args.filename.name))[0]

  parsed = {}
  for i in range(int(len(data)/8)):
    idx = i % len(samples)
    if samples[idx] not in parsed.keys():
      parsed[samples[idx]] = []
    parsed[samples[idx]].append(struct.unpack_from("<Q", data, 8*i)[0])

  for sample in samples:
    if sample != 'mcycle':
      plt.clf()
      plt.plot(parsed['mcycle'], parsed[sample])
      plt.xlabel('mcycle')
      plt.ylabel(sample)
      plt.title(benchmark)
      #plt.show()
      plt.savefig(benchmark + '.' + sample + '.png', dpi=300)
