#!/usr/bin/python

import json,urllib,sys
from country import country_codes
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i","--id",dest="kiva_id",type=str,help="Kiva ID from http://www.kiva.org/myLenderId")
(options, args) = parser.parse_args()

if options.kiva_id is None:
        parser.print_help()
        sys.exit(3)
else:
        print "User ID:", options.kiva_id

page = 1
baseurl = "http://api.kivaws.org/v1/lenders/" + options.kiva_id + "/loans.json?page="
searchurl = "http://api.kivaws.org/v1/loans/search.json?status=fundraising&country_code="
my_countries = {}
not_loaned = country_codes.copy()

url = baseurl + str(page)
data = urllib.urlopen(url).read()
d = json.loads(data)
pages = d["paging"]["pages"]

# Pull all countries we have loaned to.

while page <= pages:
        url = baseurl + str(page)
        data = urllib.urlopen(url).read()
        d = json.loads(data)

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


def find_loans(code):
        loans_found = False
        #print "Checking country:", country_codes[code]
        url = searchurl + code
        data = urllib.urlopen(url).read()
        d = json.loads(data)
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
