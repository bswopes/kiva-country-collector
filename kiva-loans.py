#!/usr/bin/python

import json, urllib, csv
from sys import exit
from country import country_codes
from optparse import OptionParser

app_id = "com.github.bswopes.kiva-country-collector"

parser = OptionParser()
parser.add_option("-i","--id",dest="kiva_id",type=str,help="Kiva ID from http://www.kiva.org/myLenderId")
parser.add_option("-c","--count",dest="count",type=int,help="Number of countries to find.",default=1)
parser.add_option("-n","--new-only",dest="newonly",action="store_true",help="Only find new countries.",default=False)
parser.add_option("-u","--update",dest="update",action="store_true",help="Ignore / Update existing user data (lender.csv)",default=False)
parser.add_option("-v","--verbose",dest="verbose",action="store_true",help="Extra output",default=False)
(options, args) = parser.parse_args()

if options.kiva_id is None:
        parser.print_help()
        exit(3)
else:
        print "User ID:", options.kiva_id

def read_lender_csv(lender):
        ''' (str) -> dict, dict

        Returns list of country codes lent to and count. Returns False if file does not exist.
        '''
        file = lender + ".csv"
        my_countries = {}
        not_loaned = country_codes.copy()
        try: 
                with open(file,'rb') as f:
                        reader = csv.reader(f)
                        for row in reader:
                                key, value = row
                                my_countries[str(key)] = int(value)
                                if key in not_loaned:
                                        del not_loaned[key]
                        if options.verbose:
                                print "Read data from file: %s" % file
                        return my_countries, not_loaned
        except IOError:
                return False, False

def write_lender_csv(lender,my_countries):
        ''' (str,dict) -> bool

        Writes country code and count to lender.csv. Returns success/failure.
        '''
        file = lender + ".csv"
        try: 
                with open(file,'wb') as f:
                        writer = csv.writer(f,quoting=csv.QUOTE_ALL)
                        for key,value in my_countries.items():
                                writer.writerow([key, value])
                        f.close()
                        print "Wrote lender file: %s" % file
                        return True
        except IOError:
                print "Unable to write to lender file: %s.csv" % lender
                return False
        

def fetch_old_loans(lender):
        ''' (str) -> dict,dict

        Polls Kiva API for lender, gathering loan count per country.

        Returns dict of country codes lent to and count. Returns dict of country codes and countries not lent to.

        '''
        page = 1 # Starting page number
        pages = 1 # Starting limit
        lender_url = "http://api.kivaws.org/v1/lenders/" + lender + "/loans.json?app_id=" + app_id + "&page="

        my_countries = {}
        not_loaned = country_codes.copy()
        while page <= pages:
                url = lender_url + str(page)
                d = json.loads(urllib.urlopen(url).read())
                pages = d["paging"]["pages"]


                #print "Working on page %s of %s." % (page, pages)
                for x in d["loans"]:
                        code = x["location"]["country_code"].encode('ascii','ignore')
                        if code not in my_countries:
                                my_countries[code] = 1
                        else:
                                my_countries[code] += 1
                        if code in not_loaned:
                                del not_loaned[code]
                page += 1

        write_lender_csv(lender,my_countries)
        return my_countries, not_loaned

def find_loans(code):
        ''' (str) -> bool

        Return True if at least one new country is found.

        '''
        search_url = "http://api.kivaws.org/v1/loans/search.json?app_id=" + app_id + "&status=fundraising&country_code="
        loans_found = False
        url = search_url + code
        d = json.loads(urllib.urlopen(url).read())
        loans = d["paging"]["total"]
        if loans > 0:
                if options.verbose:
                        print "Found %s loans for country %s" % (loans, country_codes[code])
                loans_found = True
        return loans_found

#
# Pull in data for lender's previous loans.
#

if options.update is False:
        my_countries, not_loaned = read_lender_csv(options.kiva_id)

if options.update is True or my_countries is False:
        my_countries, not_loaned = fetch_old_loans(options.kiva_id)

if options.verbose:
        # Print a list of countries already loaned to... Mostly so user realizes something is happening.
        co_list = "" 
        for code in sorted(my_countries):
                co_list = co_list + ", " + str(code)
        print "User has previously loaned to:", co_list.lstrip(' ,')

#
# Check for loans in countries we haven't hit yet.
#

loans_found = 0
for code in not_loaned:
        if options.verbose:
                print "Checking new country %s." % country_codes[code]
        new_loans_found = find_loans(code)
        if new_loans_found:
                loans_found += 1
        if loans_found == options.count:
                print "Reached specified number of countries."
                exit(0)

if options.newonly:
        print "No new countries found."
        exit(0)

if loans_found < options.count:
        print "No new countries found. Looking for less used countries."

        for code,count in sorted(my_countries.items(), key=lambda x: x[1]):
                if options.verbose:
                        print "Checking country %s, previous loan count %s." % (country_codes[code],count)
                new_loans_found = find_loans(code)
                if new_loans_found:
                        loans_found += 1
                        print "Country %s, previous loan count %s." % (country_codes[code],count)
                        print "Visit Kiva at: http://www.kiva.org/lend#/?app_id=%s&countries[]=%s" % (app_id,code)
                if loans_found == options.count:
                        print "Reached specified number of countries."
                        exit(0)
