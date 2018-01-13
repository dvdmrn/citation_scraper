import metapub
import confidence as c
import helpers

fetch = metapub.PubMedFetcher()

listOfCitations = []



def get_pmid(descriptor):
	"""
	gets the pmid of an article based off a descriptor
	descriptor: name or doi
	returns: pub med id, or False
	"""
	candidates = fetch.pmids_for_query(descriptor)

	if len(candidates) == 1:
		return candidates[0]
	if len(candidates) > 1:
		print "WARNING: multiple matches found, selecting first candidate"
		return candidates[0]
		# !!! determine most viable match
	else:
		# couldn't find anything
		print "SAD: no results found! (TT-TT)"
		return 0


def lookup_pmid(pmid):
	"""
	finds an article with a given pub med id --
	pmid = an int
	returns: a PubMedArticle
	"""
	try:
		article = fetch.article_by_pmid(pmid)
	except:
		print("    SAD: could not fetch pubmed data! (TT-TT)")
		return 0	
	return article

def create_citation(pm_article):
	"""
	Creates a NF friendly citation --
	pm_article: a PubMedArticle
	returns: a string
	"""
	title = pm_article.title
	volume = pm_article.volume
	issue = pm_article.issue
	journal = pm_article.journal
	pages = pm_article.pages
	missingData = 0
	if issue:
		issue = "("+issue+")"
	else:
		missingData += 1
		issue = ""
	if not journal:
		missingData += 1
		journal = pm_article.book
	if not journal:
		missingData += 1
		journal = "COULD_NOT_FIND_JOURNAL_SORRY_BUB"
	if not volume:
		missingData += 1
		volume = ""
	if not pages:
		missingData += 1
		pages = ""

	citation = journal+" "+volume+issue+":"+pages
	if missingData >= 2:
		citation =  citation+"!!! missing quite a bit of data"
		print "    WARNING: "+str(missingData)+" missing fields. Citation flagged."
	return citation


def process_pubs(dois):
	writeData = [] # list of Rows
	"""
	dict:
		file
		title
		citation
		confidence
	"""
	for pub in dois:
		print("\n---")
		title = ""
		citation = ""
		conf = 0
		
		if pub["doi"]:
			print "+ searching for doi: "+pub["doi"]+"; file: "+pub["file"]
			pmid = get_pmid(pub["doi"])
			if pmid:
				article = lookup_pmid(pmid)
				if article:
					citation = create_citation(article)
					title = article.title
					conf = c.confidence_metric(article,"pdfs_to_analyze/"+pub["file"])
					if conf < 0.6:
						print("\!/ WARNING \!/ pubmed data below critical confidence levels")
						citation = citation+"!!! VERIFY"
					print "writing citation: "+citation

		else:
			print("    No doi found for: "+pub["file"]+"; ignoring file")
		writeData.append({"file":pub["file"],"title":title,"citation":citation,"confidence":conf})

	return writeData




#  ==================================================
# id =  get_pmid("10.1039/c4fo00570h")
# article = lookup_pmid(id)


