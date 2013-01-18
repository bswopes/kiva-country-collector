#!/usr/bin/python

import json,urllib,pprint,country

page = 1
baseurl = "http://api.kivaws.org/v1/lenders/bswopes/loans.json?page="
searchurl = "http://api.kivaws.org/v1/loans/search.json?status=fundraising&country_code="
my_countries = []

url = baseurl + str(page)
data = urllib.urlopen(url).read()
d = json.loads(data)
pages = d["paging"]["pages"]

while page <= pages:
        url = baseurl + str(page)
        data = urllib.urlopen(url).read()
        d = json.loads(data)

        print "Working on page %s of %s." % (page, pages)
        for x in d["loans"]:
                code = x["location"]["country_code"].encode('ascii','ignore')
                if code not in my_countries:
                        my_countries.append(code)

        for code in my_countries:
                #print "My country:", code
                if code in country.country_codes:
                        del country.country_codes[code]

        page += 1

for code in country.country_codes:
        print "Checking country:", country.country_codes[code]
        url = searchurl + code
        data = urllib.urlopen(url).read()
        d = json.loads(data)
        loans = d["paging"]["total"]
        if loans > 0:
                print "Found %s loans for country %s" % (loans, country.country_codes[code])
