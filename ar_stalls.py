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
    perc.append(('IPC', data['minstret'] / data['mcycle']))
    perc.append(('I$ miss', data['ic_miss'] / data['mcycle']))
    perc.append(('I$ DMA', data['ic_dma'] / data['mcycle']))
    perc.append(('D$ pipe', data['dc_pipe'] / data['mcycle']))
    perc.append(('D$ miss', data['dc_miss'] / data['mcycle']))
    perc.append(('D$ DMA', data['dc_dma'] / data['mcycle']))
    perc.append(('BP ovr', data['bp_haz'] / data['mcycle']))
    perc.append(('Mispredict', data['br_miss'] / data['mcycle']))
    perc.append(('CSR buf', data['csr_buf'] / data['mcycle']))
    perc.append(('MUL haz', data['mul_haz'] / data['mcycle']))
    perc.append(('DIV busy', data['div_busy'] / data['mcycle']))
    perc.append(('FPU busy', data['fpu_busy'] / data['mcycle']))
    perc.append(('LD pipe', data['ld_pipe'] / data['mcycle']))
    perc.append(('LD grant', data['ld_grant'] / data['mcycle']))
    perc.append(('ST pipe', data['st_pipe'] / data['mcycle']))
    perc.append(('SBUF spec', data['sbuf_spec'] / data['mcycle']))
    perc.append(('WAW reorder', data['waw_reorder'] / data['mcycle']))
    perc.append(('SB full', data['sb_full'] / data['mcycle']))
    perc.append(('CSR flush', data['csr_flush'] / data['mcycle']))
    perc.append(('fence', data['fence'] / data['mcycle']))
    perc.append(('unknown', data['unknown'] / data['mcycle']))
    perc.append(('Sum', '=SUM(C'+str(2+fileNum)+':'+getNotation(len(perc)-1)+str(2+fileNum)+')'))

    fileNum += 1

    if len(values) == 0:
      values.append([x[0] for x in perc])
    values.append([x[1] for x in perc])

  sheets = sheetSupport.initSheets()
  sheetId = sheetSupport.addSheet(sheets, SPREADSHEET_ID, sheetName)

  print(len(values[0])-1)

  sheetSupport.writeSheet(sheets, SPREADSHEET_ID, sheetName+'!A1:'+getNotation(len(values[0])), values)
  sheetSupport.formatSheet(sheets, SPREADSHEET_ID, sheetId, len(values), len(values[0]))
  #sheetSupport.paintCells(sheets, SPREADSHEET_ID, sheetId, 3, [x[0] for x in perc].index('Sum'))
