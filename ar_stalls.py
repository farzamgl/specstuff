import sheetSupport
import argparse
import os.path
from pprint import pprint

SPREADSHEET_ID = '1YfNEdrXEHRLEvV8KjvLy8PZYHxctiLte1G5HsDPcTSU'

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
    perc.append(('mcycle', data['mcycle']))
    perc.append(('Instruction', data['minstret'] / data['mcycle']))
    perc.append(('FE wait', data['fe_wait'] / data['mcycle']))
    perc.append(('IS busy', data['is_busy'] / data['mcycle']))
    perc.append(('Scoreboard full', data['sb_full'] / data['mcycle']))
    perc.append(('Branch haz', data['br_haz'] / data['mcycle']))
    perc.append(('WAW haz', data['waw_haz'] / data['mcycle']))
    perc.append(('CSR haz', data['csr_haz'] / data['mcycle']))
    perc.append(('MUL haz', data['mul_haz'] / data['mcycle']))
    perc.append(('FLU busy', data['flu_busy'] / data['mcycle']))
    perc.append(('LSU busy', data['lsu_busy'] / data['mcycle']))
    perc.append(('FPU busy', data['fpu_busy'] / data['mcycle']))
    perc.append(('Branch mispredict', data['br_miss'] / data['mcycle']))
    perc.append(('LSU tag lookup', data['lsu_tl'] / data['mcycle']))
    perc.append(('LSU wait', data['lsu_wait'] / data['mcycle']))
    perc.append(('AMO flush', data['amo_flush'] / data['mcycle']))
    perc.append(('CSR flush', data['csr_flush'] / data['mcycle']))
    perc.append(('Exception', data['exception'] / data['mcycle']))
    perc.append(('Commit haz', data['cmt_haz'] / data['mcycle']))
    perc.append(('Unknown', data['unknown'] / data['mcycle']))
    perc.append(('Sum', '=SUM(C'+str(2+fileNum)+':'+getNotation(len(perc))+str(2+fileNum)+')'))

    fileNum += 1

    if len(values) == 0:
      values.append([x[0] for x in perc])
    values.append([x[1] for x in perc])

  sheets = sheetSupport.initSheets()
  sheetId = sheetSupport.addSheet(sheets, SPREADSHEET_ID, "Stalls")

  print(len(values[0])-1)

  sheetSupport.writeSheet(sheets, SPREADSHEET_ID, 'Stalls!A1:'+getNotation(len(values[0])), values)
  sheetSupport.formatSheet(sheets, SPREADSHEET_ID, sheetId, len(values), len(values[0]))
  sheetSupport.paintCells(sheets, SPREADSHEET_ID, sheetId, 3, [x[0] for x in perc].index('Sum'))
