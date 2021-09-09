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
    perc.append(('IPC', data['minstret'] / data['mcycle']))
    perc.append(('FE stall per cycle', data['fe_stall'] / data['mcycle']))
    perc.append(('FE queue full per cycle', data['fe_queue_full'] / data['mcycle']))
    perc.append(('BTB override %', data['ovr_taken'] / data['taken'] * 100))
    perc.append(('RAS override %', data['over_ret'] / data['ret'] * 100))
    perc.append(('FE commands per instr', data['fe_cmd_nonattaboy'] / data['minstret']))
    perc.append(('Mispredict per instr', data['mispredict'] / data['minstret']))
    perc.append(('Taken mispredict %', data['mispredict_taken'] / data['mispredict'] * 100))
    perc.append(('NTaken mispredict %', data['mispredict_ntaken'] / data['mispredict'] * 100))
    perc.append(('Non-branch mispredict %', data['mispredict_nonbr'] / data['mispredict'] * 100))
    perc.append(('I$ miss %', data['icache_rollback'] / data['icache_access'] * 100))
    perc.append(('Arverage I$ miss duration', data['icache_miss'] / data['icache_rollback']))
    perc.append(('D$ miss %', data['dcache_rollback'] / data['dcache_access'] * 100))
    perc.append(('Arverage D$ miss duration', data['dcache_miss'] / data['dcache_rollback']))
    perc.append(('Control hazzard per instr', data['control_haz'] / data['minstret']))
    perc.append(('Data hazzard per instr', data['data_dep'] / data['minstret']))
    perc.append(('Struct hazzard per instr', data['struct_haz'] / data['minstret']))
    perc.append(('Load dep %', data['load_dep'] / data['data_dep'] * 100))
    perc.append(('Mul dep %', data['mul_dep'] / data['data_dep'] * 100))

    if len(values) == 0:
      values.append([x[0] for x in perc])
    values.append([x[1] for x in perc])

  sheets = sheetSupport.initSheets()
  sheetId = sheetSupport.addSheet(sheets, "Events")

  sheetSupport.writeSheet(sheets, 'Events!A1:'+chr(ord('A')+len(values[0])-1), values)
  sheetSupport.formatSheet(sheets, sheetId, len(values), len(values[0]))
