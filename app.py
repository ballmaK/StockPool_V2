# -*- coding: utf-8 -*-
#!/usr/bin/python
import re
import os
import sys
import time
import random
import httplib
import json
import datetime
import traceback
import threadpool
import Queue

from math import ceil
from optparse import OptionParser,OptionGroup

DATADIR="data/historys"
DATEHIS="data/date-historys"
PH=50
PL=-15
STOCKINFO={}


def __getFullDate(yearStart,yearEnd):
    for year in range(yearStart,yearEnd+1):
        year = str(year)
        startdate = year+'0101'
        enddate = year+'1231'
        timestam = time.time()
        url = "q.stock.sohu.com"
        path = "/hisHq?code=zs_000001&start=%s&end=%s&stat=1&order=D&period=d&callback=historySerchHandler&rt=jsonp&r=%s" % (startdate, enddate, timestam)
        content = __httpGetContent(url, path)
        datelist = [date[0].replace('-','') for date in json.loads(content[len('historySerchHandler('):-2].replace('%',''), encoding="GBK")[0]['hq']]
        fd = open(os.path.join(DATEHIS,year), 'w+')
        fd.write(json.dumps(datelist))
        fd.close()

def __getTurnOver(code, year):    
    timestam = time.time()
    dateStart = year+'0101'
    dateEnd = year +'1231'
    url = "q.stock.sohu.com"
    path = "/hisHq?code=cn_%s&start=%s&end=%s&stat=1&order=D&period=d&callback=historySerchHandler&rt=jsonp&r=%s" % (code, dateStart, dateEnd, timestam)
    content = __httpGetContent(url, path)
    try:
        jsonp = json.loads(content[len('historySerchHandler('):-2].replace('%',''), encoding="GBK")
        stockinfo = jsonp[0]['hq']
    except:
        stockinfo = []
    
    datedict = {}
    for date in stockinfo:
        datedict[date[0].replace('-','')] = date[9]
        
    if not stockinfo:
        datedict[dateStart] = 0
    
    return datedict

def getShangHaiInfo(year):
    timestam = time.time()
    dateStart = year+'0101'
    dateEnd = year +'1231'
    url = "q.stock.sohu.com"
    path = "/hisHq?code=zs_000001&start=%s&end=%s&stat=1&order=D&period=d&callback=historySerchHandler&rt=jsonp&r=%s" % (dateStart, dateEnd, timestam)
    content = __httpGetContent(url, path)
    try:
        jsonp = json.loads(content[len('historySerchHandler('):-2].replace('%',''), encoding="GBK")
        stockinfo = jsonp[0]['hq']
    except:
        stockinfo = []
    sh = {}
    for info in stockinfo:
        shStock = {}
        date = info[0]#.replace('-','')
        shStock['date'] = date
        shStock['start'] = float(info[1])
        shStock['end'] = float(info[2])
        shStock['low'] = float(info[5])
        shStock['high'] = float(info[6])
        shStock['volume'] = int(ceil(float(info[7])))
        shStock['total'] = int(ceil(float(info[8])))
        sh[date]=shStock
    return sh

def getShangHaiBR(stock):
    stock_date = stock.keys()
    stocklist = [(k,stock[k]) for k in sorted(stock_date, reverse=True)]
    sorted_stock_date = [s[0] for s in stocklist]
    for date in stock_date:
        if date:
            try:
                index = sorted_stock_date.index(date)
            except:
                delist = True
                index = 0
        else:
            index = 0
        stockdayslist = stocklist[index:index+20]
        #print stocklist20
        h, l, a =  __getHLIn(stockdayslist)
        BR = a/(h/l)
        stock[date]['BR'] = BR
        now_price = stocklist[index][1]['end'] 
        
        if index >= 1:
            day1 = stocklist[index-1][1]['end']             #1日后收盘价
            day1_p = round((day1 - now_price)/now_price, 3) * 100   #1日后涨跌幅
            
        if index >= 3:
            day3 = stocklist[index-3][1]['end']             #3日后收盘价
            day3_p = round((day3 - now_price)/now_price, 3) * 100   #3日后涨跌幅
            
        if index >= 5:
            day5 = stocklist[index-5][1]['end']             #5日后收盘价
            day5_p = round((day5 - now_price)/now_price, 3) * 100   #5日后涨跌幅
        stock[date]['1d'] = day1_p
        stock[date]['3d'] = day3_p
        stock[date]['5d'] = day5_p
        stock[date]['price'] = now_price
    #print "%-8s %-15s %8s %8s %8s" % ('DATE', 'BR-20', '1-DAYS', '3-DAYS', '5-DAYS')
    #print "%s,%s,%s,%s,%s,%s" % ('DATE', 'BR-20', 'PRICE', '1-DAYS', '3-DAYS', '5-DAYS')
    total = b = 0 
    for s in sorted_stock_date:
        #print "%-8s %-15.2f %8.2f %8.2f %8.2f" % (stock[s]['date'],stock[s]['BR'],stock[s]['1d'],stock[s]['3d'],stock[s]['5d'])
        aa = stock[s]['BR']/stock[s]['total']
        #if aa <= 0.72:
        #    total += 1
        #    print "%s,%.2f,%d,%.2f,%d,%.2f" % (stock[s]['date'],stock[s]['BR'],stock[s]['price'],stock[s]['1d'],stock[s]['total'],stock[s]['BR']/stock[s]['total'])
        #    if stock[s]['1d'] <= 0:
        #        b += 1
        print "%s,%.2f,%d,%.2f,%d,%.2f" % (stock[s]['date'],stock[s]['BR'],stock[s]['price'],stock[s]['1d'],stock[s]['total'],stock[s]['BR']/stock[s]['total'])

    #print "TOTAL: %s, BINGO: %s" % (total, b)
    #return stock
    
    

def __convert_inner(stock, todict, stock_dict={}):
    stock_day = stock.split(',')
    if all(stock_day):
        date = stock_day[0] #日期
        start = float(stock_day[1]) #开盘价格
        high = float(stock_day[2]) #最高价格
        low = float(stock_day[3]) #最低价格
        end = float(stock_day[4]) #收盘价格
        volume = int(ceil(float(stock_day[5]))) #成交量
        total = int(ceil(float(stock_day[6]))) #成交额
        try:
            to = float(todict[date])
        except:
            to = 0.0
        #print stock, date, to

        stock_dict[date] = {
            "date": date,
            'start': start,
            'high': high,
            'low': low,
            'end': end,
            'volume': volume,
            'total': total,
            'to': to
        }
        return stock_dict

def __convert_day(content, todict):
    stock_list = content.split('=')[1].split('|')
    stock_dict = {}
    for stock in stock_list:
        if stock and stock.strip():
            __convert_inner(stock, todict, stock_dict)
    #print stock_dict
    return stock_dict

def __httpGetContent(url,path):
    conn = httplib.HTTPConnection(url,timeout=60)
    conn.request("GET", path)
    response = conn.getresponse()
    if response.status == 200:
        content = response.read()
    else:
        content = None
    return content

def __getHLIn(stocklist):
    high_list = []
    low_list = []
    money = 0
    for stock in stocklist:
        info = stock[1]
        high_list.append(info['high'])
        low_list.append(info['low'])
        #计算每10亿股相对成交额
        #if info['to'] != 0:
        #    rate = info['volume']/info['to'] / 1000000000
        money += info['total']#/rate
    return sorted(high_list)[-1], sorted(low_list)[0], money/20

def updateStockDayHistory(code, market, year='2015', type='b'):
    """
    http://qd.10jqka.com.cn/api.php?p=stock_day&info=k_sz_000005&year=2012,2013&fq=
    sz:深证
    sh:上海
    b向后复权
    q向前复权
    return dict
    """
    url = "qd.10jqka.com.cn"
    path = "/api.php?p=stock_day&info=k_%s_%s&year=%s&fq=%s" % (market, code, year, type)
    todict = __getTurnOver(code, year)
    try:
        content = __httpGetContent(url, path)
    except:
        content = None
        print code, ": Request failed ..."
    if content:
        #print code, ": Request success ..."
        stock_dict = __convert_day(content,todict)
        try:
            updateSingleLocalHistory(market, code, year, type, stock_dict)
        except Exception, e:
            #print traceback.print_exc(e)
            pass
        return stock_dict
    
def __getLocalStockInfo(code, market, year, type):
    code = market+code
    try:
        if code and year and type:
            fd = open(os.path.join(DATADIR,code, year, type, '%s' % code),'r')
            content = fd.read()
            fd.close()
        else:
            fd = None
    except Exception, e:
        #print traceback.print_exc(e)
        #if fd:
        #    fd.close()
        return
    return json.loads(content)    

def __getMemeryStockInfo(code, market, year, type):
    global STOCKINFO
    stockcode = market+code 
    if stockcode in STOCKINFO:
        return STOCKINFO[stockcode]
    else:
        codeMemInfo = __getLocalStockInfo(code, market, year, type)
        STOCKINFO[stockcode] = codeMemInfo
        return codeMemInfo
    
def updateSingleLocalHistory(market, code, year, type, stock_dict):
    code = market+code
    if os.path.exists(os.path.join(DATADIR,code)):
        if os.path.exists(os.path.join(DATADIR,code, year)):
            if os.path.exists(os.path.join(DATADIR,code, year, type)):
                fd = open(os.path.join(DATADIR,code, year, type, '%s' % code), 'w+')
                fd.write(json.dumps(stock_dict))
                fd.close()
            else:
                os.mkdir(os.path.join(DATADIR,code, year, type))
                fd = open(os.path.join(DATADIR,code, year, type, '%s' % code), 'w+')
                fd.write(json.dumps(stock_dict))
                fd.close()
        else:
            os.mkdir(os.path.join(DATADIR,code, year))
            os.mkdir(os.path.join(DATADIR,code, year, type))
            fd = open(os.path.join(DATADIR,code, year, type, '%s' % code), 'w+')
            fd.write(json.dumps(stock_dict))
            fd.close()
    else:
        os.mkdir(os.path.join(DATADIR,code))
        os.mkdir(os.path.join(DATADIR,code, year))
        os.mkdir(os.path.join(DATADIR,code, year, type))
        fd = open(os.path.join(DATADIR,code, year, type, '%s' % code), 'w+')
        fd.write(json.dumps(stock_dict))
        fd.close()

def isTradeDay(date):
    year = date[:4]
    fd = open(os.path.join(DATEHIS,year),'r')
    datelist = json.loads(fd.read())
    fd.close()
    try:
        index = datelist.index(date)
    except Exception,e:
        return False
    return True

def getNextDate(date,code=''):
    year = date[:4]
    fd = open(os.path.join(DATEHIS,year),'r')
    datelist = json.loads(fd.read())
    fd.close()
    #print datelist
    if datelist.index(date) >= 1:
        return datelist[datelist.index(date)-1]
    else:
        return datelist[0]
    
def getLastDate(date,code=''):
    year = date[:4]
    month = date[4:6]
    day = date[6:]
    if code:
        codeDateList = sorted(__getLocalStockInfo(code[2:], code[:2], year, type='b').keys(), reverse=True)
        delta = 1
        while 1:
            try:
                index = codeDateList.index(date)
                break
                #return codeDateList[index+1]
            except:
                newDate = datetime.datetime(int(year), int(month),int(day)) - datetime.timedelta(delta)
                year, month, day = str(newDate.year), '%02d' % newDate.month , '%02d' % newDate.day
                date = year+month+day 
                #return codeDateList[0]
        return codeDateList[index+1]
    else:
        fd = open(os.path.join(DATEHIS,year),'r')
        datelist = json.loads(fd.read())
        fd.close()
        delta = 1
        while 1:
            try:
                index = datelist.index(date)
                break
            except:
                print "Date is not deal day, choose one before it"
                #delta += 1
                newDate = datetime.datetime(int(year), int(month),int(day)) - datetime.timedelta(delta)
                year, month, day = str(newDate.year), '%02d' % newDate.month , '%02d' % newDate.day
                date = year+month+day 
            
        if index >= 1:
            return datelist[index+1]
        else:
            return datelist[0]

def getBR(stockCode,date="",days=20):
    code, market = stockCode[2:], stockCode[:2]
    #print code, market
    #stock = getStockDayHistory(code, market, year="2015", type="b")
    year = date[:4]
    stock = __getMemeryStockInfo(code, market, year, type="b")
    day1 = day3 = day5 = 'NaN'
    day1_p = day3_p = day5_p = 'NaN'
    now_volume = 'NaN'
    flow_volume = 0
    flow_money = 0
    delist = False
    if stock:
        stock_date = stock.keys()
        stocklist = [(k,stock[k]) for k in sorted(stock_date, reverse=True)]
        sorted_stock_date = [s[0] for s in stocklist]
        if date:
            try:
                index = sorted_stock_date.index(date)
            except:
                delist = True
                index = 0
        else:
            index = 0
        #print "date: ",sorted_stock_date[index]
        stockdayslist = stocklist[index:index+days]
        #print stocklist20
        h, l, a =  __getHLIn(stockdayslist)
        BR = a/(h/l)
        stList = getSTStock()
        now_price = stocklist[index][1]['end']              #当日收盘价
        now_volume = stocklist[index][1]['volume']
        turnover = stocklist[index][1]['to']
        if turnover == 0:
            flow_volume = 0
        else:
            flow_volume = now_volume / turnover * 100 / 100000000
            flow_money = flow_volume * now_price
        if now_volume <= 1000000 or delist or stockCode[2:] in stList:       #当天交易量小于10000手
            BR = 99999999999999999
        if index >= 1:
            day1 = stocklist[index-1][1]['end']             #1日后收盘价
            day1_p = round((day1 - now_price)/now_price, 3) * 100   #1日后涨跌幅
            
        if index >= 3:
            day3 = stocklist[index-3][1]['end']             #3日后收盘价
            day3_p = round((day3 - now_price)/now_price, 3) * 100   #3日后涨跌幅
            
        if index >= 5:
            day5 = stocklist[index-5][1]['end']             #5日后收盘价
            day5_p = round((day5 - now_price)/now_price, 3) * 100   #5日后涨跌幅
            
        return stockCode,BR,day1_p,day3_p,day5_p,now_volume,delist,flow_volume, flow_money
        #return BR,day1,day3,day5
    else:
        return stockCode,99999999999999999,day1_p,day3_p,day5_p,now_volume,delist,flow_volume,flow_money

def getStockCode():
    fdHA = open('data/HA.data','r')
    fdSA = open('data/SA.data','r')
    fdZX = open('data/ZX.data','r')
    HA = fdHA.read().split()
    SA = fdSA.read().split()
    ZX = fdZX.read().split()
    allStock = HA+SA+ZX
    allStockDict = {}
    for stock in allStock:
        k,v = stock.split(',')
        allStockDict[k] = v
    return allStockDict

def getSTStock():
    fdST = open('data/ST.data','r')
    ST = fdST.read().split()
    stDict = {}
    for st in ST:
        k,v = st.split(',')
        stDict[k] = v
    return stDict
        
def getResult(request, br_info):
    global sorted_s
    sorted_s.append(br_info)
    
def updateLocalHistory(year, type):
    '''
    year@string: 2015
    type@string: b=后复权;q=前复权
    '''
    allStockDict = getStockCode()
    stock_data = allStockDict.keys()
    q_size = len(stock_data)
    pool = threadpool.ThreadPool(10, q_size=q_size, resq_size=q_size)
    data = [([stock[2:], stock[:2], year, type],{}) for stock in stock_data]
    requests = threadpool.makeRequests(updateStockDayHistory, data)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    
def getBest(date="",length=50, days=20, printOut=False, filter=0.01):
    '''
    date@string: 20150729
    length@int:    
    days@int:    avg day
    '''
    #a = time.time()
    global sorted_s
    sorted_s = []
    allStockDict = getStockCode()
    stock_data = allStockDict.keys()
    q_size = len(stock_data)
    pool = threadpool.ThreadPool(1, q_size=q_size, resq_size=q_size)
    data = [([stock],{"date": date,"days": days}) for stock in stock_data]
    requests = threadpool.makeRequests(getBR, data, getResult)
    [pool.putRequest(req, False) for req in requests]  
    pool.wait()
    #print len(sorted_s)
    best50 = sorted(sorted_s, key=lambda sorted_s:sorted_s[1])#[:50]
    stList = getSTStock().keys()
    length = length
    best = []
    #print "DATE: %s" % date
    if printOut:
        print "==================================== TRADE DATE: %s ====================================" % date
        print "%-10s %-20s\t%-20s %-20s %-20s %-20s %-20s %-10s" % ("CODE","股票名字","BR-%s" % days,"1DAY_P","3DAY_P","5DAY_P","VOL","DELIST")
    for b in best50:
        if length > 0:
            if not filter:
                if printOut:
                    print "%-10s %-20s\t%-20.2f %-20s %-20s %-20s %-20s %-10s %10.2f %10.2f" % (b[0],allStockDict[b[0]],b[1],str(b[2]),str(b[3]),str(b[4]), b[5], b[6],b[7], b[8] ) 
                length -= 1
                best.append(b[0])
            else:
                if b[7] >= float(filter):
                    length -= 1
                    if printOut:
                        print "%-10s %-20s\t%-20.2f %-20s %-20s %-20s %-20s %-10s %10.2f %10.2f" % (b[0],allStockDict[b[0]],b[1],str(b[2]),str(b[3]),str(b[4]), b[5], b[6],b[7], b[8] ) 
                best.append(b[0])
    else:
        #print 'GET BEST TAKE: %s' % (time.time() - a)
        return best
    
def getFullCode(code):
    '''
    return@string: sz002891/sh600061 etc. 
    '''
    if code.find('sz') < 0 or code.find('sh') < 0:
        if code.find('60') == 0:
            code = 'sh' + code
        else:
            code = 'sz' + code
    return code

def getStockBR(stockCode, year='2015', type='b'):
    '''
    stockCode@string:     full code
    year@string:          year
    type@string:          b=后复权;q=前复权  
    return@int: 
    '''
    code, market = stockCode[2:], stockCode[:2]
    stockinfo = __getMemeryStockInfo(code, market, year, type)
    dateBRList = [(tuple([info]) + getBR(stockCode,info)) for info in stockinfo]
    s_date = sorted(dateBRList, key=lambda dateBRList:dateBRList[0])
    print "%-10s %-10s %-20s %-20s %-20s %-20s %-20s %-10s" % ("DATE","CODE","BR","1DAY_P","3DAY_P","5DAY_P","VOL","DELIST")
    for b in s_date:
        print "%-10s %-10s %-20s %-20s %-20s %-20s %-20s %-10s" % (b[0],b[1],str(b[2]),str(b[3]),str(b[4]), b[5], b[6], b[7] )
    
def updateStockCodeList():
    url = "quote.eastmoney.com"
    path = "/stocklist.html"    
    content = __httpGetContent(url, path)
    p_sh = 'sh\d+'
    p_sz = 'sz\d+'
    p_st = "ST(.+)\((\d+)"
    all = re.findall(p_sh, content) + re.findall(p_sz, content)
    HA = []
    SA = []
    ZX = []
    ST = []
    ST = [ t[1]+',*ST'+t[0].decode('GBK').encode('utf-8')+'\n' for t in re.findall(p_st, content)]
    #print ST
    #print content.decode('GBK')
    #print all
    for code in all:
        p_cn = '">(.+)\(' + code[2:]
        try:
            codeCN = re.findall(p_cn, content)[0].decode('GBK').encode('utf-8')
        except Exception, e:
            codeCN = 'NONAME'
        #print code, codeCN
        if code[2:].find('60') == 0:
            HA.append(code+','+codeCN+'\n')
        if code[2:].find('000') == 0:
            SA.append(code+','+codeCN+'\n')
        if code[2:].find('002') == 0:
            ZX.append(code+','+codeCN+'\n')


    fdHA = open('data/HA.data', 'w+')
    fdSA = open('data/SA.data', 'w+')
    fdZX = open('data/ZX.data', 'w+') 
    fdST = open('data/ST.data', 'w+') 
    fdHA.writelines(HA)  
    fdSA.writelines(SA)
    fdZX.writelines(ZX)
    fdST.writelines(ST)
    fdHA.close()
    fdSA.close()
    fdST.close() 
    #print content

def makeDeal(s_date, e_date, filter, codeinfo=[], rest_money=1000000, stockpick=10):
    '''
    s_date@string:     start date
    e_date@string:     end date
    codeinfo@list:     [('002063', 27.78, 300), ('002150', 21.78, 200), ('600604', 18.21, 250)]; 数量单位：(股票代码,买入价格,手数))]
    rest_money@int:    1000000
    '''
    a = time.time()
    if not codeinfo:
        #还未购买股票
        #根据上一个交易日BR，在前20随机得出5支股票
        suspension = False
        while not isTradeDay(s_date):
            s_date = getLastDate(s_date)
        #s_date = getLastDate(s_date)
        #lastDate = getLastDate(s_date)
        allStock = getBest(s_date,length=5000,days=20)
        bestlist = allStock[:20]
        codelist = []
        while len(codelist) < stockpick:
            index = random.randint(0, 19)
            if bestlist[index] not in codelist:
                codelist.append(bestlist[index])
        #codelist = [bestlist[random.randint(0,19)] for i in range(0,stockpick)]
        #infodict@dict: {codefull_0:stockyear_0, codefull_1:stockyear_1}
        infodict = {}
        #print codelist
        for bestcode in codelist:
            infodict.update({bestcode:__getMemeryStockInfo(bestcode[2:], bestcode[:2], s_date[:4], type='b')})
        #股票交易
        rest_total = 0
        #print 'TRADE DATE: ',s_date
        newCodeInfo = []
        print "==================================== TRADE DATE: %s ====================================" % s_date
        print "<<OP>> : %-10s %-6s %-6s %-6s %-6s %-6s %-6s %6s%% %8s" % ('CODE','BUY','SELL','NOW', 'DEALT', 'SUSPEN', 'RANGE', 'P/L', 'MONEY')
        for code in codelist:
            codeinfoyear = infodict[code]
            codeinfoday = codeinfoyear[s_date]
            range = allStock.index(code)
            buy = codeinfoday['start']                      #开盘价买入
            avgMoney = int(rest_money / stockpick)          #每支买入金钱
            buyNumber = int(avgMoney/buy/100)               #每支买入数量
            avgRestMoney = avgMoney - buy*buyNumber*100     #每支剩余金钱
            nextDate = getNextDate(s_date)                  #获取下一个交易日天日期
            rest_total += avgRestMoney
            print "-> BUY : %-10s %-6.2f %-6.2f %-6.2f %-6d %-6s %-6s %6s%% %8s" % (code,buy,0,buy, buyNumber, suspension, range, 0,'-'+str(int(buy*buyNumber*100)))
            newCodeInfo.append((code, buy, buyNumber))
        print ">>TOTAL: %-10s %-6s %-6s %-6s %-6s %-6s %-6s %6.2f%% %8s" % ('-','-','-','-', '-', '-', '-', 0 , 1000000)
        print 'TAKE ',int(time.time()) - a, ' seconds'
        makeDeal(nextDate, e_date, filter, newCodeInfo, rest_total, stockpick)
    else:
        print "==================================== TRADE DATE: %s ====================================" % s_date
        print "<<OP>> : %-10s %-6s %-6s %-6s %-6s %-6s %-6s %6s%% %8s" % ('CODE','BUY','SELL','NOW', 'DEALT', 'SUSPEN', 'RANGE', 'P/L', 'MONEY')
        #计算股票市值
        infodict = {}
        totalValue = 0
        lastDate = getLastDate(s_date)
        allStock = getBest(lastDate,length=5000,days=20)
        #print lastDate, allStock
        bestlist= allStock[:20]
        codelist = [_code[0] for _code in codeinfo]
        for bestcode in codelist:
            infodict.update({bestcode:__getMemeryStockInfo(bestcode[2:], bestcode[:2], s_date[:4], type='b')})
        newCodeInfo = []
        #newCodeInfo@list: [('002063', 27.78, 300), ('002150', 21.78, 200), ('600604', 18.21, 250)]; 数量单位：(股票代码,买入价格,手数))]
        for info in codeinfo:
            suspension = False
            code, buy, oBuyNumber = info
            #print allStock
            range = allStock.index(code)
            codeinfoyear = infodict[code]
            codeinfoday = None
            start_date = s_date
            while not codeinfoday:
                try:
                    codeinfoday = codeinfoyear[start_date]
                    break
                except Exception,e:
                    #print traceback.print_exc(e)
                    codeinfoday = None
                    suspension = True
                    start_date = getLastDate(start_date, code)
                    #print start_date, code

            #判断是否换股
            if not suspension:
                #未停牌
                #卖出条件：1.BR不在前20；2.盈利超过35%
                #判断盈利率
                oldPrice = codeinfo[codelist.index(code)][1]
                newPrice = codeinfoyear[s_date]['start']
                percent = (newPrice/oldPrice - 1) * 100
                #判断BR
                if code not in bestlist:
                    #从前20挑出一支没有买过的新股
                    #print code,' out of 20'
                    tmpList = [_code[0] for _code in codelist]
                    while 1:
                        new = int(random.randint(0,19))
                        
                        #新股不在codeinfo中且当日没有停牌
                        if bestlist[new] not in codelist:
                            newStock = bestlist[new]
                            newcodeinfoyear = __getMemeryStockInfo(newStock[2:], newStock[:2], s_date[:4], type='b')
                            if s_date in newcodeinfoyear.keys():
                                newRange = bestlist.index(newStock)
                                break
                    #print codeinfoyear[s_date]
                    sell = newPrice
                    print "<- SELL: %-10s %-6.2f %-6.2f %-6.2f %-6d %-6s %-6s %6.2f%% %8s" % (code,oldPrice, sell,0,oBuyNumber, suspension, range, percent,'+'+str(int(sell*oBuyNumber*100)))
                    #print sell, oBuyNumber, rest_money
                    oIndex=codelist.index(code)
                    codelist.remove(code)
                    codelist.insert(oIndex, newStock)
                    aTotalValue = sell * oBuyNumber * 100 + rest_money
                    #print sell, oBuyNumber, rest_money, aTotalValue
                    totalValue += aTotalValue
                    buy = newcodeinfoyear[s_date]['start']                  #以开盘价购买
                    buyNumber = int(aTotalValue/buy/100)                     #计算股票数量
                    rest_money = aTotalValue - buy*buyNumber*100             #重新计算剩余金钱
                    #print buy, buyNumber, rest_money
                    print "-> BUY : %-10s %-6.2f %-6.2f %-6.2f %-6d %-6s %-6s %6.2f%% %8s" % (newStock,buy, 0,buy,buyNumber, suspension, newRange, 0,'-'+str(int(buy*buyNumber*100)))
                    newCodeInfo.append((newStock, buy, buyNumber))
                    continue
                
                if percent >= PH or percent <= PL:
                    #盈利大于50%或者亏损大于15%，换股
                    #print 'Percent: ',newPrice/oldPrice
                    tmpList = [_code[0] for _code in codelist]
                    while 1:
                        new = int(random.randint(0,19))
                        if bestlist[new] not in codelist:
                            newStock = bestlist[new]
                            newcodeinfoyear = __getMemeryStockInfo(newStock[2:], newStock[:2], s_date[:4], type='b')
                            if s_date in newcodeinfoyear.keys():
                                newRange = bestlist.index(newStock)
                                break
                    #print codeinfoyear[s_date]
                    sell = newPrice
                    print "<- SELL: %-10s %-6.2f %-6.2f %-6.2f %-6d %-6s %-6s %6.2f%% %8s" % (code,oldPrice,sell,0,oBuyNumber, suspension, range, percent,'+'+str(int(sell*oBuyNumber*100)))
                    #print sell, oBuyNumber, rest_money
                    oIndex=codelist.index(code)
                    codelist.remove(code)
                    codelist.insert(oIndex, newStock)
                    aTotalValue = sell * oBuyNumber * 100 + rest_money
                    totalValue += aTotalValue
                    newcodeinfoyear = __getMemeryStockInfo(newStock[2:], newStock[:2], s_date[:4], type='b')
                    buy = newcodeinfoyear[s_date]['start']                  #以开盘价购买
                    buyNumber = int(aTotalValue/buy/100)                     #计算股票数量
                    rest_money = aTotalValue - buy*buyNumber*100             #重新计算剩余金钱
                    print "-> BUY : %-10s %-6.2f %-6.2f %-6.2f %-6d %-6s %-6s %6.2f%% %8s" % (newStock,buy,0,buy, buyNumber, suspension, range, percent,'-'+str(int(buy*buyNumber*100)))
                    newCodeInfo.append((newStock,  buy, buyNumber))
                    continue
                
                if percent > PL and percent < PH and code in bestlist:
                    oPrice = codeinfoday['start']
                    aTotalValue = oPrice * oBuyNumber * 100
                    totalValue += aTotalValue
                    print "-* HOLD: %-10s %-6.2f %-6.2f %-6.2f %-6d %-6s %-6s %6.2f%% %8d" % (code,oldPrice,0,oPrice,oBuyNumber, suspension, range, percent,oPrice*oBuyNumber*100)
                    newCodeInfo.append((code, oldPrice, oBuyNumber))
                    continue
                    
                            
            else:
                #停牌,不换股
                oldPrice = codeinfo[codelist.index(code)][1]
                lastDate = getLastDate(s_date, code)
                newPrice = codeinfoyear[lastDate]['end']       #停牌当天收盘价
                #newPrice = codeinfoyear[s_date]['start']
                percent = (newPrice/oldPrice - 1) * 100
                oPrice = codeinfoday['end']
                aTotalValue = oPrice * oBuyNumber * 100
                totalValue += aTotalValue
                print "-* HOLD: %-10s %-6.2f %-6.2f %-6.2f %-6d %-6s %-6s %6.2f%% %8d" % (code,oldPrice,0,newPrice,oBuyNumber, suspension, range, percent,oPrice*oBuyNumber*100)
                newCodeInfo.append((code, oldPrice, oBuyNumber))
        #else:
        #    totalValue = rest_money + totalValue
        print ">>TOTAL: %-10s %-6s %-6s %-6s %-6s %-6s %-6s %6.2f%% %8s" % ('-','-','-','-', '-', '-', '-', ((totalValue+rest_money)/1000000 - 1)*100 , int(totalValue+rest_money))
        #print "STOCK INFO: %s" % newCodeInfo
        #print "STOCK VALUE: %s" % totalValue
        #print "REST MONEY: %s" % rest_money
        
        #print type(s_date.encode(sys.getdefaultencoding())), type(e_date)
        #print s_date.encode(sys.getdefaultencoding()), e_date
        if s_date!=e_date:
            print 'TAKE ',int(time.time()) - a, ' seconds'
            return makeDeal(getNextDate(s_date),e_date, filter, newCodeInfo,rest_money,stockpick)
        else:
            print "FINALLY VALUE: %s" % totalValue
            return True
        
def getRange(stocklist, date='', length=20, days=20):
    '''
    stocklist: ['002063','002150', '600604']
    return: [('002063', 1374), ('002150', 2), ('600604', 'NaN')]
    '''
    bestlist = [stock for stock in getBest(date, length, days)]
    range = []
    for stock in stocklist:
        try:
            #print getFullCode(stock)
            index = bestlist.index(getFullCode(stock))
        except:
            index = 'NaN'
        range.append((stock,index))
    else:
        return range      

def setupParser():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage=usage)
    parser.add_option("-F", "--flow-filter", action="store", type="string", dest="filter", help="Filtrate by capital stock in circulation.", default='0.01')
    parser.add_option("-P", "--print-out", action="store_true", dest="aPrint", help="Decide if to print out result.", default=False)
    parser.add_option("-D", "--selected-date", action="store",type="string", dest="sDate", help="Selected date of picking.", default='')
    parser.add_option("-t", "--top-X", action="store",type="int", dest="topX", help="Picking stock from topX.", default=20)
    updateGroup = OptionGroup(parser, "Update Options","These options update all local data.")
    updateGroup.add_option("-d", "--update-date", action="store_true", dest="update_date", help="Update all date from 1999.", default=False)
    updateGroup.add_option("-l", "--update-local", action="store_true", dest="update_local", help="Update local stock info of specified year.", default=False)
    updateGroup.add_option("-s", "--update-stock", action="store", dest="update_stock", help="Update stock list, from given year(2010 later).", default='')
    parser.add_option_group(updateGroup)
    
    makeDealGroup = OptionGroup(parser, "Make Deal Options","These options simulate deals.    \
                                        e.g: python app.py -f 20100105 -e 20101231 -m 1000000 -n 10")
    makeDealGroup.add_option("-f", "--start-date", action="store",type="string", dest="sDate", help="Starting date of simulation.", default='')
    makeDealGroup.add_option("-e", "--end-date", action="store",type="string", dest="eDate", help="Ending date of simulation.", default='')
    makeDealGroup.add_option("-m", "--start-money", action="store",type="int", dest="sMoney", help="Get range by specified stocks number.", default=1000000)
    makeDealGroup.add_option("-p", "--pick-policy", action="store",type="int", dest="policy", help="Policy of stock picking:     \
                                                                                                    0: random in pick number;    \
                                                                                                    1: static top 10.", default=0)
    makeDealGroup.add_option("-n", "--pick-number", action="store",type="int", dest="pNumber", help="Number of stocks for random picking.", default=5)
    parser.add_option_group(makeDealGroup)
    
    getBestGroup = OptionGroup(parser, "Pick Best Stocks","These options pick out best stocks by specified args.    \
                                        e.g: python app.py -D 20100231 -P [-t 20] [-a 20] [-F 5]")
    
    
    getBestGroup.add_option("-a", "--average-day", action="store",type="int", dest="aDays", help="BR's average day.", default=20)
    
    getRangeGroup = OptionGroup(parser, "Get Stock Range","These options get range of stocks by given args.    \
                                        e.g: python app.py -D 20100231 [-t 20] [-a 20] [-F 5]")
    getRangeGroup.add_option("-r", "--get-range", action="store",type="string", dest="sList", help="Get one or multi stocks range.    \
                                                                                                    e.g.: 000651,000731.", default='')
    parser.add_option_group(getRangeGroup)
    
    parser.add_option_group(getBestGroup)
    return parser
    

if __name__ == "__main__":
    #l = ['2015','2014','2013','2012','2011','2010']
    #for year in l:
    #sh = getShangHaiInfo('2015')
    #    sh = getShangHaiInfo(year)
    #    getShangHaiBR(sh)
    #sh = getShangHaiInfo('2015')
    #getShangHaiBR(sh)
    sorted_s = []
    parser = setupParser()
    (options, args) = parser.parse_args()
    if options.update_date:
        print 'Update full date list ...'
        __getFullDate(2010,2016)
        print 'Complete ...'
        print 'Update stock list ...'
        updateStockCodeList()
        print 'Complete ...'
    if options.update_local:
        print 'Update ST stocks ...'
        getSTStock()
        print 'Complete ...'
    
    if options.update_stock:
        try:
            year = int(options.update_stock)
        except Exception,e:
            parser.error('%s is not a year' % options.update_stock)
        print 'Update stocks from %s to now ...' % options.update_stock
        
        for i in range(int(year),year+1):
            print 'Update %s\'s stocks info ...' % i
            updateLocalHistory(str(i),'b')
        else:
            print 'Complete ...'
            
    if options.sDate and options.topX and options.aDays:
        try:
            date, topX, aDays,filter= options.sDate, options.topX, options.aDays, options.filter
        except Exception,e:
            parser.error("Not enough args.")
        try:
            filter = float(options.filter)
        except Exception,e:
            parser.error('%s is not a float.' % options.filter)
        getBest(date,length=topX,days=aDays,printOut=options.aPrint,filter=filter)
    #else:
    #    parser.error("Not enough args.")
        
    if options.sDate and options.eDate and options.sMoney and options.pNumber:
        sDate, eDate, filter, sMoney, pNumber = options.sDate, options.eDate, options.filter, options.sMoney, options.pNumber
        makeDeal(sDate, eDate, filter, [], sMoney, pNumber)
    
    if options.sList and options.sDate:
        sDate, sList = options.sDate,options.sList
        try:
            l = sList.split(',')
        except:
            parser.error('Split stock with ",".' % options.filter)
        print getRange(l,date=sDate, length=options.topX)
    #print __getFullDate(1999,2015)
    #getStockBR('sz000739')
    #getSTStock()
    #best = getBest("20150730",length=20,days=20,printOut=True)
    #stocklist = ['000736','002735','002323','603006','002679','000025','603268','002680','603009']
    #print getRange(stocklist,date='20150730', length=20)
    #print best
    #makeDeal('20150715','20150730', [], 1000000, 5)
    #money = makeDeal("20150720", "20150724", 1000000, stockpick=2)
    #updateLocalHistory('2015','b')
    #updateStockCodeList()
        
        
        
        