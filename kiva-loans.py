#!/usr/bin/python

import json 
import urllib 
import csv
from sys import exit
from optparse import OptionParser
from webbrowser import open_new_tab

app_id = "com.github.bswopes.kiva-country-collector"

parser = OptionParser()
parser.add_option("-a","--all-countries",dest="all",action="store_true",help="Check all possible countries, not just known countries Kiva loans to. Much slower.",default=False)
parser.add_option("-d","--display-user",dest="display",action="store_true",help="Display user information only. Don't check for loans.",default=False)
parser.add_option("-f","--find-all",dest="findall",action="store_true",help="Returns all new countries found, not just the number limited by count (-c).",default=False)
parser.add_option("-i","--id",dest="kiva_id",type=str,help="Kiva ID from http://www.kiva.org/myLenderId")
parser.add_option("-c","--count",dest="count",type=int,help="Number of countries to find.",default=1)
parser.add_option("-n","--new-only",dest="newonly",action="store_true",help="Only find new countries.",default=False)
parser.add_option("-u","--update",dest="update",action="store_true",help="Ignore / Update existing user data (lender.csv)",default=False)
parser.add_option("-v","--verbose",dest="verbose",action="store_true",help="Extra output",default=False)
(options, args) = parser.parse_args()

if options.kiva_id is None:
        #parser.print_help()
        lender = raw_input("Ender your Kiva ID (http://www.kiva.org/myLenderId): ")
else:
        lender = options.kiva_id

if lender.isalnum() is False or len(lender) < 3 or len(lender) > 24:
        print "Lender ID is invalid."
        exit(1)

def read_countries(all):
        country_codes = {}
        if all:
                if options.verbose:
                        print "Checking all possible countries."
                file = 'kiva-country-iso.csv'
        else:
                file = "kiva-country-list.csv"

        with open(file) as f:
                reader = csv.reader(f)
                for row in reader:
                        k, v = row
                        country_codes[k] = v
        return country_codes

def read_lender_csv(lender):
        ''' (str) -> dict, dict

        Returns list of country codes lent to and count. Returns False if file does not exist.
        '''
        file = lender + ".csv"
        my_countries = {}
        not_loaned = country_codes.copy()
        try: 
                with open(file,'rb') as f:
                        loan_count = 0
                        reader = csv.reader(f)
                        for row in reader:
                                key, value = row
                                loan_count += int(value)
                                my_countries[str(key)] = int(value)
                                if key in not_loaned:
                                        del not_loaned[key]
                        if options.verbose:
                                print "Read data from file: %s" % file

                        if check_lender_count(lender) != loan_count:
                                print "Lender has made new loans. Updating..."
                                my_countries, not_loaned = fetch_old_loans(lender)
                        return my_countries, not_loaned
        except IOError:
                return False, False

def write_lender_csv(lender,my_countries):
        ''' (str,dict) -> bool

        Writes country code and count to lender.csv. Returns success/failure.
        '''
        file = lender + ".csv"
        try: 
                with open(file,'wb') as f:
                        writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
                        for key,value in my_countries.items():
                                writer.writerow([key, value])
                        f.close()
                        print "Wrote lender file: %s" % file
                        return True
        except IOError:
                print "Unable to write to lender file: %s.csv" % lender
                return False
        
def check_lender_count(lender):
        lender_url = "http://api.kivaws.org/v1/lenders/" + lender + "/loans.json?app_id=" + app_id
        try:
                d = json.loads(urllib.urlopen(lender_url).read())
        except:
                print "Error loading lender page. Confirm your ID at http://www.kiva.org/myLenderId"
                exit(1)
        return int(d["paging"]["total"])

def fetch_old_loans(lender):
        ''' (str) -> dict,dict

        Polls Kiva API for lender, gathering loan count per country.

        Returns dict of country codes lent to and count. Returns dict of country codes and countries not lent to.

        '''
        page = 1 # Starting page number
        pages = 1 # Starting limit
        lender_url = "http://api.kivaws.org/v1/lenders/" + lender + "/loans.json?app_id=" + app_id + "&page="

        my_countries = {}
        not_loaned = country_codes.copy()
        while page <= pages:
                url = lender_url + str(page)
                try:
                        d = json.loads(urllib.urlopen(url).read())
                except:
                        print "Error loading lender page. Confirm your ID at http://www.kiva.org/myLenderId"
                        exit(1)
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

        write_lender_csv(lender,my_countries)
        return my_countries, not_loaned


def find_loans(code):
        ''' (str) -> bool

        Return True if at least one new country is found.

        '''
        search_url = "http://api.kivaws.org/v1/loans/search.json?app_id=" + app_id + "&status=fundraising&country_code="
        loans_found = False
        url = search_url + code
        try:   
                if options.verbose:
                        print "Checking url: %s" % url
                d = json.loads(urllib.urlopen(url).read())
        except:
                print "Error loading loans for %s. Try again later." % code
        loans = d["paging"]["total"]
        if loans > 0:
                if options.verbose and len(code) < 3:
                        print "Found %s loans for country %s" % (loans, country_codes[code])
                loans_found = True
        return loans_found


def display_link(loans_found):
        if isinstance(loans_found,list):
                co_list = "" 
                for code in loans_found:
                        co_list = co_list + "," + str(code)
                co_list = co_list.lstrip(',')
        else:
                co_list = loans_found

        print "Visit Kiva at: http://www.kiva.org/lend#/?app_id=%s&countries[]=%s" % (app_id,co_list)
        try:
                open_new_tab("http://www.kiva.org/lend#/?app_id=%s&countries[]=%s" % (app_id,co_list))
        except:
                if options.verbose:
                        print "Error opening browser."
        exit(0)

#
# Pull in data for lender's previous loans.
#
country_codes = read_countries(options.all)

if options.update is False:
        my_countries, not_loaned = read_lender_csv(lender)

if options.update is True or my_countries is False:
        my_countries, not_loaned = fetch_old_loans(lender)


new_list = ""
for code in sorted(not_loaned):
        new_list = new_list + "," + str(code)
new_list = new_list.lstrip(',')

if options.verbose or options.display:
        # Print a list of countries already loaned to... Mostly so user realizes something is happening.
        old_list = "" 
        for code in sorted(my_countries):
                old_list = old_list + ", " + str(code)
        old_list = old_list.lstrip(' ,')
        print "User has previously loaned to:", old_list
        print "User has not loaned to:", new_list

if options.display:
        exit(0)

#
# Check for loans in countries we haven't hit yet.
#

loans_found = []

if find_loans(new_list):
        if options.findall:
                display_link(new_list)
        for code in not_loaned:
                if options.verbose:
                        print "Checking new country %s." % country_codes[code]
                new_loans_found = find_loans(code)
                if new_loans_found:
                        print "NEW COUNTRY! Found loans for %s" % country_codes[code]
                        loans_found.append(code)
                if len(loans_found) == options.count:
                        if options.verbose:
                                print "Reached specified number of countries."
                        display_link(loans_found)
                        exit(0)

if options.newonly:
        print "No new countries found."
        exit(0)

if len(loans_found) < options.count:
        print "No new countries found. Looking for less used countries."

        for code,count in sorted(my_countries.items(), key=lambda x: x[1]):
                if options.verbose:
                        print "Checking country %s, previous loan count %s." % (country_codes[code],count)
                new_loans_found = find_loans(code)
                if new_loans_found:
                        loans_found.append(code)
                        print "Country %s, previous loan count %s." % (country_codes[code],count)
                if len(loans_found) == options.count:
                        if options.verbose:
                                print "Reached specified number of countries."
                        display_link(loans_found)

if options.verbose:
        print "Not sure how we ended up here..."
exit(3)
