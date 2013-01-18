#!/usr/bin/python

import csv
country_codes = {}

with open('iso-country-codes.csv') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
                k, v = row
                country_codes[k] = v

#for code in country_codes:
#        print country_codes[code]
