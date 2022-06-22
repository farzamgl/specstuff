from __future__ import division
import sheetSupport
import argparse
import os.path
from pprint import pprint

SPREADSHEET_ID = '1Ia4TAmpXvCf8ghn-MUPRBDLMCQxKEmr7vfPpCJsK4iU'
sheetName = 'tmp'
plotSheetName = sheetName + 'Plots'

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def read_data(filename):
    f = open(filename, 'r')
    data = {}
    next(f)
    for line in f:
      (key, val) = line.split()
      data[key] = int(val)
    f.close()
    return data

def getNotation(n):
    string = ''
    while n > 0:
        n, rem = divmod(n-1, 26)
        string = chr(65 + rem) + string
    return string

def basicFormat(self, spreadsheetId, sheetId):
  body = {
    'requests': [
      {
        'repeatCell': {
          'cell': {
            'userEnteredFormat': {
              'numberFormat': {
                'type': 'NUMBER',
                'pattern': '#0.00'
              },
              'textFormat': {
                'fontFamily': 'Calibri,sans-serif',
                'fontSize': 10,
                'bold': False,
                'italic': False,
                'strikethrough': False,
                'underline': False,
              },
            }
          },
          'range': {
            'sheetId': sheetId,
          },
          'fields': 'userEnteredFormat'
        }
      },
    ]
  }
  self.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()


def addCols(self, spreadsheetId, sheetId, ncols):
  body = {
    "requests": [
      {
        "appendDimension": {
          "sheetId": sheetId,
          "dimension": "COLUMNS",
          "length": ncols
        }
      }
    ]
  }
  self.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

def basicChart(self, spreadsheetId, sourceSheetId, destSheetId, title, cords, nrows, cols):
  createChart(self, spreadsheetId, sourceSheetId, destSheetId, title, cords, nrows, cols, 0)

def stackChart(self, spreadsheetId, sourceSheetId, destSheetId, title, cords, nrows, cols):
  createChart(self, spreadsheetId, sourceSheetId, destSheetId, title, cords, nrows, cols, 1)

def createChart(self, spreadsheetId, sourceSheetId, destSheetId, title, cords, nrows, cols, stacked):
  series = []
  for col in cols:
    entry = {
      'series': {
        'sourceRange': {
          'sources': [
            {
              'sheetId': sourceSheetId,
              'startRowIndex': 0,
              'endRowIndex': nrows,
              'startColumnIndex': col,
              'endColumnIndex': col+1
            }
          ]
        }
      },
      "targetAxis": "LEFT_AXIS"
    }
    series.append(entry)

  body = {
    'requests': [
      {
        'addChart': {
          'chart': {
            'spec': {
              'title': title,
              'basicChart': {
                'chartType': 'COLUMN',
                'legendPosition': 'BOTTOM_LEGEND',
                'stackedType': 'NOT_STACKED' if (stacked == 0) else 'STACKED',
                'axis': [],
                'domains': [
                  {
                    'domain': {
                      'sourceRange': {
                        'sources': [
                          {
                            'sheetId': sourceSheetId,
                            'startRowIndex': 0,
                            'endRowIndex': nrows,
                            'startColumnIndex': 0,
                            'endColumnIndex': 1
                          }
                        ]
                      }
                    }
                  }
                ],
                'series': series,
                'headerCount': 1
              }
            },
            'position': {
              'overlayPosition': {
                'anchorCell': {
                  'sheetId': destSheetId,
                  'rowIndex': cords[0],
                  'columnIndex': cords[1]
                },
                'widthPixels': 900,
                'heightPixels': 400
              }
            }
          }
        }
      },
    ]
  }
  self.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('files', nargs='+', help='List of files')
  parser.add_argument('--ar_path', type=dir_path)
  parser.add_argument('--bp_path', type=dir_path)
  args = parser.parse_args()

  ar_files = [args.ar_path + f for f in args.files]
  bp_files = [args.bp_path + f for f in args.files]

  values = []
  for filename in args.files:

    ar = read_data(args.ar_path+filename)
    bp = read_data(args.bp_path+filename)

    groups = [('Benchmark', os.path.splitext(filename)[0])]

    bp_ic = bp['ic_miss'] + bp['ic_l2_miss'] + bp['ic_dma']
    #ar_ic = ar['ic_miss'] + ar['ic_dma']

    bp_dc = bp['dc_miss'] + bp['dc_l2_miss'] + bp['dc_dma']
    #ar_dc = ar['dc_miss_is'] + ar['dc_dma_is'] + ar['dc_miss_ld'] + ar['dc_dma_ld'] + ar['dc_miss_cmt'] + ar['dc_dma_cmt']
    #ar_dc_dma = ar['dc_dma_is'] + ar['dc_dma_ld'] + ar['dc_dma_cmt']

    bp_br = bp['branch_override'] + bp['ret_override'] + bp['mispredict']
    ar_br = ar['bp_haz'] + ar['br_miss']

    bp_mul = bp['mul_dep']
    #ar_mul = ar['mul_haz']

    bp_idiv = bp['sb_iraw_dep'] + bp['sb_iwaw_dep'] + bp['idiv_haz']
    #ar_idiv = ar['div_busy']

    bp_fpu = bp['sb_fraw_dep'] + bp['sb_fwaw_dep'] + bp['fdiv_haz'] + bp['aux_dep'] + bp['fma_dep']
    #ar_fpu = ar['fpu_busy']

    bp_lsu = bp['load_dep']
    #ar_lsu = ar['ld_pipe'] + ar['ld_grant'] + ar['st_pipe'] + ar['sbuf_spec'] + ar['dc_pipe_is'] + ar['dc_pipe_ld'] + ar['dc_pipe_cmt']

    bp_control = bp['control_haz']
    #ar_control = ar['fence'] + ar['csr_buf'] + ar['csr_flush']

    bp_misc = bp['long_haz']
    #ar_misc = ar['sb_full'] + ar['waw_reorder']

    bp_other = bp['mcycle'] - bp['minstret'] - bp_ic - bp_dc - bp_br - bp_idiv - bp_fpu - bp_lsu - bp_control - bp_mul - bp_misc
    #ar_other = ar['mcycle'] - ar['minstret'] - ar_ic - ar_dc - ar_br - ar_idiv - ar_fpu - ar_lsu - ar_control - ar_mul - ar_misc

    ### Speedup
    groups.append(('BP IPC', (bp['minstret']/bp['mcycle'])))
    groups.append(('AR IPC', (ar['minstret']/ar['mcycle'])))
    groups.append(('BP speedup', (ar['mcycle']/bp['mcycle'])))

    ### BP L1 miss
    groups.append(('BP avg wDMA', (bp['e_wdma_wait'] / bp['e_wdma_cnt'])))
    #groups.append(('AR avg wDMA', (ar['e_wdma_wait'] / ar['e_wdma_cnt'])))
    groups.append(('BP avg rDMA', (bp['e_rdma_wait'] / bp['e_rdma_cnt'])))
    #groups.append(('AR avg rDMA', (ar['e_rdma_wait'] / ar['e_rdma_cnt'])))

    groups.append(('BP ifetch DMA overlap', 1 - (bp['e_dma_ic'] / (bp['e_rdma_ic'] + bp['e_wdma_ic']))))
    groups.append(('BP dfetch DMA overlap', 1 - (bp['e_dma_dc_fetch'] / (bp['e_rdma_dc_fetch'] + bp['e_wdma_dc_fetch']))))

    groups.append(('BP ifetch DMA L2 visiblity', (bp['e_l2_ic_dma'] / bp['e_dma_ic'])))
    groups.append(('BP dfetch DMA L2 visiblity', (bp['e_l2_dc_fetch_dma'] / bp['e_dma_dc_fetch'])))
    groups.append(('BP devict DMA L2 visiblity', (bp['e_l2_dc_evict_dma'] / bp['e_dma_dc_evict'])))

    groups.append(('BP avg ifetch L2 miss overhead', ((bp['e_l2_ic_miss'] - bp['e_l2_ic_dma']) / bp['e_l2_ic_miss_cnt'])))
    groups.append(('BP avg dfetch L2 miss overhead', ((bp['e_l2_dc_fetch_miss'] - bp['e_l2_dc_fetch_dma']) / bp['e_l2_dc_fetch_miss_cnt'])))
    groups.append(('BP avg devict L2 miss overhead', ((bp['e_l2_dc_evict_miss'] - bp['e_l2_dc_evict_dma']) / bp['e_l2_dc_evict_miss_cnt'])))

    groups.append(('BP avg ifetch L2 access overhead', ((bp['e_l2_ic'] - bp['e_l2_ic_miss']) / bp['e_l2_ic_cnt'])))
    groups.append(('BP avg dfetch L2 access overhead', ((bp['e_l2_dc_fetch'] - bp['e_l2_dc_fetch_miss']) / bp['e_l2_dc_fetch_cnt'])))
    groups.append(('BP avg devict L2 access overhead', ((bp['e_l2_dc_evict'] - bp['e_l2_dc_evict_miss']) / bp['e_l2_dc_evict_cnt'])))

    groups.append(('BP ifetch L2 DMA share', (bp['e_l2_ic_dma'] / bp['e_l2_ic_cnt'])))
    groups.append(('BP ifetch L2 miss overhead share', ((bp['e_l2_ic_miss'] - bp['e_l2_ic_dma']) / bp['e_l2_ic_cnt'])))
    groups.append(('BP ifetch L2 access overhead share', ((bp['e_l2_ic'] - bp['e_l2_ic_miss']) / bp['e_l2_ic_cnt'])))

    groups.append(('BP dfetch L2 DMA share', (bp['e_l2_dc_fetch_dma'] / bp['e_l2_dc_fetch_cnt'])))
    groups.append(('BP dfetch L2 miss overhead share', ((bp['e_l2_dc_fetch_miss'] - bp['e_l2_dc_fetch_dma']) / bp['e_l2_dc_fetch_cnt'])))
    groups.append(('BP dfetch L2 access overhead share', ((bp['e_l2_dc_fetch'] - bp['e_l2_dc_fetch_miss']) / bp['e_l2_dc_fetch_cnt'])))

    groups.append(('BP devict L2 DMA share', (bp['e_l2_dc_evict_dma'] / bp['e_l2_dc_evict_cnt'])))
    groups.append(('BP devict L2 miss overhead share', ((bp['e_l2_dc_evict_miss'] - bp['e_l2_dc_evict_dma']) / bp['e_l2_dc_evict_cnt'])))
    groups.append(('BP devict L2 access overhead share', ((bp['e_l2_dc_evict'] - bp['e_l2_dc_evict_miss']) / bp['e_l2_dc_evict_cnt'])))

    groups.append(('BP ifetch L2 miss rate', (bp['e_l2_ic_miss_cnt'] / bp['e_l2_ic_cnt'])))
    groups.append(('BP dfetch L2 miss rate', (bp['e_l2_dc_fetch_miss_cnt'] / bp['e_l2_dc_fetch_cnt'])))
    groups.append(('BP devict L2 miss rate', (bp['e_l2_dc_evict_miss_cnt'] / bp['e_l2_dc_evict_cnt'])))

    groups.append(('BP L2 ifetch I$ visiblity', (bp['e_ic_miss_l2_ic'] / bp['e_l2_ic'])))
    groups.append(('BP L2 dfetch I$ visiblity', (bp['e_ic_miss_l2_dc_fetch'] / bp['e_l2_dc_fetch'])))
    groups.append(('BP L2 devict I$ visiblity', (bp['e_ic_miss_l2_dc_evict'] / bp['e_l2_dc_evict'])))

    groups.append(('BP L2 ifetch D$ visiblity', (bp['e_dc_miss_l2_ic'] / bp['e_l2_ic'])))
    groups.append(('BP L2 dfetch D$ visiblity', (bp['e_dc_miss_l2_dc_fetch'] / bp['e_l2_dc_fetch'])))
    groups.append(('BP L2 devict D$ visiblity', (bp['e_dc_miss_l2_dc_evict'] / bp['e_l2_dc_evict'])))

    groups.append(('BP avg I$ miss overhead', ((bp['e_ic_miss'] - bp['e_ic_miss_l2_ic'] - bp['e_ic_miss_l2_dc_fetch'] - bp['e_ic_miss_l2_dc_evict']) / bp['e_ic_miss_cnt'])))
    groups.append(('BP avg D$ miss overhead', ((bp['e_dc_miss'] - bp['e_dc_is_busy'] - bp['e_dc_miss_l2_ic'] - bp['e_dc_miss_l2_dc_fetch'] - bp['e_dc_miss_l2_dc_evict']) / (bp['e_dc_miss_cnt'] - bp['e_dc_is_busy_cnt']))))

    groups.append(('BP I$ miss L2 ifetch share', (bp['e_ic_miss_l2_ic'] / bp['e_ic_miss_cnt'])))
    groups.append(('BP I$ miss L2 dfetch share', (bp['e_ic_miss_l2_dc_fetch'] / bp['e_ic_miss_cnt'])))
    groups.append(('BP I$ miss L2 devict share', (bp['e_ic_miss_l2_dc_evict'] / bp['e_ic_miss_cnt'])))
    groups.append(('BP I$ miss L1 overhead share', ((bp['e_ic_miss'] - bp['e_ic_miss_l2_ic'] - bp['e_ic_miss_l2_dc_fetch'] - bp['e_ic_miss_l2_dc_evict']) / bp['e_ic_miss_cnt'])))

    groups.append(('BP D$ miss L2 ifetch share', (bp['e_dc_miss_l2_ic'] / (bp['e_dc_miss_cnt'] - bp['e_dc_is_busy_cnt']))))
    groups.append(('BP D$ miss L2 dfetch share', (bp['e_dc_miss_l2_dc_fetch'] / (bp['e_dc_miss_cnt'] - bp['e_dc_is_busy_cnt']))))
    groups.append(('BP D$ miss L2 devict share', (bp['e_dc_miss_l2_dc_evict'] / (bp['e_dc_miss_cnt'] - bp['e_dc_is_busy_cnt']))))
    groups.append(('BP D$ miss L1 overhead share', ((bp['e_dc_miss'] - bp['e_dc_is_busy'] - bp['e_dc_miss_l2_ic'] - bp['e_dc_miss_l2_dc_fetch'] - bp['e_dc_miss_l2_dc_evict']) / (bp['e_dc_miss_cnt'] - bp['e_dc_is_busy_cnt']))))
    #groups.append(('BP D$ miss UCE busy share', (bp['e_dc_is_busy'] / bp['e_dc_miss_cnt'])))

    groups.append(('BP I$ miss rate', (bp['e_ic_miss_cnt'] / bp['e_ic_req_cnt'])))
    groups.append(('BP D$ miss rate', ((bp['e_dc_miss_cnt'] - bp['e_dc_is_busy_cnt']) / bp['e_dc_req_cnt'])))

    groups.append(('BP I$ miss stall / tot', ((bp['ic_miss'] + bp['ic_l2_miss'] + bp['ic_dma']) / bp['e_ic_miss'])))
    groups.append(('BP D$ miss stall / tot', ((bp['dc_miss'] + bp['dc_l2_miss'] + bp['dc_dma']) / bp['e_dc_miss'])))

    ### AR L1 miss
    groups.append(('AR avg I$ rDMA', (ar['e_rdma_ic'] / ar['e_rdma_ic_cnt'])))
    groups.append(('AR avg D$ rDMA', (ar['e_rdma_dc'] / ar['e_rdma_dc_cnt'])))
    groups.append(('AR avg D$ wDMA', (ar['e_wdma_dc'] / ar['e_wdma_dc_cnt'])))
 
    groups.append(('AR I$ rDMA visiblity', (ar['e_ic_rdma'] / ar['e_rdma_ic'])))
    groups.append(('AR D$ LD rDMA visiblity', (ar['e_ld_rdma'] / ar['e_rdma_ld'])))
    groups.append(('AR D$ LD wDMA visiblity', (ar['e_ld_wdma'] / ar['e_wdma_ld'])))
    groups.append(('AR D$ ST rDMA visiblity', (ar['e_st_rdma'] / ar['e_rdma_st'])))
    groups.append(('AR D$ ST wDMA visiblity', (ar['e_st_wdma'] / ar['e_wdma_st'])))

#    ### other
#    groups.append(('BP branch', (bp_br / bp['minstret'])))
#    groups.append(('AR branch', (ar_br / ar['minstret'])))
#    groups.append(('BP mul', (bp_mul / bp['minstret'])))
#    groups.append(('AR mul', (ar_mul / ar['minstret'])))
#    groups.append(('BP idiv', (bp_idiv / bp['minstret'])))
#    groups.append(('AR idiv', (ar_idiv / ar['minstret'])))
#    groups.append(('BP fpu', (bp_fpu / bp['minstret'])))
#    groups.append(('AR fpu', (ar_fpu / ar['minstret'])))
#    groups.append(('BP lsu', (bp_lsu / bp['minstret'])))
#    groups.append(('AR lsu', (ar_lsu / ar['minstret'])))
#    groups.append(('BP control', (bp_control / bp['minstret'])))
#    groups.append(('AR control', (ar_control / ar['minstret'])))
#    groups.append(('BP misc', (bp_misc / bp['minstret'])))
#    groups.append(('AR misc', (ar_misc / ar['minstret'])))
#    groups.append(('BP other', (bp_other / bp['minstret'])))
#    groups.append(('AR other', (ar_other / ar['minstret'])))

    if len(values) == 0:
      values.append([x[0] for x in groups])
    values.append([x[1] for x in groups])

  sheets = sheetSupport.initSheets()
  sheetId = sheetSupport.addSheet(sheets, SPREADSHEET_ID, sheetName)
  DMAplotSheetId = sheetSupport.addSheet(sheets, SPREADSHEET_ID, plotSheetName+'DMA')
  ARplotSheetId = sheetSupport.addSheet(sheets, SPREADSHEET_ID, plotSheetName+'AR')

  print(len(values[0])-1)

  sheetSupport.writeSheet(sheets, SPREADSHEET_ID, sheetName+'!A1:'+getNotation(len(values[0])), values)
  basicFormat(sheets, SPREADSHEET_ID, sheetId)

  addCols(sheets, SPREADSHEET_ID, DMAplotSheetId, 100)
  addCols(sheets, SPREADSHEET_ID, ARplotSheetId, 100)

  ##################################### Speedup
#  basicChart(sheets, SPREADSHEET_ID, sheetId, IPCplotSheetId, 'IPC', [0,0], len(args.files)+1, [values[0].index('BP IPC'),values[0].index('AR IPC')])
#  basicChart(sheets, SPREADSHEET_ID, sheetId, IPCplotSheetId, 'BP speedup', [20,0], len(args.files)+1, [values[0].index('BP speedup')])

  ##################################### AR DMA
  basicChart(sheets, SPREADSHEET_ID, sheetId, ARplotSheetId, 'AR avg I$ rDMA', [0,0], len(args.files)+1, [values[0].index('AR avg I$ rDMA')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, ARplotSheetId, 'AR avg D$ rDMA', [20,0], len(args.files)+1, [values[0].index('AR avg D$ rDMA')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, ARplotSheetId, 'AR avg D$ wDMA', [20,9], len(args.files)+1, [values[0].index('AR avg D$ wDMA')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, ARplotSheetId, 'AR I$ rDMA visiblity', [40,0], len(args.files)+1, [values[0].index('AR I$ rDMA visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, ARplotSheetId, 'AR D$ LD rDMA visiblity', [60,0], len(args.files)+1, [values[0].index('AR D$ LD rDMA visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, ARplotSheetId, 'AR D$ LD wDMA visiblity', [60,9], len(args.files)+1, [values[0].index('AR D$ LD wDMA visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, ARplotSheetId, 'AR D$ ST rDMA visiblity', [80,0], len(args.files)+1, [values[0].index('AR D$ ST rDMA visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, ARplotSheetId, 'AR D$ ST wDMA visiblity', [80,9], len(args.files)+1, [values[0].index('AR D$ ST wDMA visiblity')])




  ##################################### DMA
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg wDMA', [0,0], len(args.files)+1, [values[0].index('BP avg wDMA')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg rDMA', [0,9], len(args.files)+1, [values[0].index('BP avg rDMA')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP ifetch DMA overlap', [20,0], len(args.files)+1, [values[0].index('BP ifetch DMA overlap')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP dfetch DMA overlap', [20,9], len(args.files)+1, [values[0].index('BP dfetch DMA overlap')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP ifetch DMA L2 visiblity', [40,0], len(args.files)+1, [values[0].index('BP ifetch DMA L2 visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP dfetch DMA L2 visiblity', [40,9], len(args.files)+1, [values[0].index('BP dfetch DMA L2 visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP devict DMA L2 visiblity', [40,18], len(args.files)+1, [values[0].index('BP devict DMA L2 visiblity')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg ifetch L2 miss overhead', [60,0], len(args.files)+1, [values[0].index('BP avg ifetch L2 miss overhead')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg dfetch L2 miss overhead', [60,9], len(args.files)+1, [values[0].index('BP avg dfetch L2 miss overhead')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg devict L2 miss overhead', [60,18], len(args.files)+1, [values[0].index('BP avg devict L2 miss overhead')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg ifetch L2 access overhead', [80,0], len(args.files)+1, [values[0].index('BP avg ifetch L2 access overhead')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg dfetch L2 access overhead', [80,9], len(args.files)+1, [values[0].index('BP avg dfetch L2 access overhead')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg devict L2 access overhead', [80,18], len(args.files)+1, [values[0].index('BP avg devict L2 access overhead')])

  stackChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg L2 ifetch breakdown', [100,0], len(args.files)+1, [values[0].index('BP ifetch L2 DMA share'),values[0].index('BP ifetch L2 miss overhead share'), values[0].index('BP ifetch L2 access overhead share')])

  stackChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg L2 dfetch breakdown', [100,9], len(args.files)+1, [values[0].index('BP dfetch L2 DMA share'),values[0].index('BP dfetch L2 miss overhead share'), values[0].index('BP dfetch L2 access overhead share')])

  stackChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg L2 devict breakdown', [100,18], len(args.files)+1, [values[0].index('BP devict L2 DMA share'),values[0].index('BP devict L2 miss overhead share'), values[0].index('BP devict L2 access overhead share')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP ifetch L2 miss rate', [120,0], len(args.files)+1, [values[0].index('BP ifetch L2 miss rate')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP dfetch L2 miss rate', [120,9], len(args.files)+1, [values[0].index('BP dfetch L2 miss rate')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP devict L2 miss rate', [120,18], len(args.files)+1, [values[0].index('BP devict L2 miss rate')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP L2 ifetch I$ visiblity', [140,0], len(args.files)+1, [values[0].index('BP L2 ifetch I$ visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP L2 dfetch I$ visiblity', [140,9], len(args.files)+1, [values[0].index('BP L2 dfetch I$ visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP L2 devict I$ visiblity', [140,18], len(args.files)+1, [values[0].index('BP L2 devict I$ visiblity')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP L2 ifetch D$ visiblity', [160,0], len(args.files)+1, [values[0].index('BP L2 ifetch D$ visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP L2 dfetch D$ visiblity', [160,9], len(args.files)+1, [values[0].index('BP L2 dfetch D$ visiblity')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP L2 devict D$ visiblity', [160,18], len(args.files)+1, [values[0].index('BP L2 devict D$ visiblity')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg I$ miss overhead', [180,0], len(args.files)+1, [values[0].index('BP avg I$ miss overhead')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg D$ miss overhead', [180,9], len(args.files)+1, [values[0].index('BP avg D$ miss overhead')])

  stackChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg I$ miss breakdown', [200,0], len(args.files)+1, [values[0].index('BP I$ miss L2 ifetch share'),values[0].index('BP I$ miss L2 dfetch share'), values[0].index('BP I$ miss L2 devict share'), values[0].index('BP I$ miss L1 overhead share')])

  stackChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP avg D$ miss breakdown', [200,9], len(args.files)+1, [values[0].index('BP D$ miss L2 ifetch share'),values[0].index('BP D$ miss L2 dfetch share'), values[0].index('BP D$ miss L2 devict share'), values[0].index('BP D$ miss L1 overhead share')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP I$ miss rate', [220,0], len(args.files)+1, [values[0].index('BP I$ miss rate')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP D$ miss rate', [220,9], len(args.files)+1, [values[0].index('BP D$ miss rate')])

  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP I$ miss stall to event ratio', [240,0], len(args.files)+1, [values[0].index('BP I$ miss stall / tot')])
  basicChart(sheets, SPREADSHEET_ID, sheetId, DMAplotSheetId, 'BP D$ miss stall to event ratio', [240,9], len(args.files)+1, [values[0].index('BP D$ miss stall / tot')])

