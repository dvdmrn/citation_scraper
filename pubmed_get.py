import metapub
import confidence as c

fetch = metapub.PubMedFetcher()

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
		return 0
		# !!! determine most viable match
	else:
		# couldn't find anything
		return False


def lookup_pmid(pmid):
	"""
	finds an article with a given pub med id --
	pmid = an int
	returns: a PubMedArticle
	"""
	try:
		article = fetch.article_by_pmid(pmid)
	except:
		print "pubmed id not valid! :("
		return False	
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

	citation = journal+" "+volume+"("+issue+")"+":"+pages
	return citation

# def search_doi(doi):
# 	"""
# 	Gets an article based off doi
# 	doi :  a string
# 	returns: a PubMedArticle
# 	"""
# 	article = fetch.pmids_from_citation(doi)
# 	return article

# print "hello"
id =  get_pmid("10.1039/c4fo00570h")
article = lookup_pmid(id)

abstract = article.abstract
title = article.title
doi = article.doi
authors = article.authors
print(str(authors))
onlineText = title+" "+abstract+" "+doi


pdfText = c.convert_pdf_to_txt("12_pg01.pdf")

print("typeinfo:",type(onlineText),type(pdfText))
print (c.wordMatch(onlineText.encode('utf-8'), pdfText))

