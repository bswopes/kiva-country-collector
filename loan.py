#!/usr/bin/python

import json 
import urllib
from sys import exit
from country import country_codes

app_id = "com.bhodisoft.kcc"


def find_loans(code,verbose=True):
    ''' (str) -> bool
        
        Return True if at least one new country is found.
        
        '''
    search_url = "http://api.kivaws.org/v1/loans/search.json?app_id=" + app_id + "&status=fundraising&country_code="
    loans_found = False
    loans = -1
    url = search_url + code
    try:   
        if verbose:
            print "Checking url: %s" % url
        d = json.loads(urllib.urlopen(url).read())
        loans = d["paging"]["total"]
    except:
        print "Error loading loans for %s. Try again later." % code    
    if loans > 0:
        if verbose and len(code) < 3:
            print "Found %s loans for country %s" % (loans, country_codes[code])
        loans_found = True
    return loans_found

def display_link(loans_found):
    if isinstance(loans_found,list):
        co_list = "" 
        for code in loans_found:
            co_list = co_list + "," + str(code)
        co_list = co_list.lstrip(',')
    else:
        co_list = loans_found
    
    print "Visit Kiva at: http://www.kiva.org/lend#/?app_id=%s&countries[]=%s" % (app_id,co_list)
    exit(0)


if __name__ == "__main__":
    verbose = True
    list = ["AF","AD","BD","SV","LB"]
    print find_loans(','.join(list))
    for x in list:
        print find_loans(x)

