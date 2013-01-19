#!/usr/bin/python

import csv
country_codes = {}
file = "kiva-country-list.csv"
#file = 'iso-country-codes.csv'

with open(file) as f:
        reader = csv.reader(f)
        for row in reader:
                k, v = row
                country_codes[k] = v

#for code in country_codes:
#        print country_codes[code]
