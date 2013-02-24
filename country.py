#!/usr/bin/python

import string, time
import json, urllib, csv
import sys

app_id = "com.bhodisoft.kcc"

def read_countries():
    country_codes = {}
    file = "data/kiva-country-list.csv"
    
    with open(file) as f:
        reader = csv.reader(f)
        for row in reader:
            k, v = row
            country_codes[k] = v
    return country_codes

def new_kiva_country(code):
    url = "http://api.kivaws.org/v1/loans/search.json?app_id=" + app_id + "&country_code=" + code
    d = json.loads(urllib.urlopen(url).read())
    if len(d["loans"]) > 0:
        return str(d["loans"][0]["location"]["country"])
    else:
        return False

def check_kiva_countries():
    write_country_file = False
    methodurl='http://api.kivaws.org/v1/methods/GET*%7Cloans%7Csearch.json?app_id=' + app_id
    country_codes = read_countries()
    
    d = json.loads(urllib.urlopen(methodurl).read())['methods'][0]['arguments']
    for arg in d:
        if arg['name'] == 'country_code':
            for rule in arg['rules']:
                if rule['name'] == 'inList':
                    code = rule['values']
                    break

    for x in code:
        if x not in country_codes:
            if __name__ == "__main__":
                print "Country %s not in list." % x
            co_name = new_kiva_country(x)
            if co_name != False:
                country_codes[x] = co_name
                write_country_file = True

    if write_country_file:
        with open('data/kiva-country-list.csv','wb') as f:
            writer = csv.writer(f,quoting=csv.QUOTE_ALL)
            for key,value in sorted(country_codes.items()):
                writer.writerow([key, value])

    return country_codes

if __name__ == "__main__":
        print check_kiva_countries()