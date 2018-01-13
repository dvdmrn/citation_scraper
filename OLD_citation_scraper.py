# -*- coding: utf-8 -*-

import scholarly
import csv
import io
import sys

"""
TODO: write confidence levels in .csv

Citation format:
volume(number):pagestart-pageend


"""

matchThreshold = 0.6
problemkids = []
apiBlock = 0

def getJournalAbbrev(journal):

    with open("res/pubmedNameMappings.csv") as mappingcsvfile:
        mappings = csv.DictReader(mappingcsvfile)
        for row in mappings:
            if journal.encode('utf-8') == row["Full Name"]:
                print("ISO abbreviation match found!\n    Abbreviating: "+journal+" ==> "+row["ISO abbrev"])
                return row["ISO abbrev"]
        print("Could not find ISO abbreviation. Using full name.")
        return journal

def getPubKeyValue(pubdata,keys,key):
    if(key in keys):
        return pubdata[key].strip()
    else:
        return ""

def formatCitation(pubdata):
    keys = pubdata.keys()
    volume = getPubKeyValue(pubdata, keys,'volume')
    number = getPubKeyValue(pubdata, keys,'number')
    journal = getPubKeyValue(pubdata, keys, 'journal')
    if not journal:
        journal = getPubKeyValue(pubdata, keys, 'booktitle')    
    pages = getPubKeyValue(pubdata, keys,'pages').replace("--","-")

    # print("data: ",volume, number, journal, pages)

    journalShortName = getJournalAbbrev(journal)
    if number:
        return str(journalShortName)+", "+str(volume)+"("+str(number)+"):"+str(pages)
    else:
        return str(journalShortName)+", "+str(volume)+":"+str(pages)

def getPubInfo(title):
    global apiBlock

    if (not title.strip()):
        # given an empty string 
        return

    citation = ""
    if "doi" in title.lower():
        print("\n--------------------------------------------------------\\\\\nsearching for doi: "+title)
        search_query = scholarly.search_pubs_query(title)

        try:
            pubdata = next(search_query).fill().bib
        except:
            print("Unable to retrieve google scholar data :( skipping field...\n........................................................")
            apiBlock += 1
            if(apiBlock > 3):
                print("If this is happening a lot, you may have exceeded the number of requests to make to Google Scholar and they may be blocking your access.\n========================================================")
            return {"citation":"N/A","confidence":"-"}

        print("FOUND:               "+pubdata['title'].encode('utf-8'))
        probabilityOfMatch = "-" # TODO: figure out a metric, maybe grab the name and contrast its DOI? Scholarly does not provide doi data for some reason...
        citation = formatCitation(pubdata)
        print("cite: ",citation)
        return {"citation":citation,"confidence":probabilityOfMatch}

    print("\n--------------------------------------------------------\\\\\nsearching for title: "+title)
    search_query = scholarly.search_pubs_query(title)

    try:
        pubdata = next(search_query).fill().bib
    except:
        print("Unable to retrieve google scholar data :( skipping field...\n........................................................")
        apiBlock += 1
        if(apiBlock > 3):
            print("If this is happening a lot, you may have exceeded the number of requests to make to Google Scholar and they may be blocking your access.\n========================================================")
        return {"citation":"N/A","confidence":"-"}

    print("FOUND:               "+pubdata['title'].encode('utf-8'))
    
    # gets the edit distance, if over the threshold it is probably not a match
    s1 = str(pubdata['title'].encode('utf-8').strip(".").lower())
    s2 = str(title.strip().strip(".").lower())
    editDistance = levenshteinDistance(s1,s2)
    probabilityOfMatch = max(0, ((len(title)-editDistance)/ float(len(title))) )

    # no match --
    if(probabilityOfMatch < matchThreshold):
        print("\!/ WARNING \!/ match below confidence levels\n    edit distance: "+str(editDistance)+"\n    match confidence [0-1]: "+str(probabilityOfMatch))
        
        pubdata = handleProblemKids(search_query, pubdata, probabilityOfMatch,title)
        print("\!/ Manually verify citation after processing is complete.")
        if pubdata["confidence"] < 0.6:
            citation = formatCitation(pubdata["citation"])+" !!! VERIFY"
        elif pubdata["confidence"] < 0.8:
            citation = formatCitation(pubdata["citation"])+" *"
        else:
            citation = formatCitation(pubdata["citation"])


        print("--------------------------------------------------------//\n")
        return {"citation":citation,"confidence":probabilityOfMatch}
    # match --
    else:
        print("Match verified with:\n    edit distance: "+str(editDistance)+"\n    match confidence [0-1]: "+str(probabilityOfMatch))
        if probabilityOfMatch<0.8:
                    citation = formatCitation(pubdata)+" *"
        else:           
            citation = formatCitation(pubdata)

    print("    - CITATION: "+citation)
    print("--------------------------------------------------------//\n")

    return {"citation":citation,"confidence":probabilityOfMatch}


def handleProblemKids(search_query,firstResultDict,firstProbability,title):
    queries = [{"data":firstResultDict,"p":firstProbability}]
    print("........................................................")
    print("evaluating the next 5 search results for maximum match...")
    pMatch = 0

    for i in xrange(5):
        try:
            pubdata = next(search_query).fill().bib
        except:
            break
        print("---")
        pMatch = matchProbability(pubdata,title)
        print("+ comparing: "+pubdata['title']+"\n    -p(match): "+str(pMatch))
        queries.append({"data":pubdata,"p":pMatch})
    
    mostLikely = max(queries,key=lambda x:x['p'])

    print("........................................................")
    print("The best I could find is: "+mostLikely['data']['title']+" with "+str(mostLikely['p'])+" confidence.")
    return {"citation":mostLikely['data'],"confidence":mostLikely['p']}

def matchProbability(pubdata, title):
    s1 = str(pubdata['title'].strip(".").lower())
    s2 = str(title.strip().strip(".").lower())
    editDistance = levenshteinDistance(s1,s2)
    return max(0, ((len(title)-editDistance)/ float(len(title))) )

    # problemkids["results"];
    # print("\n==========================================================\nmismatched titles\nConfirm if title is a good enough match (y) or to move onto the next search result (n) or previous (b)")

    # print("INPUT TITLE:   "+problemKid["title"]+"\nSEARCH RESULT: "+problemKid["firstResult"]) 
    # response = raw_input("\{(y)es/(n)ext/(b)ack\}")
    # TODO: handle input

def parseTitles(titles,name):
    citationList = []
    for title in titles:
        if len(title.strip()) > 3:
            citationDict = getPubInfo(title)
            citationList.append({"title":title,"citation":citationDict["citation"],"confidence":citationDict["confidence"]})
    # TODO: handle problem kids
    # for problemKid in problemkids:
    writeCSV(citationList,name)

def writeCSV(rows,name):
    print("writing csv...")
    with open (name+"_citation_list.csv","wb") as csvfile:
        fieldNames = ["title","citation","confidence"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        writer.writeheader()
        writer.writerows(rows)

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


def main():
    if(len(sys.argv)>1):
        filename = sys.argv[1]
    else:
        filename = raw_input('enter file path: ')
    if(".csv" not in filename):
        print("Invalid filename. Remember to include the .csv extension!")
        return
    with open(filename, "rb") as csvfile:
        print("opening: "+filename+"...")
        name = filename[:-4]
        parseTitles(csvfile,name)
    print("Complete! Always remember to have fun!")


main()