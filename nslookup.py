#!/usr/bin/python3

import dns.resolver

def nslookup(domain, typ="A"):
   result = ""
   rcount = 0
   try:
      answer = dns.resolver.query(domain, typ)
      for rdata in answer:
         if rcount > 0:
            result += "\n"
         if hasattr(rdata, 'exchange'):
            result += str(rdata.preference)+" "+str(rdata.exchange)
            rcount += 1
         else:
            result += str(rdata)
            rcount += 1
   except dns.resolver.NXDOMAIN as err:
      result = str(err)
   except Exception as err:
      result = "Error"
      print("nslookup error! - "+str(err))
   del answer
   return result

def main():
   print(nslookup("elmo.space", "AAAA"))

if __name__ == "__main__":
   main()
