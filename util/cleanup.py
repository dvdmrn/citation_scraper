import xml.etree.ElementTree as ET
import csv
# import time
"""
Need:

<NCBICatalogRecord>
	<JrXml>
		<Serial>
			*** <Title></title>
			*** <ISOAbbreviation></ISOAbbreviation>
"""




def constructMappings():
	mappings = [] # mappings is a List of Dictionaries like {"Full Name":"Journal of Avocado Science", "ISO abbrev":"Avo. Sci."}
	print("getting root...")
	root = ET.parse("nlmcatalog_result.xml").getroot()
	print("success! parsing tree...")
	for serial in root.iter("Serial"):
		print("FOUND SERIAL",serial)
		pair = {}
		for c in serial:
			if (c.tag=="Title"):
				name = c.text.encode('utf-8').strip()
				print("FOUND NAME: ",name)
				pair["Full Name"] = name
			if (c.tag=="ISOAbbreviation"):
				if c.text.strip():
					print("FOUND ABBREV: "+c.text.encode('utf-8').strip())
					pair["ISO abbrev"] = c.text.encode('utf-8').strip()
					mappings.append(pair)
					# print("------")
					# print("pair:",pair)
					# print("mappings: ",mappings)
					# time.sleep(1)

					pair = {}
					break
	return mappings

def writeCSV(rows):
	print("writing csv...")
	with open ("pubmedNameMappings.csv","wb") as csvfile:
		fieldNames = ["Full Name","ISO abbrev"]
		writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
		writer.writeheader()
		writer.writerows(rows)

def main():
	mappings = constructMappings()
	print("mappings: ",mappings)
	writeCSV(mappings)

main()