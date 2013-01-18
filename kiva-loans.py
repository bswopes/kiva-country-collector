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
        page += 1

#for code in sorted(my_countries, key=my_countries.get, reverse=True):
#        print "Country %s, count %s" % (country_codes[str(code)],my_countries[code])
#sys.exit(3)


# Check for loans in countries we haven't hit yet.

for code in country_codes:

        for code in my_countries:
                #print "My country:", code
                if code in country_codes:
                        del country_codes[code]

        print "Checking country:", country_codes[code]
        url = searchurl + code
        data = urllib.urlopen(url).read()
        d = json.loads(data)
        loans = d["paging"]["total"]
        if loans > 0:
                print "Found %s loans for country %s" % (loans, country_codes[code])
