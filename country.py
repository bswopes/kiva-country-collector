#!/usr/bin/python

import json
import urllib
import csv
import unittest

app_id = 'com.bhodisoft.kcc'
country_list_filename = 'data/kiva-country-list.csv'

def read_countries():
    ''' (None) -> Dict
    
    Returns dict with the contents of file country_list_filename.
    '''
    country_codes = {}
    
    try:
        with open(country_list_filename) as f:
            reader = csv.reader(f)
            for row in reader:
                k, v = row
                country_codes[k] = v
    except:
        if __name__ == "__main__":
            print "Unable to read kiva country file."
    return country_codes

def new_kiva_country(code):
    ''' (str) -> str
    
    Returns country name for country code.
    '''
    methodurl = 'http://api.kivaws.org/v1/methods/GET*%7Cloans%7Csearch.json?app_id=' + app_id
    d = json.loads(urllib.urlopen(methodurl).read())
    if code in d['methods'][0]['arguments'][3]['labels']['en']:
        return d['methods'][0]['arguments'][3]['labels']['en'][code]
    else:
        return False

def check_kiva_countries():
    ''' (None) -> dict
    
    Get current list of all countries KIVA has worked with.
    If new country added to the list, call new_kiva_country and update country file.
    
    Returns list of country codes.
    '''
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
        try:
            with open(country_list_filename,'wb') as f:
                writer = csv.writer(f,quoting=csv.QUOTE_ALL)
                for key,value in sorted(country_codes.items()):
                    writer.writerow([key, value])
                    #print "Writing:" + key + "," + value
        except:
            if __name__ == "__main__":
                print "Unable to write new kiva country file."

    return country_codes

def get_codes(co_list):
    ''' (dict) -> list
    
    Returns sorted list of country codes.
    '''
    codes = ""
    for code,count in sorted(co_list.items(), key=lambda x: x[1]):
        codes = codes + "," + code

    return codes.lstrip(',')

    

class TestCountry(unittest.TestCase):
    def testKivaCountries(self):
        country_codes = check_kiva_countries()
        self.assertGreater(len(country_codes), 1, "Problem loading country codes")
        
    def testNewCountry(self):
        self.assertIsNot(new_kiva_country("SV"), False, "Problem with testing new countries.")
        
    def testFakeNewCountry(self):
        self.assertFalse(new_kiva_country("ZZ"),False)


if __name__ == "__main__":
    unittest.main()
else:
    country_codes = check_kiva_countries()
