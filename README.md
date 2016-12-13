# StockPool_V2
一个简单的股票程序

Usage: app.py [options] arg

Options:
  -h, --help            show this help message and exit
  -F FILTER, --flow-filter=FILTER
                        Filtrate by capital stock in circulation.
  -P, --print-out       Decide if to print out result.
  -D SDATE, --selected-date=SDATE
                        Selected date of picking.
  -t TOPX, --top-X=TOPX
                        Picking stock from topX.

  Update Options:
    These options update all local data.

    -d, --update-date   Update all date from 1999.
    -l, --update-local  Update local stock info of specified year.
    -s UPDATE_STOCK, --update-stock=UPDATE_STOCK
                        Update stock list, from given year(2010 later).

  Make Deal Options:
    These options simulate deals.
    e.g: python app.py -f 20100105 -e 20101231 -m 1000000 -n 10

    -f SDATE, --start-date=SDATE
                        Starting date of simulation.
    -e EDATE, --end-date=EDATE
                        Ending date of simulation.
    -m SMONEY, --start-money=SMONEY
                        Get range by specified stocks number.
    -p POLICY, --pick-policy=POLICY
                        Policy of stock picking:
                        0: random in pick number;
                        1: static top 10.
    -n PNUMBER, --pick-number=PNUMBER
                        Number of stocks for random picking.

  Get Stock Range:
    These options get range of stocks by given args.
    e.g: python app.py -D 20100231 [-t 20] [-a 20] [-F 5]

    -r SLIST, --get-range=SLIST
                        Get one or multi stocks range.
                        e.g.: 000651,000731.

  Pick Best Stocks:
    These options pick out best stocks by specified args.
    e.g: python app.py -D 20100231 -P [-t 20] [-a 20] [-F 5]

    -a ADAYS, --average-day=ADAYS
                        BR's average day.
