limit = 60
remaining = 60

def get_rate(f,verbose=False):
    ''' (httpmesg,[bool]) > int,int
    
    Passed http url opened by urllib. 
    
    Returns rate limit information from http headers.
    '''
    
    furlinfo = f.info()

    if furlinfo.getheader("X-RateLimit-Specific-Remaining"):
        limit = int(furlinfo.getheader("X-RateLimit-Specific-Limit"))
        remaining = int(furlinfo.getheader("X-RateLimit-Specific-Remaining"))
    else:
        limit = int(furlinfo.getheader("X-RateLimit-Overall-Limit"))
        remaining = int(furlinfo.getheader("X-RateLimit-Overall-Remaining"))
    if verbose:
        print "API Calls Remaining: %s of %s" % (remaining,limit)
    
    return remaining,limit