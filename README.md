kiva-country-collector
=======================

Check Kiva for loans from countries you haven't loaned to.

If no new countries are found, check for loans starting with countries you have loaned to the least.

Writes to csv file with lender country code / count, to reduce API calls. Use -u (--update) to force an update.

$ ./index.py -i bswopes -c2  
No new countries found. Looking for less used countries.  
Country India, previous loan count 1.  
Country Cameroon, previous loan count 2.  
Visit Kiva at: http://www.kiva.org/lend#/?app_id=com.bhodisoft.kcc&countries[]=IN,CM  

### Notes

If you want to use this code on your own site, you will need to edit the url in index.html, 
to prevent it redirecting back to my domain.

> if(top === self){  
>   top.location.href = 'http://www.bhodisoft.com/kiva-country-collector/';  
> }  
