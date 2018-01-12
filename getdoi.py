from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

import sys, os
import re

"""
TODO: 
1. sometimes dois are at the end of the document instead of the start.
We are doing a shallow search (the first 2 pages of a doc) to save time.
We will need to loop back and do a deep search if we can't find the doi

3. pipe to citation_scraper.py

4. possible misclassification if the doc lists a doi for another paper before this one.
    - dois in the form doi:xxx are preferred over doi.org/xxx

"""



doiList = []
examineList = []
maxPageDepth = 2

def batch_process_pdf(directory):
    """
    batch_process_pdf
    Iterates through all pdfs in directory and gets their doi

    directory :=  a string
    returns: nothing
    """
    numOfFiles = 0
    numOfDois = 0
    print("searching "+directory+"...")
    for filename in os.listdir(directory):
        if filename[-3:] == "pdf":
            numOfFiles += 1
            print("\n---\nfound document: "+filename)
            doi = convert_pdf_to_txt(directory+filename)
            if doi:
                numOfDois += 1
                doiList.append(doi)
            else:
                examineList.append(filename)
    completion = numOfDois/float(numOfFiles) * 100
    print("==================================\nComplete!\nFound dois for "+str(completion)+"% of files\nI could not find dois in the following files: ")
    for f in examineList:
        print("    - "+f)
    print("--dois: "+str(doiList))


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
        pageDepth += 1
        if pageDepth > maxPageDepth:
            break
        else:
            interpreter.process_page(page)


    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()

    prunedText = text.replace(" ","") # we remove whitespace because sometimes the dois l o o k  l i k e  t h i s 
    # search for a DOI in a form that looks like `doi : xxx/xxx.xxx.xx/x`
    doi = re.search('(doi|DOI).+/(\w+\.|\w+/|\w+)*', prunedText)
    if doi:
        print("    - "+doi.group(0))
        return doi.group(0)
    else:
        # search for a doi in the form `http://dx.doi.org/10.1080/14737140.2017.1381565`
        doi = re.search('doi.org/(\w+\.|\w+/|\w+)*', prunedText)
    if doi:
        print("    - "+doi.group(0))
        return doi.group(0)
    else:
        # todo: no pdf found, look through the rest of the pdf (maybe it's at the bottom)
        print("    :( no doi found")
        return False
    


# pdfTxt = convert_pdf_to_txt("test2.pdf")

batch_process_pdf("testpdfs/")