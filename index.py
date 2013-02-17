#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
import cgi
import subprocess as sub
import urllib
import os
import Cookie
from sys import exit
cgitb.enable()

print "Content-Type: text/html;charset=utf-8"

form = cgi.FieldStorage()

bool_args = ""
set_cookie = True
arg_list = form.getlist("arguments")

if "verbose" in arg_list:
	bool_args = bool_args + "v"
if "findall" in arg_list:
	bool_args = bool_args + "f"
if "newonly" in arg_list:
	bool_args = bool_args + "n"
if "private" in arg_list:
	bool_args = bool_args + "p"
        set_cookie = False

if len(bool_args) > 0:
	bool_args = "-" + bool_args

lender = cgi.escape(form.getfirst('lender', 'empty')).strip('"\'')

if lender == "empty":
        try:
                cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
                lender = cookie["lender"].value
        except:
                print


if lender.isalnum() is False or len(lender) < 3 or len(lender) > 24:
        print "Lender ID is invalid."
	exit(0)
else:
        if set_cookie:
                print "Set-Cookie: lender=" + lender
        print
	print "<p>Hello %s!</p>" % lender

count = form.getfirst('count','1')
if not count.isdigit() and int(count) <= 0:
	count = "1"

p = sub.Popen(["./kcc.py",bool_args,"-i",lender,"-c",count],stdout=sub.PIPE)
output = urllib.unquote(p.stdout.read())
output = output.split("Visit Kiva at: ")

print "<pre>%s</pre>" % output[0]

if len(output) == 2:
	print 'Visit Kiva <a href="%s" target=_top>HERE</a>' % output[1]
