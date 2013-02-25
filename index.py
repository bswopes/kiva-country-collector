#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import subprocess as sub
import urllib
import os
import Cookie
import string
import re
from sys import exit
from optparse import OptionParser
import lender
import loan

if 'GATEWAY_INTERFACE' in os.environ:
    cgitb.enable()
    print "Content-Type: text/html;charset=utf-8"

    form = cgi.FieldStorage()

    bool_args = ""
    set_cookie = True
    arg_list = form.getlist("arguments")

    if 'verbose' in arg_list:
        verbose = True
    else:
        verbose = False
    if 'display' in arg_list:
        display = True
    else:
        display = False
    if 'newonly' in arg_list:
        newonly = True
    else:
        newonly = False
    if 'private' in arg_list:
        private = True
        set_cookie = False
    else:
        private = False
        set_cookie = True

    if len(bool_args) > 0:
        bool_args = '-' + bool_args

    kiva_id = cgi.escape(form.getfirst('lender', 'empty')).strip('"\'')

    if kiva_id == 'empty':
            try:
                    cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
                    kiva_id = cookie["lender"].value
            except:
                    print

    kiva_id = lender.check_lender_id(kiva_id)
    if set_cookie:
        print 'Set-Cookie: lender=' + kiva_id
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
    parser.add_option("-p","--private",dest="private",action="store_true",help="Do not write cache file!",default=False)
    parser.add_option("-v","--verbose",dest="verbose",action="store_true",help="Extra output",default=False)
    (options, args) = parser.parse_args()

    verbose = options.verbose
    display = options.display
    newonly = options.newonly
    private = options.private
    loan_count = options.count
    
    if options.kiva_id is None:
        if 'GATEWAY_INTERFACE' not in os.environ:
            kiva_id = lender.check_lender_id(os.environ["USER"])
        else:
            exit(3)
    else:
        kiva_id = lender.check_lender_id(options.kiva_id)


#
# Done deciding if we're CGI or CLI
#



#p = sub.Popen(['./kcc.py',bool_args,'-i',kiva_id,'-c',loan_count],stdout=sub.PIPE)
#output = urllib.unquote(p.stdout.read())
##output = output.split('Visit Kiva at: ')


my_countries, not_loaned = lender.read_lender_csv(kiva_id,private,verbose,display)
loans_found = loan.find_new_loans(not_loaned,loan_count,verbose)

if newonly:
    print "Searched all new countries."
    exit(0)

if len(loans_found) < loan_count:
    print "Found %s loans for new countries. Looking for less used countries." % len(loans_found)
    loans_found = loan.find_old_loans(loans_found,my_countries,loan_count,verbose)

if verbose:
    print "Not sure how we ended up here..."
if len(loans_found) > 0:
    loan.display_link(loans_found)

if 'GATEWAY_INTERFACE' in os.environ:
    print '</p>'


exit(3)