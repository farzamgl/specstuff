from __future__ import division
import sheetSupport
import argparse
import os.path
from pprint import pprint

SPREADSHEET_ID = '1weV998msz8swoQPR78iDW5thry7FIFesaX_a04lkIA0'
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
    perc.append(('ipc', data['minstret']/data['mcycle']))
    perc.append(('mem instr %', data['mem_instr']/data['minstret']))
    perc.append(('write DMA cnt', data['wdma_cnt']))
    perc.append(('read DMA cnt', data['rdma_cnt']))
    perc.append(('avg write DMA', data['wdma_wait']/data['wdma_cnt']))
    perc.append(('avg read DMA', data['rdma_wait']/data['rdma_cnt']))
    perc.append(('DMA stall', data['dma']))
    perc.append(('DMA stall ratio', data['dma']/data['dma_wait']))
    perc.append(('L2 miss cnt', data['l2_miss_cnt']))
    perc.append(('avg L2 miss', data['l2_miss_wait']/data['l2_miss_cnt']))
    perc.append(('L2(-DMA) stall', data['l2_miss']))
    perc.append(('L2 stall ratio', (data['l2_miss']+data['dma'])/data['l2_miss_wait']))

    fileNum += 1

    if len(values) == 0:
      values.append([x[0] for x in perc])
    values.append([x[1] for x in perc])

  sheets = sheetSupport.initSheets()
  sheetId = sheetSupport.addSheet(sheets, SPREADSHEET_ID, sheetName)

  print(len(values[0])-1)

  sheetSupport.writeSheet(sheets, SPREADSHEET_ID, sheetName+'!A1:'+getNotation(len(values[0])), values)
  #sheetSupport.formatSheet(sheets, SPREADSHEET_ID, sheetId, len(values), len(values[0]))
  #sheetSupport.paintCells(sheets, SPREADSHEET_ID, sheetId, 3, [x[0] for x in perc].index('Sum'))
