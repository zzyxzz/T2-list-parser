#!/usr/bin/python  
#-*- coding: utf-8 -*-
#
# Create by Meibenjin. 
#
# Last updated: 2013-04-02
#
# google search results crawler 
# 
# Modified by Shawn
# Date: 07/05/2015

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib2, socket, time
import gzip, StringIO
import re, random, types

from bs4 import BeautifulSoup 
import csv

base_url = 'https://www.google.co.uk/'
results_per_page = 3

user_agents = list()

# results from the search engine
# basically include url, title,content
class SearchResult:
    def __init__(self):
        self.url= '' 
        self.title = '' 
        self.content = '' 

    def getURL(self):
        return self.url

    def setURL(self, url):
        self.url = url 

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = title


    def printIt(self, prefix = ''):
        print 'url\t->', self.url
        print 'title\t->', self.title

    def writeFile(self, filename):
        file = open(filename, 'a')
        writer = csv.writer(file)
        row = [self.url, self.title]
        try:
            writer.writerow([s.encode("utf-8") for s in row])
        except IOError, e:
            print 'file error:', e
        finally:
            file.close()


class GoogleAPI:
    def __init__(self):
        timeout = 40
        socket.setdefaulttimeout(timeout)

    def randomSleep(self,type='error'):
        if type == 'error':
            sleeptime =  random.randint(60, 120)
            time.sleep(sleeptime)
        elif type == "delay":
            sleeptime = random.randint(30, 60)
            time.sleep(sleeptime)

    #extract the domain of a url
    def extractDomain(self, url):
        domain = ''
        pattern = re.compile(r'http[s]?://([^/]+)/', re.U | re.M)
        url_match = pattern.search(url)
        if(url_match and url_match.lastindex > 0):
            domain = url_match.group(1)

        return domain

    #extract a url from a link
    def extractUrl(self, href):
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]+)/', re.U | re.M)
        url_match = pattern.search(href)
        if(url_match and url_match.lastindex > 0):
            url = url_match.group(1)

        return url 

    # extract serach results list from downloaded html file
    def extractSearchResults(self, html):
        soup = BeautifulSoup(html)
        div = soup.find('div', id  = 'search')
        if (type(div) != types.NoneType):
            lis = div.findAll('li', {'class': 'g'})
            if(len(lis) > 0):
                for li in lis:
                    
                    h3 = li.findAll('h3', {'class': 'r'})
                    if(type(h3) == types.NoneType):
                        continue

                    # extract domain and title from h3 object
                    for h in h3:
                        result = SearchResult()
                        # print h
                        # print "-------"
                        link = h.find('a')
                        if (type(link) == types.NoneType):
                            continue
                        url = link['href']
                        url = self.extractDomain(url)
                        if(cmp(url, '') == 0):
                            continue
                        title = link.renderContents()
                        if "maps.google" in url:
                            continue
                        result.setURL(url)
                        result.setTitle(title)
                        return result
        return SearchResult()

    # search web
    # @param query -> query key words 
    # @param lang -> language of search results  
    # @param num -> number of search results to return 
    def search(self, query, lang='en', num=results_per_page):
#        search_results = list()
        query = urllib2.quote(query)
        if(num % results_per_page == 0):
            pages = num / results_per_page
        else:
            pages = num / results_per_page + 1

        for p in range(0, pages):
            start = p * results_per_page 
            url = '%s/search?hl=%s&num=%d&start=%s&q=%s' % (base_url, lang, results_per_page, start, query)
            retry = 3
            while(retry > 0):
                try:
                    request = urllib2.Request(url)
                    length = len(user_agents)
                    index = random.randint(0, length-1)
                    user_agent = user_agents[index] 
                    request.add_header('User-agent', user_agent)
                    request.add_header('connection','keep-alive')
                    request.add_header('Accept-Encoding', 'gzip')
                    request.add_header('referer', base_url)
                    response = urllib2.urlopen(request)
                    html = response.read()

                    if(response.headers.get('content-encoding', None) == 'gzip'):
                        html = gzip.GzipFile(fileobj=StringIO.StringIO(html)).read()

                    result = self.extractSearchResults(html)
                    break

                except urllib2.URLError,e:
                    print 'url error:', e
                    self.randomSleep()
                    retry = retry - 1
                    continue
                
                except Exception, e:
                    print 'error:', e
                    retry = retry - 1
                    self.randomSleep()
                    continue
        return result 

def load_user_agent():
    fp = open('./files/user_agents', 'r')

    line  = fp.readline().strip('\n')
    while(line):
        user_agents.append(line)
        line = fp.readline()
    fp.close()

def crawler():
    # Load use agent string from file
    load_user_agent()

    # Create a GoogleAPI instance
    api = GoogleAPI()

    # set expect search results to be crawled
    expect_num = 1
    # read company names from file
    with open('./files/data.csv', 'r') as t2_list:
        reader = csv.reader(t2_list)
        for company in reader:
            name = company[0].rstrip()
            if not name:
                continue
            results = api.search(name, num = expect_num)
            results.writeFile("./files/urls.csv")
            api.randomSleep(type='delay')

if __name__ == '__main__':
    crawler()
