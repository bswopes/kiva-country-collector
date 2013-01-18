#!/usr/bin/python

import csv
country_codes = {}

reader = csv.reader(open('iso-country-codes.csv','r'))
reader.next()
for row in reader:
        k, v = row
        country_codes[k] = v

#for code in country_codes:
#        print country_codes[code]
