#!/usr/bin/python

import json 
import urllib 
import csv
from os import environ
from sys import exit
from optparse import OptionParser
import string
import re
import country
import lender

app_id = "com.bhodisoft.kcc"

parser = OptionParser()
parser.add_option("-d","--display-user",dest="display",action="store_true",help="Display user information only. Don't check for loans.",default=False)
parser.add_option("-f","--find-all",dest="findall",action="store_true",help="Returns all new countries found, not just the number limited by count (-c).",default=False)
parser.add_option("-i","--id",dest="kiva_id",type=str,help="Kiva ID from http://www.kiva.org/myLenderId")
parser.add_option("-c","--count",dest="count",type=int,help="Number of countries to find.",default=1)
parser.add_option("-n","--new-only",dest="newonly",action="store_true",help="Only find new countries.",default=False)
parser.add_option("-p","--private",dest="private",action="store_true",help="Do not write cache file!",default=False)
parser.add_option("-u","--update",dest="update",action="store_true",help="Ignore / Update existing user data (lender.csv)",default=False)
parser.add_option("-v","--verbose",dest="verbose",action="store_true",help="Extra output",default=False)
(options, args) = parser.parse_args()


def find_loans(code):
        ''' (str) -> bool

        Return True if at least one new country is found.

        '''
        search_url = "http://api.kivaws.org/v1/loans/search.json?app_id=" + app_id + "&status=fundraising&country_code="
        loans_found = False
        url = search_url + code
        try:   
                if options.verbose:
                        print "Checking url: %s" % url
                d = json.loads(urllib.urlopen(url).read())
        except:
                print "Error loading loans for %s. Try again later." % code
        loans = d["paging"]["total"]
        if loans > 0:
                if options.verbose and len(code) < 3:
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

#
# Verify Lender ID has valid format
#
if options.kiva_id is None:
    #parser.print_help()
    #kiva_id = raw_input("Ender your Kiva ID (http://www.kiva.org/myLenderId): ")
    if 'GATEWAY_INTERFACE' not in environ:
        kiva_id = environ["USER"]
else:
    kiva_id = options.kiva_id

lender.check_lender_id(kiva_id)

#
# Pull in data for lender's previous loans.
#
country_codes = country.check_kiva_countries()

if options.update is False:
        my_countries, not_loaned = lender.read_lender_csv(kiva_id,country_codes)

if options.update is True or my_countries is False:
        my_countries, not_loaned = lender.fetch_old_loans(kiva_id,country_codes)


new_list = ""
for code in sorted(not_loaned):
        new_list = new_list + "," + str(code)
new_list = new_list.lstrip(',')

if options.verbose or options.display:
        # Print a list of countries already loaned to... Mostly so user realizes something is happening.
        old_list = "" 
        for code in sorted(my_countries):
                old_list = old_list + ", " + str(code)
        old_list = old_list.lstrip(' ,')
        print "User has previously loaned to:", old_list
        print "User has not loaned to:", new_list

if options.display:
        exit(0)

#
# Check for loans in countries we haven't hit yet.
#

loans_found = []

if find_loans(new_list):
        if options.findall:
                display_link(new_list)
        for code in not_loaned:
                if options.verbose:
                        print "Checking new country %s." % country_codes[code]
                new_loans_found = find_loans(code)
                if new_loans_found:
                        print "NEW COUNTRY! Found loans for %s" % country_codes[code]
                        loans_found.append(code)
                if len(loans_found) == options.count:
                        if options.verbose:
                                print "Reached specified number of countries."
                        display_link(loans_found)
                        exit(0)

if options.newonly:
        print "No new countries found."
        exit(0)

if len(loans_found) < options.count:
        print "No new countries found. Looking for less used countries."

        for code,count in sorted(my_countries.items(), key=lambda x: x[1]):
                if options.verbose:
                        print "Checking country %s, previous loan count %s." % (country_codes[code],count)
                new_loans_found = find_loans(code)
                if new_loans_found:
                        loans_found.append(code)
                        print "Country %s, previous loan count %s." % (country_codes[code],count)
                if len(loans_found) == options.count:
                        if options.verbose:
                                print "Reached specified number of countries."
                        display_link(loans_found)

if options.verbose:
        print "Not sure how we ended up here..."
if len(loans_found) > 0:
        display_link(loans_found)
exit(3)
