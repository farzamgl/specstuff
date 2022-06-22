from __future__ import division
import sheetSupport
import argparse
import os.path
from pprint import pprint

SPREADSHEET_ID = '1Ia4TAmpXvCf8ghn-MUPRBDLMCQxKEmr7vfPpCJsK4iU'
sheetName = 'tmp'

def getNotation(n):
    string = ''
    while n > 0:
        n, rem = divmod(n-1, 26)
        string = chr(65 + rem) + string
    return string

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
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
    perc.append(('mcycle', data['mcycle']))
    perc.append(('Instr', data['minstret'] / data['mcycle']))
    perc.append(('DMA', data['dma'] / data['mcycle']))
    perc.append(('L2 miss', data['l2_miss'] / data['mcycle']))
    perc.append(('I$ miss', data['icache_miss'] / data['mcycle']))
    perc.append(('D$ miss', data['dcache_miss'] / data['mcycle']))
    perc.append(('IRAW SB', data['sb_iraw_dep'] / data['mcycle']))
    perc.append(('FRAW SB', data['sb_fraw_dep'] / data['mcycle']))
    perc.append(('IWAW SB', data['sb_iwaw_dep'] / data['mcycle']))
    perc.append(('FWAW SB', data['sb_fwaw_dep'] / data['mcycle']))
    perc.append(('FMA dep', data['fma_dep'] / data['mcycle']))
    perc.append(('AUX dep', data['aux_dep'] / data['mcycle']))
    perc.append(('load dep', data['load_dep'] / data['mcycle']))
    perc.append(('mul dep', data['mul_dep'] / data['mcycle']))
    perc.append(('long haz', data['long_haz'] / data['mcycle']))
    perc.append(('idiv haz', data['idiv_haz'] / data['mcycle']))
    perc.append(('fdiv haz', data['fdiv_haz'] / data['mcycle']))
    perc.append(('other Data haz', data['data_haz'] / data['mcycle']))
    perc.append(('other Control haz', data['control_haz'] / data['mcycle']))
    perc.append(('other Struct haz', data['struct_haz'] / data['mcycle']))
    perc.append(('Mispredict', data['mispredict'] / data['mcycle']))
    perc.append(('BTB ovr', data['branch_override'] / data['mcycle']))
    perc.append(('RAS ovr', data['ret_override'] / data['mcycle']))
    perc.append(('FE cmd', data['fe_cmd'] / data['mcycle']))
    perc.append(('FE cmd fence', data['fe_cmd_fence'] / data['mcycle']))
    perc.append(('Other', data['unknown'] / data['mcycle']))
    perc.append(('Sum', '=SUM(C'+str(2+fileNum)+':'+getNotation(len(perc))+str(2+fileNum)+')'))
    #perc.append(('Mem instr', data['mem_instr']/data['minstret']))
    #perc.append(('Aux instr', data['aux_instr']/data['minstret']))
    #perc.append(('FMA instr', data['fma_instr']/data['minstret']))
    #perc.append(('Long INT instr', data['ilong_instr']/data['minstret']))
    #perc.append(('Long FP instr', data['flong_instr']/data['minstret']))

    fileNum += 1

    if len(values) == 0:
      values.append([x[0] for x in perc])
    values.append([x[1] for x in perc])

  sheets = sheetSupport.initSheets()
  sheetId = sheetSupport.addSheet(sheets, SPREADSHEET_ID, sheetName)

  print(len(values[0])-1)

  sheetSupport.writeSheet(sheets, SPREADSHEET_ID, sheetName + '!A1:'+getNotation(len(values[0])), values)
  sheetSupport.formatSheet(sheets, SPREADSHEET_ID, sheetId, len(values), len(values[0]))
  #sheetSupport.paintCells(sheets, SPREADSHEET_ID, sheetId, 3, [x[0] for x in perc].index('Sum'))
