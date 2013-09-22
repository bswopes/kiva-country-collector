#!/usr/bin/python

import json 
import urllib
from os import environ
from sys import exit
from country import country_codes
import rate
import unittest

app_id = "com.bhodisoft.kcc"


def find_loans(code,verbose=True):
    ''' (str) -> bool
        
    Return True if at least one new country is found.
        
    '''
    search_url = "http://api.kivaws.org/v1/loans/search.json?app_id=" + app_id + "&status=fundraising&country_code="
    loans_found = False
    loans = -1
    url = search_url + code
    if verbose:
        if 'GATEWAY_INTERFACE' not in environ:
            print "Checking url: %s" % url
        else:
            if ',' not in code:
                print 'Checking <a href="%s" target=_top>%s</a>' % (url,country_codes[code])
            else:
                print 'Checking <a href="%s" target=_top>%s</a>' % (url,code)
    try:   
        f = urllib.urlopen(url)
        rate.get_rate(f)
        d = json.loads(f.read())
        if d["paging"]["total"] > 0:
            loans = d["paging"]["total"]
    except:
        rate.get_rate(f, True)
        if d["message"]:
            print d["message"]
        else:
            print "Error loading loans for %s. Try again later." % code    
        exit(1)
    if loans > 0:
        if verbose and len(code) < 3:
            print "Found %s loans for country %s" % (loans, country_codes[code])
        loans_found = True
    return loans_found

def display_link(loans_found,rss=False):
    ''' (dict,[bool]) -> exits
    
    Displays link to search for found loans, or rss feed for remaining countries.
    Formats based on if called from command line or cgi.
    '''
    if isinstance(loans_found,list):
        co_list = "" 
        for code in loans_found:
            co_list = co_list + "," + str(code)
        co_list = co_list.lstrip(',')
    else:
        co_list = loans_found

    if not rss:
        link = "http://www.kiva.org/lend#/?app_id=" + app_id + "&countries[]=" + co_list
    else:
        link = "http://api.kivaws.org/v1/loans/search.rss?app_id=" + app_id + "&status=fundraising&country_code=" + co_list

    if 'GATEWAY_INTERFACE' not in environ:
        print "Visit Kiva at: %s" % link
    else:
        print 'Visit Kiva <a href="%s" target=_top>HERE</a>' % link
        print "</p>"
    exit(0)

def find_new_loans(not_loaned,loan_count=1,verbose=False):
    ''' (dict,[int],[bool]) -> dict
    
    For all countries in not_loaned, call find_loans to search for available loans.
    
    If target loan count is reached, display links and exit.
    
    Returns dict.
    '''
    loans_found = []
    new_list = ','.join(sorted(not_loaned))
    if find_loans(new_list,verbose):
        for code in not_loaned:
            if verbose:
                print "Checking new country %s." % country_codes[code]
            new_loans_found = find_loans(code,verbose)
            if new_loans_found:
                print "NEW COUNTRY! Found loans for %s" % country_codes[code]
                loans_found.append(code)
            if len(loans_found) == loan_count:
                if verbose:
                    print "Reached specified number of countries."
                display_link(loans_found)
    return loans_found

def find_old_loans(loans_found,my_countries,loan_count=1,verbose=False):
    ''' (dict,dict,[int],[bool]) -> dict
    
    Search through previously loaned countries by least number of loans for available loans.
    
    If target loan count is reached, display links and exit.
    
    Returns dict.
    '''
    for code,count in sorted(my_countries.items(), key=lambda x: len(x[1])):
        new_loans_found = find_loans(code,verbose)
        if new_loans_found:
            loans_found.append(code)
            print "Country %s, previous loan count %s." % (country_codes[code],len(count))
        if len(loans_found) == loan_count:
            if verbose:
                print "Reached specified number of countries."
            display_link(loans_found)
    return loans_found

class TestLoan(unittest.TestCase):
    def testFindLoans(self):
        loan_list = ["AF","AD","BD","SV","LB"]
        result_find_loans = len(find_new_loans(loan_list,6))
        self.assertGreater(result_find_loans,0,"Problem with find_new_loans.")

if __name__ == "__main__":
    unittest.main()


