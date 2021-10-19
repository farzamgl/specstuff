import sheetSupport
import argparse
import os.path
from pprint import pprint

def getNotation(n):
    string = ''
    while n > 0:
        n, rem = divmod(n-1, 26)
        string = chr(65 + rem) + string
    return string

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
#  parser.add_argument("-i", dest="filename", required=True,
#                      help="input binary file", metavar="FILE",
#                      type=lambda x: is_valid_file(parser, x))
  parser.add_argument('files', nargs='+', help='List of files')
  args = parser.parse_args()

  values = []
  fileNum = 0

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
    perc.append(('D$ miss', data['dcache_miss'] / data['mcycle']))
    perc.append(('D$ rollback', data['dcache_rollback'] / data['mcycle']))
    perc.append(('I$ miss', data['icache_miss'] / data['mcycle']))
    perc.append(('I$ rollback', data['icache_rollback'] / data['mcycle']))
    perc.append(('IRAW Scoreboard', data['sb_iraw_dep'] / data['mcycle']))
    perc.append(('FRAW Scoreboard', data['sb_fraw_dep'] / data['mcycle']))
    perc.append(('IWAW Scoreboard', data['sb_iwaw_dep'] / data['mcycle']))
    perc.append(('FWAW Scoreboard', data['sb_fwaw_dep'] / data['mcycle']))
    perc.append(('FMA dependency', data['fma_dep'] / data['mcycle']))
    perc.append(('Aux dependency', data['aux_dep'] / data['mcycle']))
    perc.append(('Load dependency', data['load_dep'] / data['mcycle']))
    perc.append(('Mul dependency', data['mul_dep'] / data['mcycle']))
    perc.append(('Other Data hazards', data['data_haz'] / data['mcycle']))
    perc.append(('Long hazard', data['long_haz'] / data['mcycle']))
    perc.append(('Other Control hazards', data['control_haz'] / data['mcycle']))
    perc.append(('Long pipe busy Int', data['long_i_busy'] / data['mcycle']))
    perc.append(('Long pipe busy Float', data['long_f_busy'] / data['mcycle']))
    perc.append(('Long pipe busy Int/Float', data['long_if_busy'] / data['mcycle']))
    perc.append(('Other Struct hazards', data['struct_haz'] / data['mcycle']))
    perc.append(('Mispredict', data['mispredict'] / data['mcycle']))
    perc.append(('BTB override', data['taken_override'] / data['mcycle']))
    perc.append(('RAS override', data['ret_override'] / data['mcycle']))
    perc.append(('Other', data['unknown'] / data['mcycle']))
    perc.append(('FE queue stall', data['fe_queue_stall'] / data['mcycle']))
    perc.append(('FE wait stall', data['fe_wait_stall'] / data['mcycle']))
    perc.append(('I$ fence', data['icache_fence'] / data['mcycle']))
    perc.append(('FE cmd', data['fe_cmd'] / data['mcycle']))
    perc.append(('FE cmd fence', data['fe_cmd_fence'] / data['mcycle']))
    perc.append(('Sum', '=SUM(A'+str(2+fileNum)+':'+getNotation(len(perc))+str(2+fileNum)+')'))
    perc.append(('Mem instr', data['mem_instr']/data['minstret']))
    perc.append(('Aux instr', data['aux_instr']/data['minstret']))
    perc.append(('FMA instr', data['fma_instr']/data['minstret']))
    perc.append(('Long INT instr', data['ilong_instr']/data['minstret']))
    perc.append(('Long FP instr', data['flong_instr']/data['minstret']))

    fileNum += 1

    if len(values) == 0:
      values.append([x[0] for x in perc])
    values.append([x[1] for x in perc])

  sheets = sheetSupport.initSheets()
  sheetId = sheetSupport.addSheet(sheets, "Stalls")

  print(len(values[0])-1)

  sheetSupport.writeSheet(sheets, 'Stalls!A1:'+getNotation(len(values[0])), values)
  sheetSupport.formatSheet(sheets, sheetId, len(values), len(values[0]))
  sheetSupport.paintCells(sheets, sheetId, 2, [x[0] for x in perc].index('Sum'))
