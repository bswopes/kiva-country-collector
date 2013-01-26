kiva-country-collector
=======================

Check Kiva for loans from countries you haven't loaned to.

If no new countries are found, check for loans starting with countries you have loaned to the least.

Writes to csv file with lender country code / count, to reduce API calls. Use -u (--update) to force an update.

$ ./kcc.py -i bswopes -c2  
No new countries found. Looking for less used countries.  
Country India, previous loan count 1.  
Country Cameroon, previous loan count 2.  
Visit Kiva at: http://www.kiva.org/lend#/?app_id=com.bhodisoft.kcc&countries[]=IN,CM  
