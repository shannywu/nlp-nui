#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import urllib, re, sqlite
from itertools import groupby, imap, product
from collections import defaultdict
import fileinput

def linggleit(query):
    url = 'http://linggle.com/query/{}'.format(urllib.quote(query, safe=''))
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()

def postProcess(start1, query):
    #print; print query; print
    res = linggleit(query)
    phrases = [ [  w.replace('<strong>','').replace('</strong>','')  for w in ngram['phrase'][start1:]] for ngram in res]
    phrases = [ [sqlite.search_lemma(ph[0].strip().lower())]+ ph[1:] for ph in phrases]
    phrases = [ ' '.join([x.strip() for x in ph]) for ph in phrases]
    counts = [ ngram['count_str'] for ngram in res]
    counts = [ int(x.replace(',','')) for x in counts]

    ngramCounts = zip(phrases, counts)
    ngramCounts.sort(key=lambda x: x[0])
    ngramCounts = [ (ngram, sum( [x[1] for x in ngramcounts ] )) \
                    for ngram, ngramcounts in groupby(ngramCounts, key=lambda x:x[0]) ]
    ngramCounts.sort(key=lambda x:x[1], reverse=True)

    resList = []
    for ngram, count in ngramCounts:
        #print '%s\t%s' % (ngram, count)
        resList.append((ngram, count))

    #dic.clear()
    return resList

def vnCollocation(headword):
    template1 = 'pron. v. ?prep. ?det. %s'
    start1 = 1
    query = template1 % headword
    return postProcess(start1, query)

def vanCollocation(headword):
    template1 = 'v. ?prep. ?det. adj. %s'
    start1 = 0
    query = template1 % headword
    return postProcess(start1, query)

def anCollocation(headword):
    template1 = 'det./prep. adj. %s'
    start1 = 1
    query = template1 % headword
    return postProcess(start1, query)

def vpCollocation(headword):
    template1 = 'pron. %s ?prep. ?n.'
    start1 = 1
    query = template1 % headword
    return postProcess(start1, query)

def synonym(headword):
    template1 = '~%s'
    start1 = 0
    query = template1 % headword
    return postProcess(start1, query)

# def allCollocations(headword):
#     vnCollocation(headword)
#     anCollocation(headword)
#     vanCollocation(headword)
#     vpCollocation(headword)

Nouns = ['words', 'word', 'nouns', 'noun', 'things', 'thing', 'something', 'example']
Verbs = ['verbs', 'verb']
Adjs = ['adjectives', 'ADJ', 'adj']
Preps = ['preposition', 'prepositions', 'prep']
wordBeforeTarget = ['describe', 'associate with', 'associates with', 'for', 'of', 'go with', 'use with', 'go for', 'use for', 'describe for', 'do for', 'do with', 'describes', 'goes with', 'uses with', 'goes for', 'uses for', 'describes for']
deleteWord = ['a', 'an', 'the', 'how', 'what', 'is', 'are', 'which', 'I', 'you', 'good', 'best', 'can', 'could', 'should', 'would', 'be', 'What', 'what', 'How', 'how', 'Which', 'which']
Synonym = ['same', 'syn', 'synonyms', 'synonym', 'alike', 'another']

def transQuery(question):
    que = [ token for token in re.findall("\w+", question)]
    [que.remove(i) for i in deleteWord if i in que]
    # print que
    speech = ['N' for i in Nouns if i in que]
    speech += ['V' for i in Verbs if i in que]
    speech += ['A' for i in Adjs if i in que]
    speech += ['P' for i in Preps if i in que]
    speech += ['S' for i in Synonym if i in que]
    speech += ['W' for i in wordBeforeTarget if ' '+i+' ' in ' '.join(que)]
    # print speech
    speech_n = list(set(speech))
    # print speech_n
    headword = [' '.join(que[(que.index(i.strip().split(' ')[-1])+1):]) for i in wordBeforeTarget if ' '+i+' ' in ' '.join(que)]
    if '' in headword: headword.remove('')
    # print headword

    finalRes = []

    if 'V' in speech_n:
        finalRes.append(['pron. v. ?prep. ?det. '+headword[0], 'v. ?prep. ?det. adj. '+headword[0]])
        finalRes.append(vnCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    elif 'S' in speech_n:
        finalRes.append(['~'+headword[0]])
        finalRes.append(synonym(headword[0]))
    elif 'P' in speech_n:
        finalRes.append(['pron. '+headword[0]+' ?prep. ?n.'])
        finalRes.append(vpCollocation(headword[0]))
    elif 'A' in speech_n:
        finalRes.append(['det./prep. adj. '+headword[0], 'v. ?prep. ?det. adj. '+headword[0]])
        finalRes.append(anCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    elif 'N' in speech_n:
        finalRes.append(['pron. '+headword[0]+' ?prep. ?n.', 'pron. v. ?prep. ?det. '+headword[0], 'v. ?prep. ?det. adj. '+headword[0], 'det./prep. adj. '+headword[0]])
        finalRes.append(vpCollocation(headword[0]))
        finalRes.append(vnCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
        finalRes.append(anCollocation(headword[0]))
    elif 'W' in speech_n:
        finalRes.append(['det./prep. adj. '+headword[0], 'v. ?prep. ?det. adj. '+headword[0]])
        finalRes.append(anCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    else:
        finalRes.append('I don\'t know what are you talking about')
    
    return finalRes

if __name__ == '__main__':
    while True:
        query = raw_input(">>(type 'EX' to exit)\n>>query: ")
        if query == 'EX': break
        else: 
            print transQuery(query)[0]
            print '------------------------------------------------'
            for q in transQuery(query)[1:]:
                for i in q:
                    print '{}\t{}'.format(i[0],i[1])
                print '========================================'
