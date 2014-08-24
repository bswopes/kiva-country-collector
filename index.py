#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import os
import Cookie
import datetime
from sys import exit
from optparse import OptionParser
import lender
import loan

if 'GATEWAY_INTERFACE' in os.environ:
    cgitb.enable()
    print "Content-Type: text/html;charset=utf-8"

    form = cgi.FieldStorage()
    arg_list = form.getlist("arguments")

    verbose = 'verbose' in arg_list
    display = 'display' in arg_list
    newonly = 'newonly' in arg_list
    rss = 'rss' in arg_list
    private = 'private' in arg_list
    set_cookie = 'private' not in arg_list

    kiva_id = cgi.escape(form.getfirst('lender', 'empty')).strip('"\'')
    if kiva_id == 'empty':
            try:
                    cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
                    kiva_id = cookie["lender"].value
            except:
                    print
    if not lender.check_lender_id(kiva_id):
        print
        print "Lender ID is invalid."
        exit(1)

    if set_cookie:
        expiration = datetime.datetime.now() + datetime.timedelta(days=60)
        print 'Set-Cookie: lender=' + kiva_id + "; expires=" + expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
    print

    loan_count = form.getfirst('count','1')
    if not loan_count.isdigit() and int(loan_count) <= 0:
        loan_count = '1'
    loan_count = int(loan_count)

    print '<p>Hello %s!</p>' % kiva_id
    print '''<p style="
        max-width: 100%;
        white-space: pre-line;
        ">'''


else:
    parser = OptionParser()
    parser.add_option("-d","--display-user",dest="display",action="store_true",help="Display user information only. Don't check for loans.",default=False)
    parser.add_option("-i","--id",dest="kiva_id",type=str,help="Kiva ID from http://www.kiva.org/myLenderId")
    parser.add_option("-c","--count",dest="count",type=int,help="Number of countries to find.",default=1)
    parser.add_option("-n","--new-only",dest="newonly",action="store_true",help="Only find new countries.",default=False)
    parser.add_option("-r","--rss",dest="rss",action="store_true",help="Build RSS feed.",default=False)
    parser.add_option("-p","--private",dest="private",action="store_true",help="Do not write cache file!",default=False)
    parser.add_option("-v","--verbose",dest="verbose",action="store_true",help="Extra output",default=False)
    (options, args) = parser.parse_args()

    verbose = options.verbose
    display = options.display
    newonly = options.newonly
    rss = options.rss
    private = options.private
    loan_count = options.count
    
    if options.kiva_id is None:
        if 'GATEWAY_INTERFACE' not in os.environ:
            kiva_id = os.environ["USER"]
        else:
            exit(3)
    else:
        kiva_id = options.kiva_id
        
    if not lender.check_lender_id(kiva_id):
        print "Lender ID is invalid."
        exit(1)
    


#
# Done deciding if we're CGI or CLI
#

my_countries, not_loaned = lender.read_lender_file(kiva_id,private,verbose,display)
loans_found = loan.find_new_loans(not_loaned,loan_count,verbose)

if newonly:
    print "Searched all new countries."
    exit(0)

if rss:
    import country
    codes = country.get_codes(not_loaned)
    loan.display_link(codes,rss)

if len(loans_found) < loan_count:
    print "Found %s loans for new countries. Looking for less used countries." % len(loans_found)
    loans_found = loan.find_old_loans(loans_found,my_countries,loan_count,verbose)

if verbose:
    print "Looks like we ran out of countries..."
if len(loans_found) > 0:
    loan.display_link(loans_found)

if 'GATEWAY_INTERFACE' in os.environ:
    print '</p>'


exit(3)
