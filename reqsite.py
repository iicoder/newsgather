#coding=utf-8
#author@alingse
#2016.08.17

from __future__ import print_function

from pyquery import PyQuery as pq
from urllib import quote
import urlparse
import re

from random import choice
import json
import sys

hreffind = re.compile('href *= *[\'"]([^\'"<]*)').findall

class siteReq(object):

    def __init__(self, site):
        self.site = site

    def is_allow(self,host):
        for match in self.site.allow_hosts_matches:
            if match(host):
                return True

    def is_url(self,url):
        for match in self.site.url_matches:
            if match(url):
                return True

    def is_index(self,url):
        for match in self.site.index_matches:
            if match(url):
                return True

    def is_invalidtail(self,tail):
        if tail in self.site.invalid_tails:
            return True

    @staticmethod
    def chg_ua(site,onlypc=None,onlymb=None):
        if onlymb and onlypc:
            #raise Exception("")
            return False
        #ua = site.headers['User-Agent']
        if onlypc:
            ualist = site.user_agents.pc
        elif onlymb:
            ualist = site.user_agents.mobile
        else:
            ualist = choice([site.user_agents.mobile,site.user_agents.pc])

        site.headers['User-Agent'] = choice(ualist)
        return True

    def chg_my_ua(self,**kwargs):

        return self.chg_ua(self.site,**kwargs)

    def req_html(self,url):
        self.chg_my_ua()
        html = self.site.req_html(url)
        return html


    def req_meta(self,url):
        self.chg_my_ua()
        meta = self.site.req_meta(url)
        return meta

    #the most important
    def html2links(self,url,html):
        site = self.site
        host = site.host
        urld = urlparse.urlparse(url)
        #
        urlhost = '{0.scheme}://{0.netloc}'.format(urld)
        urlpath = urlhost + urld.path

        hrefs = hreffind(html)
        links = []
        for href in hrefs:
            if href.startswith('//'):
                href = href.strip('//')
            elif href.startswith('/'):
                href = urlhost + href
            elif '://' not in href:
                href = urlpath + href

            links.append(href)
        return links


    def shuffle(self,links):
        site = self.site
        urls = set()
        indexes = set()
        for link in links:
            try:
                linkd = urlparse.urlparse(link)
            except Exception as e:
                print('err:parse,',link)
                continue

            #check - tail
            path = linkd.path
            tail = path[path.rfind('.'):]
            if self.is_invalidtail(tail):
                continue
            '''
            if not self.is_allow(linkd.host):
                continue
            '''

            try:
                _path = path.encode(self.site.urlcharset)
            except Exception as e:
                print('err:encode',e,link)
                continue

            #not ascii
            if len(path) != len(_path):
                #解决unicode unquote url                
                path = quote(_path)

            linkdlst = list(linkd)
            linkdlst[2] = path
            linkdlst[-1] = ''

            link = urlparse.urlunparse(linkdlst)
            
            if self.is_url(link):
                urls.add(link)
    
            elif self.is_index(link):
                indexes.add(link)

        urls = list(urls)
        indexes = list(indexes)
        return urls,indexes
        

if __name__ == '__main__':
    from requtil import load_sites
    slist = load_sites()
    site = slist[0]

    link = choice(site.seeds)
    
    req = siteReq(site)
    html = req.req_html(link)
    #print(html)
    links = req.html2links(link,html)
    urls,indexes = req.shuffle(links)
    print('url')
    map(print,urls)
    print('index')
    map(print,indexes)
    links = [
        u'http://www.cnblogs.com/ansiboy/tag/Linq%2bAccess%2bC%23/',
        u'http://www.cnblogs.com/ansiboy/tag/Linq+Access+C#/',
        u'http://www.cnblogs.com/unruledboy/tag/技术栈/'
        ]
    urls,indexes = req.shuffle(links)
    print('url')
    map(print,urls)
    print('index')
    map(print,indexes)
