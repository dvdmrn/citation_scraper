from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

from pdfminer.pdfpage import PDFPage
from pdfminer.layout import *


"""
	Maybe something for later
	Takes the first 200 or so characters from the first
	decently sized LTTTextBoxHorizontal (representation of a pdf textbox)
	...maybe then serach for it?
	Problems: author names, titles, abstracts sometimes in the same rect...

"""

document = open('34_pg01.pdf','rb')

# Create resource manager
rsrcmgr = PDFResourceManager()
# Set parameters for analysis.
laparams = LAParams()
# Create a PDF page aggregator object.
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
for page in PDFPage.get_pages(document):
	interpreter.process_page(page)
	# receive the LTPage object for the page.
	layout = device.get_result()
	for element in layout:
		if isinstance(element, LTTextBoxHorizontal):
			if len(element.get_text()) > 200:
				print element.get_text().encode('utf-8')[0:200]
				break
