#
# -*- coding: utf-8 -*-
#  Amal Roumi

#---------------------------------------------------------------------------------
import pymycraawler # to import the __init__.py file  from the folder pymycraawler
import argparse
import datetime
import time # to calculate  elapsed time 

def start_greeting():
    """Print some messages about this crawler"""
    print "==========================================================="
    print "Web-spider  for the Development Tools ,MSWL  course, 2013/2014"
    print "Amal Roumi, email: roumia@gmail.com"
    print " let start crawling "
def summary(depth,end,start):
    """ Print summary messages  and calculate the elapsed time """
    elapsed = end - start
    elapsed_time_int = int(elapsed)
    print "-----------------------------------------------------"
    print " '*' indicated to the level depth"
    print ' Time taken for crawling {} level is :{} seconds ' \
                              .format (depth,elapsed_time_int)
    print "Done :D "

def print_links (url,n):
    """  to make loop to and extract the url in the crawleing depth   """
    page_counter = 0
    if n == 0:
       print "Root"
    enlaces = pymycraawler.retrieve_url (url)
      
    for l in enlaces:
       print " %s %s " % ("*"*n,l)  
       print_links (l,n-1)
       page_counter +=1  # to count number of pages crawled  in the 
    print (" %s Webpages were crawled " % (page_counter))
     
def main():
    start = time.time()  #to start calculate the elapsed time 
    parser = argparse.ArgumentParser ( description = 'This application is for crawling the web page ! '\
                                             ,version ='0.1')

    parser.add_argument ( '-n' , '--number-of-levels' , type = int ,\
                            default =1 ,help = 'how deep the crawler will go')

    parser.add_argument ('URL', nargs=1,help= 'Target URL to crawle ' )

    args = parser.parse_args ()
    depth = args.number_of_levels
    url =args.url[0]
    start_greeting()        # calling the function greeting
    print_links(url,depth)  # calling the function print_links
    end = time.time()       #"to end calculate the elapsed time "
    summary(depth,end,start)# calling the function summary
if __name__=='__main__':
       main ()
