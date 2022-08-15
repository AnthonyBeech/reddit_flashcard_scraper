#counts frequency of word within list
from collections import Counter

#for punction replacement
import string

#package for translating
import googletrans
from googletrans import Translator

#package to scrape reddit data
import praw
from praw.models import MoreComments

#package to run lemmatisation
import spacy

#usual imports
import pandas as pd
pd.set_option('display.max_rows', 1000)
import time
from time import sleep
import sys
from tqdm import tqdm

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
    '''returns list of comments scraped from
    selected subreddit'''
    
    print('scraping comments ({} subs)...'.format(posts))
    
    #create subreddit class
    subreddit = r.subreddit(page)
    
    sl = [] #stores all comment data
    i=1
    
    #for each sub in the top subs, for each comment 
    #if comment is true comment then append to main list
    for sub in subreddit.top(time_filter = 'month',limit=posts): 
        sys.stdout.write('\r')
        sys.stdout.write('{}/{}'.format(i,posts))
        sys.stdout.flush()
        i+=1
        for comment in sub.comments.list():
            
            if isinstance(comment, MoreComments):
                continue
            sl.append(' '.join(comment.body.split()))
            
    print('\ndone!')
    return sl
    
    
def lang_mod(lang):
    '''loads in model of selected language...'''
    
    print('load lemma models')
    
    #will add support for other languages later
    #parser and ner not needed so disabled to save space
    if lang == "es":
        load_model = spacy.load('es_core_news_sm', disable = ['parser','ner'])
    else:
        raise ValueError('{} is not a supported language'.format(lang))
    
    print('done!')
    return load_model


def symbol_replace(sl):
    '''removes symbols from text'''
    
    #'' maps to '' removing spaces and punctuation maps to none
    sl = [item.translate(str.maketrans('', '', string.punctuation+'¿')) for item in sl]
    
    #removes '' from list
    sl = [item for item in sl if item != '']

    return sl    
        
    
def data_format(sl,load_model,wrds=4):
    ''''''
    
    print('format and lematise comments...')
    
    #convert input to single space
    sl = " ".join(sl)
    
    #lematise and clean up comments
    sl_mod = load_model(sl)
    sl_lem = [token.lemma_ for token in sl_mod]
    sl_lem = symbol_replace(sl_lem)
        
    #create freq dictionary of words
    sl_lem = Counter(sl_lem).most_common(wrds)
    
    print('done!')
    return sl_lem
    
        
def translate_item(wrd,phrs,lang):
    ''''''
    translator = Translator()
    wrd = translator.translate(wrd,src=lang,dest='english').text
    phrs = translator.translate(phrs,src=lang,dest='english').text

    return wrd,phrs

    
def examples(sl,sl_lem,load_model,lang,wrds=10):
    ''''''
    
    print('find comments containing words and translate...')
    
    #stores all flashcards
    rows_list = []
    
    #sort comments by length
    sl_in = sorted(sl, key=len)
    sl = []

    #convert comments to lemma form
    for comment in sl_in:
        comment = load_model(comment)
        sl.append(" ".join([token.lemma_ for token in comment]))
    
    #look for word in each comment, pick shortest comment
    for i in tqdm(range(wrds)):   
        id = list(' '+sl_lem[i][0]+' ' in x for x in sl).index(True)    
        wrdt,phrst = translate_item(sl_lem[i][0],sl_in[id],lang)
        
        dict1 = {
                "word {}".format(lang) : sl_lem[i][0],
                "phrase {}".format(lang) : sl_in[id],
                "word en" : wrdt,
                "phrase en" : phrst,
                "frequency" : sl_lem[i][1]
            } 
        rows_list.append(dict1)
        
    df = pd.DataFrame(rows_list)  

    #print all card contents    
    #print(df)     
    #print("\n----------------\n")   
    print('done!')
    return df

def main():
    ''''''
    
    #scrape data from reddit
    sl = scrape(page,posts)
    
    #load lemma model
    load_model = lang_mod(lang)
    
    #create common word lists
    sl_lem = data_format(sl, load_model, wrds)
    
    #create flashcards
    df = examples(sl,sl_lem,load_model,lang,wrds)
    
    print("\n\n\nend of script")
    
    return df

#language subreddits
#mexico, LatinoPeopleTwitter
#italy, memesITA
#turkey, TurkeyJerky

page = "mexico"   #subreddit
lang = "es"    #language of subreddit
posts = 10       #no of submissions
wrds = 200           # how many words to view

df = main()
