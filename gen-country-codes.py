#!/usr/bin/python

import string, time
import json, urllib, csv

code = []
country_codes = {}

for a in string.ascii_uppercase:
        for b in string.ascii_uppercase:
                code.append(a + b)

for x in code:
        url = "http://api.kivaws.org/v1/loans/search.json?country_code=" + x
        print url
        d = json.loads(urllib.urlopen(url).read())
        total = d["paging"]["total"]
        if total > 0:
                country_name = str(d["loans"][0]["location"]["country"])
                country_codes[x] = country_name
        time.sleep(2)

print country_codes

with open('kiva-country-list.csv','wb') as f:
        writer = csv.writer(f,quoting=csv.QUOTE_ALL)
        for key,value in sorted(country_codes.items()):
                writer.writerow([key, value])

