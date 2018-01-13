import helpers
import getdoi
import confidence
import getpubmed

def main():
	print("searching in directory: pdfs_to_analyze")
	getdoi.batch_process_pdfs("pdfs_to_analyze/")


main()