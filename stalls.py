import sheetSupport
import argparse
import os.path
from pprint import pprint

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
#  parser.add_argument("-i", dest="filename", required=True,
#                      help="input binary file", metavar="FILE",
#                      type=lambda x: is_valid_file(parser, x))
  parser.add_argument('files', nargs='+', help='List of files')
  args = parser.parse_args()

  values = []

  for filename in args.files:
    f = open(filename, 'r')
    data = {}
    next(f)
    for line in f:
      (key, val) = line.split()
      data[key] = int(val)

    f.close()

    perc = [('Benchmark', os.path.splitext(os.path.basename(f.name))[0])]
    perc.append(('Instruction', data['minstret'] / data['mcycle']))
    perc.append(('FE queue stall', data['fe_queue_stall'] / data['mcycle']))
    perc.append(('I$ rollback', data['icache_rollback'] / data['mcycle']))
    perc.append(('I$ miss', data['icache_miss'] / data['mcycle']))
    perc.append(('I$ fence', data['icache_fence'] / data['mcycle']))
    perc.append(('BTB override', data['taken_override'] / data['mcycle']))
    perc.append(('RAS override', data['ret_override'] / data['mcycle']))
    perc.append(('FE cmd', data['fe_cmd'] / data['mcycle']))
    perc.append(('FE cmd fence', data['fe_cmd_fence'] / data['mcycle']))
    perc.append(('Mispredict', data['mispredict'] / data['mcycle']))
    perc.append(('Control hazzard', data['control_haz'] / data['mcycle']))
    perc.append(('Long hazzard', data['long_haz'] / data['mcycle']))
    perc.append(('Data hazzard', data['data_haz'] / data['mcycle']))
    perc.append(('Load dependency', data['load_dep'] / data['mcycle']))
    perc.append(('Mul dependency', data['mul_dep'] / data['mcycle']))
    perc.append(('Struct hazzard', data['struct_haz'] / data['mcycle']))
    perc.append(('D$ rollback', data['dcache_rollback'] / data['mcycle']))
    perc.append(('D$ miss', data['dcache_miss'] / data['mcycle']))
    perc.append(('Other', data['unknown'] / data['mcycle']))


    if len(values) == 0:
      values.append([x[0] for x in perc])
    values.append([x[1] for x in perc])

  sheets = sheetSupport.initSheets()
  sheetId = sheetSupport.addSheet(sheets, "Stalls")

  sheetSupport.writeSheet(sheets, 'Stalls!A1:'+chr(ord('A')+len(values[0])-1), values)
  sheetSupport.formatSheet(sheets, sheetId, len(values), len(values[0]))
