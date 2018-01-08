# citation_scraper

### Dependencies:
  * Python 2
  * Scholarly (Install by opening a terminal window and typing `pip install scholarly`)

### How to use:
  * Populate a single column .csv with a list of paper titles
  * Open the program in terminal by typing `python citation_scraper.py`
  * Enter the path to your .csv, for example, if your .csv is named 'titles' and is in the same folder as citation_scraper.py, write `titles.csv`
    * Update: you can also supply your .csv as a command line argument (i.e. `python citaiton_scraper.py titles.csv`)
  * A new file will be created in the directory containing `citation_scraper.py` called `<your_file_name>_citation_list.csv`
  * Just relax

### How does it work?
citation_scraper looks for the first google scholar result and then evaluates the degree to which it is different from the title you supplied. If citation_scraper is >60% confident that it's a match, then the script will accept the result and attempt to create a shortform citation. If not, it will iterate through the next 5 google scholar results and select the most similar sounding publication. Unconfident results will be flagged with a "!!!" in the output .csv.

The probability of a match is a value from 0-1 determined by `(length_of_title_you_supplied - editDistance(title_you_supplied,title_to_compare)) / length_of_title_you_supplied`.
The `editDistance()` is the number of operations it takes to transform one string to another (e.g. "Avocado -> Avocad" has an edit distance of 1). 
