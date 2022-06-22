from __future__ import division
import sheetSupport
import argparse
import os.path
from pprint import pprint

SPREADSHEET_ID = '1Ia4TAmpXvCf8ghn-MUPRBDLMCQxKEmr7vfPpCJsK4iU'
sheetName = 'new CVA6 Events'

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


if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('files', nargs='+', help='List of files')
  parser.add_argument('--ar_path', type=dir_path)
  parser.add_argument('--bp_path', type=dir_path)
  args = parser.parse_args()

  ar_files = [args.ar_path + f for f in args.files]
  bp_files = [args.bp_path + f for f in args.files]

  values = []
  fileNum = 0

  for filename in args.files:

    ar_data = read_data(args.ar_path+filename)
    bp_data = read_data(args.bp_path+filename)

    perc = [('Benchmark', os.path.splitext(filename)[0])]

    perc.append(('br cnt ratio', ar_data['e_br_cnt']/bp_data['e_br_cnt']))
    perc.append(('jalr cnt ratio', ar_data['e_jalr_cnt']/bp_data['e_jalr_cnt']))
    perc.append(('ret cnt ratio', ar_data['e_ret_cnt']/bp_data['e_ret_cnt']))
    perc.append(('BP br miss %', bp_data['e_br_miss']/bp_data['e_br_cnt']))
    perc.append(('AR br miss %', ar_data['e_br_miss']/ar_data['e_br_cnt']))
    perc.append(('BP jalr miss %', bp_data['e_jalr_miss']/bp_data['e_jalr_cnt']))
    perc.append(('AR jalr miss %', ar_data['e_jalr_miss']/ar_data['e_jalr_cnt']))
    perc.append(('BP ret miss %', bp_data['e_ret_miss']/bp_data['e_ret_cnt']))
    perc.append(('AR ret miss %', ar_data['e_ret_miss']/ar_data['e_ret_cnt']))
    perc.append(('BP I$ miss %', bp_data['e_ic_miss_cnt']/bp_data['e_ic_req_cnt']))
    perc.append(('AR I$ miss %', ar_data['e_ic_miss_cnt']/ar_data['e_ic_req_cnt']))
    perc.append(('BP D$ miss %', bp_data['e_dc_miss_cnt']/bp_data['e_dc_req_cnt']))
    perc.append(('AR D$ miss %', ar_data['e_dc_miss_cnt']/ar_data['e_dc_req_cnt']))
    #perc.append(('div cnt ratio', ar_data['e_div_cnt']/bp_data['e_div_cnt']))
    #perc.append(('div avg wait', data['e_div_wait']/data['e_div_cnt']))

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
