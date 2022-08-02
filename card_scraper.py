#counts frequency of word within list
from collections import Counter

#for punction replacement
import string

#package for translating
from deep_translator import GoogleTranslator,MyMemoryTranslator

#package to scrape reddit data
import praw
from praw.models import MoreComments

#package to run lemmatisation
import spacy

import pandas as pd

import time

#create id,secret and agent from create app option in reddit here: 
#https://www.reddit.com/prefs/apps
#username/password as redit login
r = praw.Reddit(
    client_id="ydNnLEGvxTnJB9Dxo6Y87w",
    client_secret="zp1imQRPyJblAwUx5RDVc9w3Fim_mw",
    password="r1b0lly",
    user_agent="ab_data_scraper",
    username="Integratedlemon",
)

def scrape(page,posts=10):
    '''returns list of commets scraped from
    selected subreddit'''
    
    #create subreddit class
    subreddit = r.subreddit(page)
    
    sl = [] #stores all comment data
    
    #for each sub in the top subs, for each comment 
    #if comment is true comment then append to main list
    for sub in subreddit.top(time_filter = 'month',limit=posts): 
        for comment in sub.comments.list():
            if isinstance(comment, MoreComments):
                continue
            sl.append(' '.join(comment.body.split()))
            
    return sl
    
    
def lang_mod(lang):
    '''loads in model of selected language'''
    
    #parser and ner not needed so disabled to save space
    if lang == "italian":
        load_model = spacy.load('it_core_news_sm', disable = ['parser','ner'])
    elif lang == "spanish":
        load_model = spacy.load('es_core_news_sm', disable = ['parser','ner'])
    elif lang == "turkish":
        load_model = spacy.load('xx_ent_wiki_sm', disable = ['parser','ner'])
    else:
        raise ValueError('{} is not a supported language'.format(lang))
    
    return load_model


def symbol_replace(sl):
    '''removes symbols from text'''

    time.sleep(1)
    #replace within each word
    sl = [item.translate(str.maketrans('', '', string.punctuation)) for item in sl]
    
    #removes '' from list
    sl = [item for item in sl if item != '']

    return sl    
        
  
def data_format(sl,load_model,wrds=4):
    ''''''
    
    #convert input to single space
    sl_sp = " ".join(sl)
    
    #split by word
    sl = sl_sp.split(" ") 
    
    #replace symbols
    sl = symbol_replace(sl)
    
    #create version with lemitisation
    sl_mod = load_model(sl_sp)
    sl_lem = [token.lemma_ for token in sl_mod]
    sl_lem = symbol_replace(sl_lem)
        
    #create combination words
    sl2 = [x+' '+y for (x,y) in zip(sl[0::],sl[1:-1:])]
    sl3 = [x+' '+y+' '+z for (x,y,z) in zip(sl[0::],sl[1:-1:],sl[2:-2:])]
    
    sl = Counter(sl).most_common(wrds)
    sl2 = Counter(sl2).most_common(wrds)
    sl3 = Counter(sl3).most_common(wrds)
    sl_lem = Counter(sl_lem).most_common(wrds)
    
    return sl,sl2,sl3,sl_lem

    
def display(sla):
    ''''''
    
    types = ["Single Word","Two Word","Three Word","Lemmatised"]
    
    
    for sl,type in zip(sla,types):
        #print results neatly
        print("\n\n{}\n-------------".format(type))
        for i in sl:
            print(i[0],"     ",i[1])
        print("-------------\n\n")
        
def translator(wrd,phrs,lang):
    ''''''
    
    wrd = MyMemoryTranslator(source=lang, target='english').translate(wrd)
    phrs = MyMemoryTranslator(source=lang, target='english').translate(phrs)     

    return wrd,phrs
    
def examples(sl,sla,load_model,lang,wrds=10):
    ''''''
    #stores all flashcards
    all_cards = []
    
    #sort comments by length
    sl_in = sorted(sl, key=len)
    sl = []

    #convert comments to lemma form
    for comment in sl_in:
        comment = load_model(comment)
        sl.append(" ".join([token.lemma_ for token in comment]))
    
    #look for word in each comment, pick shortest comment
    for i in range(wrds):
        id = list(' '+sla[0][i][0]+' ' in x for x in sl_in).index(True)
        
        wrdt,phrst = translator(sla[0][i][0],sl_in[id],lang)
        
        all_cards.append('{}    {}    {}    {}'.format(sla[0][i][0],sl_in[id],wrdt,phrst))
    #print all card contents    
    for card in all_cards:
        print(card)
        
    print("\n----------------\n")    
    all_cards = []    
        
    #look for word in each comment, pick shortest comment for lemmatised words
    for i in range(wrds):
        id = list(' '+sla[3][i][0]+' ' in x for x in sl).index(True)
        
        wrdt,phrst = translator(sla[0][i][0],sl_in[id],lang)
        
        all_cards.append('{}    {}    {}    {}'.format(sla[3][i][0],sl_in[id],wrdt,phrst))
        
        
        
    #print all card contents      
    for card in all_cards:
        print(card)
        
    def main():
    ''''''
    
    #scrape data from reddit
    sl = scrape(page,posts)
    
    #load lemma model
    load_model = lang_mod(lang)
    
    #create common word lists
    sla = data_format(sl, load_model, wrds)
    
    #display results
    display(sla)
    
    #create flashcards
    examples(sl,sla,load_model,lang,wrds)
    
    print("\n\n\nend of script")
    
    
#language subreddits
#mexico, LatinoPeopleTwitter
#italy, memesITA
#turkey, TurkeyJerky

page = "mexico"   #subreddit
lang = "spanish"    #language of subreddit
posts = 20       #no of submissions
wrds = 50           # how many words to view

main()
