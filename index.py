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
cgitb.enable()

if 'GATEWAY_INTERFACE' in os.environ:

    print "Content-Type: text/html;charset=utf-8"

    form = cgi.FieldStorage()

    bool_args = ""
    set_cookie = True
    arg_list = form.getlist("arguments")

    if 'verbose' in arg_list:
        bool_args = bool_args + 'v'
    if 'findall' in arg_list:
        bool_args = bool_args + 'f'
    if 'newonly' in arg_list:
        bool_args = bool_args + 'n'
    if 'private' in arg_list:
        bool_args = bool_args + 'p'
        set_cookie = False

    if len(bool_args) > 0:
        bool_args = '-' + bool_args

    kiva_id = cgi.escape(form.getfirst('lender', 'empty')).strip('"\'')

    if kiva_id == 'empty':
            try:
                    cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
                    kiva_id = cookie["lender"].value
            except:
                    print

    lender.check_lender_id(kiva_id)
    if set_cookie:
        print 'Set-Cookie: lender=' + kiva_id
    print

    loan_count = form.getfirst('count','1')

else:
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
    loan_count = str(options.count)
    
    bool_args = ""
    if verbose:
        bool_args = bool_args + 'v'
    if findall:
        bool_args = bool_args + 'f'
    if newonly:
        bool_args = bool_args + 'n'
    if private:
        bool_args = bool_args + 'p'
    if len(bool_args) > 0:
        bool_args = '-' + bool_args
    
    if options.kiva_id is None:
        if 'GATEWAY_INTERFACE' not in os.environ:
            kiva_id = os.environ["USER"]
        else:
            exit(3)
    else:
        kiva_id = options.kiva_id
    lender.check_lender_id(kiva_id)

#
# Done deciding if we're CGI or CLI
#

print '<p>Hello %s!</p>' % kiva_id

if not loan_count.isdigit() and int(loan_count) <= 0:
    loan_count = '1'

p = sub.Popen(['./kcc.py',bool_args,'-i',kiva_id,'-c',loan_count],stdout=sub.PIPE)
output = urllib.unquote(p.stdout.read())
output = output.split('Visit Kiva at: ')

print '<pre>%s</pre>' % output[0]

if len(output) == 2:
	print 'Visit Kiva <a href="%s" target=_top>HERE</a>' % output[1]
