import httplib
from sys import exit

limit = 60
remaining = 60

def get_rate(f,verbose=False):
    
    furlinfo = f.info()

    if furlinfo.getheader("X-RateLimit-Specific-Remaining"):
        limit = furlinfo.getheader("X-RateLimit-Specific-Limit")
        remaining = furlinfo.getheader("X-RateLimit-Specific-Remaining")
    else:
        limit = furlinfo.getheader("X-RateLimit-Overall-Limit")
        remaining = furlinfo.getheader("X-RateLimit-Overall-Remaining")
    if verbose:
        print "API Calls Remaining: %s of %s" % (remaining,limit)
    
    return remaining