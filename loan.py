#!/usr/bin/python

import json 
import urllib
from os import environ
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
    if verbose:
        if 'GATEWAY_INTERFACE' not in environ:
            print "Checking url: %s" % url
        else:
            if ',' not in code:
                print 'Checking <a href="%s" target=_top>%s</a>' % (url,country_codes[code])
            else:
                print 'Checking <a href="%s" target=_top>%s</a>' % (url,code)
    try:   
        d = json.loads(urllib.urlopen(url).read())
        if d["paging"]["total"] > 0:
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

    link = "http://www.kiva.org/lend#/?app_id=" + app_id + "&countries[]=" + co_list
    if 'GATEWAY_INTERFACE' not in environ:
        print "Visit Kiva at: %s" % link
    else:
        print 'Visit Kiva <a href="%s" target=_top>HERE</a>' % link
        print "</p>"
    exit(0)

def find_new_loans(not_loaned,loan_count=1,verbose=False):
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
    for code,count in sorted(my_countries.items(), key=lambda x: x[1]):
#        if verbose:
#            print "Checking country %s, previous loan count %s." % (country_codes[code],count)
        new_loans_found = find_loans(code,verbose)
        if new_loans_found:
            loans_found.append(code)
            print "Country %s, previous loan count %s." % (country_codes[code],count)
        if len(loans_found) == loan_count:
            if verbose:
                print "Reached specified number of countries."
            display_link(loans_found)
    return loans_found

if __name__ == "__main__":
    verbose = True
    loan_list = ["AF","AD","BD","SV","LB"]
    print find_new_loans(loan_list)


