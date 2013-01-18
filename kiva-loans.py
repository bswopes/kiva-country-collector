#!/usr/bin/python

import json, urllib
from sys import exit
from country import country_codes
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i","--id",dest="kiva_id",type=str,help="Kiva ID from http://www.kiva.org/myLenderId")
(options, args) = parser.parse_args()

if options.kiva_id is None:
        parser.print_help()
        exit(3)
else:
        print "User ID:", options.kiva_id

page = 1 # Starting page number
pages = 1 # Starting limit
lender_url = "http://api.kivaws.org/v1/lenders/" + options.kiva_id + "/loans.json?page="
search_url = "http://api.kivaws.org/v1/loans/search.json?status=fundraising&country_code="
my_countries = {}
not_loaned = country_codes.copy()

# Pull all countries we have loaned to.

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

# Print a list of countries already loaned to... Mostly so user realizes something is happening.
co_list = "" 
for code in sorted(my_countries):
        co_list = co_list + ", " + str(code)
print "User has previously loaned to:", co_list


def find_loans(code):
        ''' (str) -> bool

        Return True if at least one new country is found.

        '''
        loans_found = False
        #print "Checking country:", country_codes[code]
        url = search_url + code
        d = json.loads(urllib.urlopen(url).read())
        loans = d["paging"]["total"]
        if loans > 0:
                print "Found %s loans for country %s" % (loans, country_codes[code])
                loans_found = True
        return loans_found


# Check for loans in countries we haven't hit yet.
loans_found = False
for code in not_loaned:
        loans_found = find_loans(code)

if loans_found != True:
        print "No new countries found. Looking for less used countries."

        for code in sorted(my_countries, key=my_countries.get):
                loans_found = find_loans(code)
                if loans_found == True:
                        print "Country %s, previous loan count %s" % (country_codes[str(code)],my_countries[code])
                        break;
