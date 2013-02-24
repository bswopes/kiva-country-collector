#!/usr/bin/python

from os import environ
from sys import exit
from optparse import OptionParser
import lender
import loan

app_id = "com.bhodisoft.kcc"

parser = OptionParser()
parser.add_option("-d","--display-user",dest="display",action="store_true",help="Display user information only. Don't check for loans.",default=False)
parser.add_option("-f","--find-all",dest="findall",action="store_true",help="Returns all new countries found, not just the number limited by count (-c).",default=False)
parser.add_option("-i","--id",dest="kiva_id",type=str,help="Kiva ID from http://www.kiva.org/myLenderId")
parser.add_option("-c","--count",dest="count",type=int,help="Number of countries to find.",default=1)
parser.add_option("-n","--new-only",dest="newonly",action="store_true",help="Only find new countries.",default=False)
parser.add_option("-p","--private",dest="private",action="store_true",help="Do not write cache file!",default=False)
parser.add_option("-v","--verbose",dest="verbose",action="store_true",help="Extra output",default=False)
(options, args) = parser.parse_args()

verbose = options.verbose
display = options.display
findall = options.findall
newonly = options.newonly
private = options.private
loan_count = options.count



#
# Verify Lender ID has valid format and pull lender history.
#

if options.kiva_id is None:
    if 'GATEWAY_INTERFACE' not in environ:
        kiva_id = environ["USER"]
    else:
        exit(3)
else:
    kiva_id = options.kiva_id

lender.check_lender_id(kiva_id)
my_countries, not_loaned = lender.read_lender_csv(kiva_id,private,verbose,display)

#
# Check for loans in countries we haven't hit yet.
#

loans_found = loan.find_new_loans(not_loaned,loan_count,verbose)

if newonly:
        print "Searched all new countries."
        exit(0)

if len(loans_found) < loan_count:
    print "Found %s new countries. Looking for less used countries." % len(loans_found)
    loans_found = loan.find_old_loans(loans_found,my_countries,loan_count,verbose)


if verbose:
        print "Not sure how we ended up here..."
if len(loans_found) > 0:
        loan.display_link(loans_found)
exit(3)
