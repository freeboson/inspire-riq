#!/usr/bin/env python
'''
inspire-req.py -- InspireHep riq-index calculation
Copyright 2015 Sujeet Akula (sujeet@freeboson.org)
Licensed under GNU GPLv2

More info:
 * http://github.com/freeboson/inspire-req/
 * http://arXiv.org/abs/1209.2124
'''
import urllib2
from urllib import urlencode
from lxml import etree
from StringIO import StringIO
from HTMLParser import HTMLParser
import re, feedparser
import numpy as np

from time import mktime, gmtime
from datetime import datetime
seconds_in_year = 3.15569e7

headers = { 'User-Agent' :  
            'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'}

base_url = 'http://inspirehep.net/rss'
base_dat = {'ln' : 'en',
            'rg' : '500'} # rg is number of entries
                          # should fix this part

record_filter = re.compile(r'.*record\/([\d]*)[/]{,1}') # id will be in \1

marc = '{http://www.loc.gov/MARC21/slim}'

def fetch_records(search):
    
    records = list()

    data = base_dat
    data['p'] = search

    request = urllib2.Request(base_url, urlencode(data), headers)
    xml = urllib2.urlopen(request).read()

    feed = feedparser.parse(xml)
    for entry in feed.entries:
        records.append(record_filter.sub(r'\1', entry.id))

    return records

def get_bib_length(inspire_id):

    url = u'http://inspirehep.net/record/{}/export/xm'.format(inspire_id)
    xml = urllib2.urlopen(urllib2.Request(url)).read()

    root = etree.parse(StringIO(xml)).getroot()
    record = root.find(marc + 'record').getiterator()

    # if you could "jump" to the last record with these tags
    # you could get the id of the last reference, which is 
    # equivalent to the count -- not sure if I can with etree
    count = 0
    for elem in record:
        if elem.get('tag') == '999' and \
            elem.get('ind1') == 'C' and \
            elem.get('ind2') == '5':
            count += 1

    return float(count)

def get_num_authors(inspire_id):

    url = u'http://inspirehep.net/record/{}/export/xd'.format(inspire_id)
    xml = urllib2.urlopen(urllib2.Request(url)).read()

    feed = feedparser.parse(xml)
    return float(len(feed.feed.get('authors')))

def get_pub_date(inspire_id):

    url = u'http://inspirehep.net/record/{}/export/xd'.format(inspire_id)
    xml = urllib2.urlopen(urllib2.Request(url)).read()

    feed = feedparser.parse(xml)
    return datetime.fromtimestamp(mktime(feed.feed.get('updated_parsed')))

def riq_analysis(author="S.Akula.1"):

    print("Computing riq index for InspireHep author " + author + ".")

    print("Fetching " + author + "'s bibliography...")
    papers = fetch_records("author:{0}".format(author))
    num_authors = np.array(map(get_num_authors, papers))
    print("{} has {} papers on InspireHep.net".format(author,len(papers)))
    print("On average, {}'s papers have {} authors".format(author, 
        np.mean(num_authors)))
    
    print("Fetching citing articles (excl. self-cites)...")
    cites = map(lambda recid: fetch_records(
        u"refersto:recid:{} -author:{}".format(recid,author)), papers)
    print("Found {} citations.".format(sum(map(len,cites))))

    print("Finding bibliography length for citing articles...")
    total_bib_lengths = list()
    cached_lengths = dict()
    for cite_list in cites:
        bib_lengths = np.zeros(len(cite_list))
        for idx in range(len(bib_lengths)):
            recid = cite_list[idx]
            if recid in cached_lengths:
                bib_lengths[idx] = cached_lengths[recid]
            else:
                bib_lengths[idx] = get_bib_length(recid)
                cached_lengths[recid] = bib_lengths[idx]
        total_bib_lengths.append(bib_lengths)

#    print("Saved {} lookups by caching.".format(sum(map(len,cites))
#            -len(cached_lengths)))

    print("Computing tori...")
    r_inverse = np.array([np.sum(np.reciprocal(x)) for x in total_bib_lengths])
    tori = np.dot(r_inverse, np.reciprocal(num_authors))
    print("{}'s tori = {}".format(author,tori))

    print("Computing riq...")
    earliest_pub_date = min(map(get_pub_date, papers))
    years_active = (datetime.fromtimestamp(mktime(gmtime())) -
                         earliest_pub_date).total_seconds()/seconds_in_year
    riq = np.sqrt(tori)/years_active
    print("{}'s riq-index = {}".format(author,np.round(1000*riq)))

if __name__ == "__main__":
    riq_analysis()



