from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

import sys, os
import helpers

import getdoi

maxPageDepth = 1

def convert_pdf_to_txt(path):
    """
    convert_pdf_to_text()
    gets text representation of a pdf and searches for the doi

    path := a string
    returns: a string or FALSE it's python get over it 
    """
    print("+ parsing: "+path)
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    pageDepth = 0

    # look at the first maxPageDepth pages of a pdf
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        print("checking page")
        interpreter.process_page(page)


    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()

    return text



def levenshteinDistance(s1, s2):
    s1 = s1.lower()
    s2 = s2.lower()
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def matchProbability(foundPubContent, sourcePubContent):
    s1 = foundPubContent.lower()
    s2 = sourcePubContent.lower()
    editDistance = levenshteinDistance(s1,s2)
    return max(0, ((len(sourcePubContent)-editDistance)/ float(len(sourcePubContent))) )

def wordMatch(found,source):
    pdfWords = source.split(" ")
    scrapedWords = found.split(" ")
    matchedWords = 0
    foundStrBuffer = source

    # ideally, since everything in the abstract is contained in the pdf
    # scrape, we compare everything as the proportion to which the
    # pdf scrape matches the abstract
    for i in xrange(0,len(scrapedWords)-1):
        if scrapedWords[i] in pdfWords:
            matchedWords += 1
            pdfWords[i] = pdfWords[i]+"-M" # flag as matched so we don't look at duplicates
    # print "words found online: "+str(len(scrapedWords))
    # print "words in pdf: "+str(len(pdfWords))
    
    # print "number of matches: "+str(matchedWords)
    # print "proportion: "+str(matchedWords/float(len(scrapedWords)))
    confidence = matchedWords/float(len(scrapedWords))
    return confidence


def confidence_metric(article,pdfPath):
    abstract = article.abstract
    title = article.title
    doi = article.doi
    authors = article.authors
    try:
        onlineText = title+" "+abstract+" "+doi
    except:
        if title:
            print "\!/ WARNING: \!/ not enough information for string comparison, comparing title..."
            onlineText = title
        else:
            print "\!/ WARNING: \!/ not enough information for string comparison, flagging as 0 confidence."
            return 0
    for a in authors:
        onlineText+" "+a

    pdfText = getdoi.convert_pdf_to_txt(pdfPath,1)
    conf = wordMatch(helpers.checkUnicode(onlineText), pdfText)
    print "confidence: "+str(conf)
    return conf
