import helpers
import getdoi
import confidence
import getpubmed
import csv

def writeCSV(name,rows):
    print("writing: "+name+" ...")
    with open (name,"wb") as csvfile:
        fieldNames = ["file","title","citation","confidence"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        writer.writeheader()
        writer.writerows(rows)

def main(directory):
	csvname = raw_input("What would you like to name your citation list? ")
	if ".csv" not in csvname:
		csvname += ".csv"
	print("\n[searching dois]======================================")
	print("searching in directory: "+directory)
	dois = getdoi.batch_process_pdfs(directory)
	print("\n[getting pubmed data]=================================")
	citationRows = getpubmed.process_pubs(dois)
	print("\n[writing data]========================================")
	print("cleaning data...")
	helpers.purgeUnicodeInListOfDicts(citationRows)
	writeCSV(csvname, citationRows)
	print("\n======================================================")
	print("Complete!")


main("pdfs_to_analyze/")