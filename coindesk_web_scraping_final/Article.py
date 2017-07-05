import selenium
from selenium import webdriver
import urllib.request
from bs4 import BeautifulSoup
import re
import time
import random
from settings import *
from Article_database import Article_database

class Article():
    def __init__(self, settings, webpage_url):
        
        self.db_host = settings["db_host"]
        self.db_user = settings["db_user"]
        self.db_password = settings["db_password"]
        self.db_port = settings["db_port"]
        self.db_use_unicode = settings["db_use_unicode"]
        self.charset = settings["charset"]
        self.db_name = settings["db_name"]
        self.webpage_url = webpage_url
        self.article_instance = Article_database(self.db_user,self.db_password,self.db_name, self.db_host,self.db_port,self.db_use_unicode,self.charset)
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

    #Find all links on website by autoclick loadmore button
    def click_to_end(self, webpage):
        self.dr = webdriver.PhantomJS(executable_path='C:\\Users\\win10\\Downloads\\phantomjs-2.1.1-windows\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')
        self.dr.get(webpage)
        #for i in range(2):
        for i in range(837):
            self.btn = self.dr.find_element_by_css_selector('#byscripts_ajax_posts_loader_trigger')
            self.btn.click()
            time.sleep(8)
        print('Finish loading all articles.')
        return self.dr.page_source

    def store_articles(self, pageSource):

        self.homepage = BeautifulSoup(pageSource, "html.parser")

        def deal_with_a_tag(atag):
            if 'href' in atag.attrs:
                article_url = atag.attrs['href']
                if not self.article_instance.article_url_exists_in_table(article_url):
                    response = self.opener.open(article_url)
                    time.sleep(random.randint(4,10))
                    indiv_article = BeautifulSoup(response, "html.parser")
                    try:
                        source = self.webpage_url

                        title = indiv_article.find("div", {"class":"article-meta"}).find("h3", {"class":"featured-article-title"})        
                        title = title.get_text().strip()

                        author = indiv_article.find("div", {"class":"article-meta"}).p.a
                        author = author.get_text()
                        
                        paras_list = indiv_article.find("div", {"class":"article-content-container"}).findAll("p")
                        content = ''
                        for para in paras_list:
                            para = re.sub(r'\/\*\ <!\[.*\]>\ \*\/', "", para.get_text())
                            content = content + para
                            
                        written_time = indiv_article.find("div", {"class":"article-meta"}).p.time.attrs['datetime']
                        written_time = written_time.replace("T", " ").replace("+00:00", "")

                        now = time.localtime(time.time())
                        collection_time = time.strftime("%Y-%m-%d %H:%M:%S", now)

                    except AttributeError:
                        print("This page is missing something")

                    article_info = (source, title, written_time, author, article_url, content, collection_time)
                    
                    
                    try:
                        self.article_instance.insert_article_into_articles(article_info)
                        print("Article Stored Successfully.")
                    except:
                        print("Unable to store the article.")

                else:
                    print("Article already stored.")

        self.div_tag_set_featured = self.homepage.find("div", {"class":"grid_6 main blog-one"}).findAll("div", {"class":"article article-featured"})
        for div_tag in self.div_tag_set_featured:
            a_tag = div_tag.a
            deal_with_a_tag(a_tag)

        self.div_tag_set_postinfo = self.homepage.find("div", {"class":"grid_6 main blog-one"}).findAll("div", {"class":"post-info"})
        for div_tag in self.div_tag_set_postinfo:
            a_tag = div_tag.h3.a
            deal_with_a_tag(a_tag)
        
                    
        print("Finish storing all articles.")

    def store_previous_articles(self):
        return self.store_articles(self.click_to_end(self.webpage_url))

    def store_new_articles(self):
        while True:
            self.store_articles(self.webpage_url)
            time.sleep(86400)

    def store_sources(self):
        self.webpage_name = self.webpage_url.replace('http://www.', '').replace('.com/', '')
        self.source_info = (self.webpage_name, self.webpage_url)
        if not self.article_instance.source_information_exists_in_table(self.webpage_url):
            try:
                self.article_instance.insert_source_into_sources(self.source_info)
                print("Source information stored successfully.")
            except:
                print("Unable to store source information.")
        else:
            print("Source information has already been stored.")

coindesk_page = "http://www.coindesk.com/"
cd = Article(settings, coindesk_page)
cd.store_sources()
cd.store_previous_articles()
cd.store_new_articles()

