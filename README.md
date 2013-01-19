kiva-country-collector
=======================

Check Kiva for loans from countries you haven't loaned to.

If no new countries are found, check for loans starting with countries you have loaned to the least.

Writes to csv file with lender country code / count, to reduce API calls. Use -u (--update) to force an update.

$ ./kiva-loans.py -i bswopes -c 2  
User ID: bswopes  
Read data from file: bswopes.csv  
User has previously loaned to: AF, AL, AM, AZ, BF, BI, BJ, BO, CD, CG, CL, CM, CO, CR, DO, EC, GE, GH, GT, HN, HT, ID, IL, IN, IQ, JO, KE, KG, KH, LB, LR, ML, MN, MX, MZ, NI, PE, PH, PK, PS, PY, QS, RW, SL, SN, SV, TG, TJ, TL, TZ, UA, UG, US, VN, WS, XK, YE, ZA, ZM, ZW  
No new countries found. Looking for less used countries.  
Found 2 loans for country KOSOVO  
Country KOSOVO, previous loan count 3.  
Visit Kiva at: http://www.kiva.org/lend#/?countries[]=XK  
Found 42 loans for country BOLIVIA, PLURINATIONAL STATE OF  
Country BOLIVIA, PLURINATIONAL STATE OF, previous loan count 3.  
Visit Kiva at: http://www.kiva.org/lend#/?countries[]=BO  
Reached specified number of countries.  
