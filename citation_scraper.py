# -*- coding: utf-8 -*-

import scholarly
import csv
import time
import io

"""
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

	return str(journalShortName)+", "+str(volume)+"("+str(number)+"):"+str(pages)


def getPubInfo(title):
	global apiBlock

	if (not title.strip()):
		# given an empty string 
		return

	citation = ""
	print("\n--------------------------------------------------------\\\\\nsearching for title: "+title)
	search_query = scholarly.search_pubs_query(title)

	try:
		pubdata = next(search_query).fill().bib
	except:
		print("Unable to retrieve google scholar data :( skipping field...\n........................................................")
		apiBlock += 1
		if(apiBlock > 3):
			print("If this is happening a lot, you may have exceeded the number of requests to make to Google Scholar and they may be blocking your access.\n========================================================")
		return "-"

	print("FOUND:               "+pubdata['title'])
	
	# gets the edit distance, if over the threshold it is probably not a match
	s1 = str(pubdata['title'].strip(".").lower())
	s2 = str(title.strip().strip(".").lower())
	editDistance = levenshteinDistance(s1,s2)
	probabilityOfMatch = (len(title)-editDistance)/ float(len(title))

	# no match --
	if(probabilityOfMatch < matchThreshold):
		print("\!/ WARNING \!/ match below confidence levels\n    edit distance: "+str(editDistance)+"\n    match confidence [0-1]: "+str(probabilityOfMatch))
		
		pubdata = handleProblemKids(search_query, pubdata, probabilityOfMatch,title)
		print("\!/ Manually verify citation after processing is complete.")
		citation = formatCitation(pubdata)+" !!! VERIFY"
		print("--------------------------------------------------------//\n")
		return citation
	# match --
	else:
		print("Match verified with:\n    edit distance: "+str(editDistance)+"\n    match confidence [0-1]: "+str(probabilityOfMatch))
		citation = formatCitation(pubdata)

	print("    - CITATION: "+citation)
	print("--------------------------------------------------------//\n")

	return citation


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
	return mostLikely['data']

def matchProbability(pubdata, title):
	s1 = str(pubdata['title'].strip(".").lower())
	s2 = str(title.strip().strip(".").lower())
	editDistance = levenshteinDistance(s1,s2)
	return (len(title)-editDistance)/ float(len(title))

	# problemkids["results"];
	# print("\n==========================================================\nmismatched titles\nConfirm if title is a good enough match (y) or to move onto the next search result (n) or previous (b)")

	# print("INPUT TITLE:   "+problemKid["title"]+"\nSEARCH RESULT: "+problemKid["firstResult"]) 
	# response = raw_input("\{(y)es/(n)ext/(b)ack\}")
	# TODO: handle input

def parseTitles(titles):
	citationList = []
	for title in titles:
		if len(title.strip()) > 3:
			citation = getPubInfo(title)
			citationList.append({"title":title,"citation":citation})
	# TODO: handle problem kids
	# for problemKid in problemkids:
	writeCSV(citationList)

def writeCSV(rows):
	print("writing csv...")
	with open ("citationList.csv","wb") as csvfile:
		fieldNames = ["title","citation"]
		writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
		writer.writeheader()
		writer.writerows(rows)

def levenshteinDistance(s1, s2):
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
	filename = raw_input('enter file path: ')
	if(".csv" not in filename):
		print("Invalid filename. Remember to include the .csv extension!")
		return
   	with open(filename, "rb") as csvfile:
   		print("opening: "+filename+"...")
   		parseTitles(csvfile)
   	print("Complete! Always remember to have fun!")


main()