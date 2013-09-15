#!/usr/bin/python

import json 
import urllib 
import csv
from os import mkdir, path, environ
from sys import exit
import string
import re
from country import country_codes
import rate
import unittest

app_id = "com.bhodisoft.kcc"


def check_lender_id(lender_in):
    notallowed = "[^" + string.ascii_lowercase + string.digits + "]+"
    lender = re.sub(notallowed,'', lender_in.lower())
    
    if lender != lender_in or lender.isalnum() is False or len(lender) < 3 or len(lender) > 24:
        return False
    else:
        return True

def read_lender_csv(lender,private=False,verbose=False,display=False):
        ''' (str) -> dict, dict

        Returns list of country codes lent to and count. Returns False if file does not exist.
        '''
        lender_file = "lenders/" + lender + ".csv"
        my_countries = {}
        not_loaned = country_codes.copy()
        loan_count = 0
        try: 
                with open(lender_file,'rb') as f:
                        reader = csv.reader(f)
                        for row in reader:
                                key, value = row
                                value = string.strip(value,"[]")
                                value = string.replace(value,' ','')
                                value = string.split(value,',')
                                loan_count += len(value)
                                # print "key: %s, value: %s, count: %s" % (key,value,loan_count)
                                my_countries[str(key)] = value
                                if key in not_loaned:
                                        del not_loaned[key]
                        if __name__ == "__main__":
                                print "Loading cached data from file: %s" % lender_file
        except IOError:
            if __name__ == "__main__":
                print "Cached data not found."

        if check_lender_count(lender,verbose) != loan_count:
            print "Lender has made new loans (%s vs %s). Updating..." % (check_lender_count(lender),loan_count)
            my_countries, not_loaned = fetch_old_loans(lender,private,verbose)
            
        if verbose or display:
            display_lender_data(my_countries,not_loaned,display)
        return my_countries, not_loaned


def write_lender_csv(lender,my_countries):
        ''' (str,dict) -> bool

        Writes country code and count to lender.csv. Returns success/failure.
        '''
        lender_file = "lenders/" + lender + ".csv"
        if not path.exists("lenders"):
                try:
                        mkdir("lenders",0700)
                except IOError:
                        if __name__ == "__main__":
                                print "Directory already exists."

                
        try: 
                with open(lender_file,'wb') as f:
                        writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
                        for key,value in my_countries.items():
                                writer.writerow([key, value])
                        f.close()
                        print "Cached lender data to file: %s" % lender_file
                        return True
        except IOError:
                print "Unable to write to lender file: %s.csv" % lender
                return False
        

def check_lender_count(lender,verbose=False):
        lender_url = "http://api.kivaws.org/v1/lenders/" + lender + ".json?app_id=" + app_id
        try:
                if verbose:
                    print "Getting lender loan count: %s" % lender_url
                f = urllib.urlopen(lender_url)
                rate.get_rate(f)
                d = json.loads(f.read())
                total_loans = int(d["lenders"][0]["loan_count"])
        except:
                rate.get_rate(f, True)
                if d["message"]:
                    print d["message"]
                else:
                    print "Error loading lender page. Confirm your ID at http://www.kiva.org/myLenderId"
                exit(1)
        return total_loans


def fetch_old_loans(lender,private=False,verbose=False):
        ''' (str) -> dict,dict

        Polls Kiva API for lender, gathering loan count per country.

        Returns dict of country codes lent to and count. Returns dict of country codes and countries not lent to.

        '''
        page = 1 # Starting page number
        pages = 1 # Starting limit
        lender_url = "http://api.kivaws.org/v1/lenders/" + lender + "/loans.json?app_id=" + app_id + "&sort_by=oldest&page="

        my_countries = {}
        not_loaned = country_codes.copy()
        while page <= pages:
                url = lender_url + str(page)
                try:
                        if verbose:
                            print "Collecting previous loan data from: %s" % url
                        f = urllib.urlopen(url)
                        d = json.loads(f.read())
                        pages = d["paging"]["pages"]
                except:
                        rate.get_rate(f, True)
                        if d["message"]:
                            print d["message"]
                        else:
                            print "Error loading lender page. Confirm your ID at http://www.kiva.org/myLenderId"
                        exit(1)


                #print "Working on page %s of %s." % (page, pages)
                for x in d["loans"]:
                        code = x["location"]["country_code"].encode('ascii','ignore')
                        loan_id = int(x["id"])
                        if code not in my_countries:
                                my_countries[code] = []
                                my_countries[code].append(loan_id)
                        else:
                                my_countries[code].append(loan_id)
                        if code in not_loaned:
                                del not_loaned[code]
                page += 1


                    
                rate_remaining,rate_limit = rate.get_rate(f)
                if rate_remaining <= rate_limit/10:
                    print "Warning: Approaching API rate limit. Exiting."
                    if not private:
                        write_lender_csv(lender,my_countries)
                    exit(1)
                    
        if not private:
            write_lender_csv(lender,my_countries)
        return my_countries, not_loaned


def display_lender_data(my_countries,not_loaned,display=False):
    print "User has previously loaned to:", ', '.join(sorted(my_countries))
    print "User has not loaned to:", ', '.join(sorted(not_loaned))
    print "Remaining countries:", len(not_loaned)

    if display:
        if 'GATEWAY_INTERFACE' in environ:
            print '</p>'
        exit(0)

class TestLender(unittest.TestCase):
    def testLender(self):
        self.assertTrue(check_lender_id("bswopes"))
        
    def testShortLender(self):
        self.assertFalse(check_lender_id("b"))
        
    def testLenderBad(self):
        self.assertFalse(check_lender_id("bsw%op$es!"))

if __name__ == "__main__":
    unittest.main()

#    my_countries, not_loaned = fetch_old_loans(lender)
#    print my_countries
#    print not_loaned

