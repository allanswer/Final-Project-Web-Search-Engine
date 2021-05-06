#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
from collections import deque
import certifi
import re
import nltk
import os
from itertools import chain
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import itertools
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import math
import operator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.request import urljoin
from bs4 import BeautifulSoup
from urllib.request import urlparse
import ssl
# Set for storing urls with same domain
depth = 1
links_intern = set()

# importan variable
input_url = "https://www.uic.edu/"
hashtable = {} 
depth = 10
# ***************

docmap = {}
stop_words = set(stopwords.words("english"))
# Set for storing urls with different domain
links_extern = set()
lem = WordNetLemmatizer()
desirednum = 3200


# In[2]:


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


# In[3]:


# tokenize query or text
def tokenize(query, qMap):
    tmp = {}
    query = re.sub(r'[^A-Za-z]+', ' ', query).lower()
    token_word = word_tokenize(query)
    for word in token_word:
        if word not in stop_words and not word.isdigit():
            word = lem.lemmatize(word)
            qMap[word] = qMap.setdefault(word, 0) + 1       
    return qMap


# In[4]:


def tokenizeContents(url, query, qMap):
    query = re.sub(r'[^A-Za-z]+', ' ', query).lower()
    token_word = word_tokenize(query)
    for word in token_word:
        if word not in stop_words and not word.isdigit():
            word = lem.lemmatize(word)
            # append new dict to existing dict of that word
            if word in word_tokenized:
                tmpdict = word_tokenized[word]
                tmpdict[url] = tmpdict.setdefault(url, 0) + 1 
            #create a dict to that word with corresponding url
            else:
                tmp = {}
                tmp[url] = 1
                word_tokenized[word] = tmp
                      
    return word_tokenized


# In[5]:


def returnContent(input_url):
    text = ''
    try:
        r = requests.get(input_url, verify=False)
        text = BeautifulSoup(r.text, "lxml").text
        return text
    except:
        print("An exception occurred while getting content")
        return text


# In[18]:


# initialize queries
query1 = {}
query2 = {}
query3 = {}
query4 = {}
query5 = {}

query1 = tokenize("appointment vaccine", query1)
query2 = tokenize("basketball court", query2)
query3 = tokenize("register course", query3)
query4 = tokenize("job board", query4)
query5 = tokenize("train station", query5)
print(query1, query2, query3, query4, query5)


# In[7]:


# Set for storing urls with same domain
links_intern = set()
hashtable = {}
input_url = "https://www.uic.edu/"
  
# Set for storing urls with different domain
links_extern = set()
  
  
# Method for crawling a url at next level
def level_crawler(input_url):
    temp_urls = set()
    current_url_domain = urlparse(input_url).netloc
#     print(current_url_domain)
    if ".uic.edu" not in current_url_domain:
        return
    
    
    # Creates beautiful soup object to extract html tags
    try:
        r = requests.get(input_url, verify=False)
        beautiful_soup_object = BeautifulSoup(r.content, "lxml")
    except:
        print("An exception occurred")
        return
  
    # Access all anchor tags from input 
    # url page and divide them into internal
    # and external categories
    for anchor in beautiful_soup_object.findAll("a"):
        href = anchor.attrs.get("href")
        if(href != "" or href != None):
            href = urljoin(input_url, href)
            href_parsed = urlparse(href)
            href = href_parsed.scheme
            href += "://"
            href += href_parsed.netloc
            href += href_parsed.path
            final_parsed_href = urlparse(href)
            is_valid = bool(final_parsed_href.scheme) and bool(
                final_parsed_href.netloc)
            if is_valid:
                if ".uic.edu" not in href and href not in links_extern:
#                     print("Extern - {}".format(href))
                    links_extern.add(href)
                if ".uic.edu" in href and href not in links_intern:
#                     print("Intern - {}".format(href))
                    text = returnContent(href)
                    if(text ==''):
                        continue
                    else:
                        links_intern.add(href)
                        hashtable[href] = text
#                     links_intern.add(href)
#                     hashtable[href] = BeautifulSoup(r.text, "lxml").text
                    temp_urls.add(href)
    return temp_urls
  
  
if(depth == 0):
    print("Intern - {}".format(input_url))
  
elif(depth == 1):
    level_crawler(input_url)
  
else:
    # Used a BFS approach
    queue = []
    queue.append(input_url)
    for j in range(depth):
        print("depth:", j)
        for count in range(len(queue)):
            if(count %10 == 0) :
                print("links_intern", len(links_intern))
            if(len(links_intern) > desirednum):
                print("Reach 3200")
                break
            url = queue.pop(0)
            urls = level_crawler(url)
            s = requests.session()
            s.keep_alive = False
            if(not urls):
                print("Out of domain:", urls)
                continue
            for i in urls:
                queue.append(i)


# In[17]:


print("Size of links_intern:", len(links_intern))
lem = WordNetLemmatizer()


# In[10]:


# tokenize each contens of each links
# map[word] = {url: cnt....}
global word_tokenized
print("Total links to be tokenize:",len(hashtable))
word_tokenized = {}
progress = 0
for i in hashtable:
     
    tokenizeContents(i, hashtable[i], word_tokenized)
    
    #print progress
    progress += 1
    if(progress %50 == 0 or progress == len(hashtable)):
        print(progress)
# print(word_tokenized)


# In[11]:



print(len(word_tokenized))


# In[12]:


def getTfidf_Length(hashtable, query):
    N = len(hashtable)

    tfidf_word_in_link = {}
    length_word_in_link = {}

    for qword in query:
        qtf = query[qword]
        print(qword)
        if qword in word_tokenized:
    #         print(word_tokenized[qword])
            dft = len(word_tokenized[qword])
            idf = math.log(N / (dft))
            print("In " + str(dft) + " links")
            #calcaulate tf-idf in each links
            for link in word_tokenized[qword]:
                tf = word_tokenized[qword][link]
                tf_idf = tf * idf
                dot = qtf * tf_idf
                tfidf_word_in_link[link] = tfidf_word_in_link.setdefault(link, 0) + dot
                length_word_in_link[link] = length_word_in_link.setdefault(link, 0) + pow(tf_idf, 2)
                #print(length_word_in_link)
    return  tfidf_word_in_link,  length_word_in_link         


# In[20]:


# calculate sum of tf-idf to see which is relevant
#q1{go:1, chicago:1}, tf = 1, 1, idfs are same.
#caculate cosine simiiar = (Vq*Vt)/(|Vq| * |Vt|), the length of Vq are same, so we only need the length of Vt

print("Query1----------------------")
tfidf_word_in_link1, length_word_in_link1 = getTfidf_Length(hashtable, query1)

print("Query2----------------------")
tfidf_word_in_link2, length_word_in_link2 = getTfidf_Length(hashtable, query2)

print("Query3----------------------")
tfidf_word_in_link3, length_word_in_link3 = getTfidf_Length(hashtable, query3)

print("Query4----------------------")
tfidf_word_in_link4, length_word_in_link4 = getTfidf_Length(hashtable, query4)

print("Query5----------------------")
tfidf_word_in_link5, length_word_in_link5 = getTfidf_Length(hashtable, query5)

# N = len(hashtable)

# tfidf_word_in_link = {}
# length_word_in_link = {}

# for qword in query:
#     qtf = query[qword]
#     print(qword)
#     if qword in word_tokenized:
# #         print(word_tokenized[qword])
#         dft = len(word_tokenized[qword])
#         idf = math.log(N / (dft))
#         print("In " + str(dft) + " links")
#         #calcaulate tf-idf in each links
#         for link in word_tokenized[qword]:
#             tf = word_tokenized[qword][link]
#             tf_idf = tf * idf
#             dot = qtf * tf_idf
#             tfidf_word_in_link[link] = tfidf_word_in_link.setdefault(link, 0) + dot
#             length_word_in_link[link] = length_word_in_link.setdefault(link, 0) + pow(tf_idf, 2)
#             #print(length_word_in_link)
            


# In[21]:


def getResAndRank(tfidf_word_in_link, length_word_in_link):
    cosineres = {}
    for i in length_word_in_link:
        length_word_in_link[i] = math.sqrt(length_word_in_link[i])
        cosineres[i] =  tfidf_word_in_link[i] / length_word_in_link[i]

    # Sort results
    sorted_cosine = dict( sorted(cosineres.items(), key=operator.itemgetter(1),reverse=True))
    cnt = 0
    for link in sorted_cosine:
        print("No." + str(cnt + 1) + " link: " + link + " ," + str(sorted_cosine[link]))
        cnt += 1
        if(cnt == 10): break
    


# In[26]:


#Get results of cosine similarities and rank them


print("Ranks of Query1----------------------" + "appointment vaccine")
getResAndRank(tfidf_word_in_link1, length_word_in_link1)
print('\n')

print("Ranks of Query2----------------------" + "basketball court")
getResAndRank(tfidf_word_in_link2, length_word_in_link2)
print('\n')

print("Ranks of Query3----------------------" + "register course")
getResAndRank(tfidf_word_in_link3, length_word_in_link3)
print('\n')

print("Ranks of Query4----------------------" + "job board")
getResAndRank(tfidf_word_in_link4, length_word_in_link4)
print('\n')

print("Ranks of Query5----------------------" + "train station")
getResAndRank(tfidf_word_in_link5, length_word_in_link5)
print('\n')

# cosineres = {}
# for i in length_word_in_link:
#     length_word_in_link[i] = math.sqrt(length_word_in_link[i])
#     cosineres[i] =  tfidf_word_in_link[i] / length_word_in_link[i]
    
# # Sort results
# sorted_cosine = dict( sorted(cosineres.items(), key=operator.itemgetter(1),reverse=True))
# cnt = 0
# for link in sorted_cosine:
#     print("No." + str(cnt + 1) + " link: " + link + " ," + str(sorted_cosine[link]))
#     cnt += 1
#     if(cnt == 10): break


# In[27]:


print("finish")


# In[ ]:




