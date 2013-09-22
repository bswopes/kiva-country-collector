#!/usr/bin/python

import json 
import urllib 
from os import mkdir, path, environ
from sys import exit
import string
import re
from country import country_codes
import rate
import unittest
import code

app_id = "com.bhodisoft.kcc"
my_countries = {}
not_loaned = country_codes.copy()
loan_count = 0
total_loans = 0

def check_lender_id(lender_in):
    ''' (str) -> bool
    Return true if lender_id submitted is 3-24 characters and all letters/numbers.
    '''
    notallowed = "[^" + string.ascii_lowercase + string.digits + "]+"
    lender = re.sub(notallowed,'', lender_in.lower())
    
    if lender != lender_in or lender.isalnum() is False or len(lender) < 3 or len(lender) > 24:
        return False
    else:
        return True

def read_lender_file(lender,private=False,verbose=False,display=False):
        ''' (str,[bool],[bool],[bool]) -> dict, dict

        Reads json data from lender file.
        
        Returns list of country codes lent to and count. Returns False if file does not exist.
        '''
        lender_file = "lenders/" + lender + ".json"
        global my_countries
        global not_loaned
        global loan_count

        try: 
                with open(lender_file,'rb') as f:
                        data = json.load(f)
                        my_countries = data["my_countries"]
                        loan_count = data["loan_count"]

                        for code in my_countries:
                            if code in not_loaned:
                                del not_loaned[code]
                                
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


def write_lender_file(lender):
        ''' (str) -> bool

        Writes json data to lender file. 
        
        Returns success/failure.
        '''
        global my_countries
        global loan_count
        lender_file = "lenders/" + lender + ".json"

        data = {}
        data["loan_count"] = loan_count
        data["my_countries"] = my_countries        
        
        if not path.exists("lenders"):
                try:
                        mkdir("lenders",0700)
                except IOError:
                        if __name__ == "__main__":
                                print "Directory already exists."

                
        try: 
                with open(lender_file,'wb') as f:
                        json.dump(data,f)
                        f.close()
                        print "Cached lender data to file: %s" % lender_file
                        return True
        except IOError:
                print "Unable to write to lender file: %s.csv" % lender
                return False
        

def check_lender_count(lender,verbose=False):
        ''' (str,[bool]) -> int
        
        Returns total loan count for passed lender id.
        '''
        lender_url = "http://api.kivaws.org/v1/lenders/" + lender + ".json?app_id=" + app_id
        global total_loans
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
        ''' (str,[bool],[bool]) -> dict,dict

        Polls Kiva API for lender, gathering loan count per country.

        Returns dict of country codes lent to and count. Returns dict of country codes and countries not lent to.

        '''
        global my_countries
        global not_loaned
        global total_loans
        global loan_count
        page = (loan_count//20) # Starting page number
        if page == 0:
            page = 1 # There is no page 0.
        pages = page # Starting limit, this will update after the first call.
        lender_url = "http://api.kivaws.org/v1/lenders/" + lender + "/loans.json?app_id=" + app_id + "&sort_by=newest&page="

        while page <= pages and loan_count != total_loans:
                url = lender_url + str(page)
                try:
                        if verbose:
                            print "Collecting previous loan data from page: %s" % page
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


                for x in d["loans"]:
                        code = x["location"]["country_code"].encode('ascii','ignore')
                        loan_id = int(x["id"])
                        if code not in my_countries:
                            if verbose:
                                print "Adding country: %s" % code
                            my_countries[code] = []
                            my_countries[code].append(loan_id)
                        elif loan_id not in my_countries[code]:
                            my_countries[code].append(loan_id)
                            
                        if code in not_loaned:
                            del not_loaned[code]
                page += 1

                # Keep track of current loan count so we know when to stop calling the api.
                counter = 0
                for code in my_countries:
                    counter += len(my_countries[code])
                loan_count = counter
                    
                # Leave some breathing room on the api rate limit.
                rate_remaining,rate_limit = rate.get_rate(f)
                if rate_remaining <= rate_limit/10:
                    print "Warning: Approaching API rate limit. Exiting."
                    if not private:
                        write_lender_file(lender)
                    exit(1)
                    
        if not private:
            write_lender_file(lender)
        if verbose:
            if loan_count != total_loans:
                print "Loan counts don't match! %s vs %s" % (loan_count,total_loans)
        return my_countries, not_loaned


def display_lender_data(my_countries,not_loaned,display=False):
    ''' (dict,dict,[bool]) -> exits
    
    Prints out data about lender's loans and exit.
    '''
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

