# Automatized paper allocation for TPC meetings


### Basic requirements

The code needs Python 3.7+ to run.



### Obtain reviewer assignments

Go to HotCRP, search for the papers you want to consider, go at the bottom of the page, select all papers, 
click on Download, select "PC Assignments" and click on Go. 

Also supply a CSV file with PC time preferences. It has to have:
- A column with reviewers' ID (emails, names)
- A column with reviewers' time zones (the list of time zones is currently hard coded)
- A column for each day of TPC meeting with reviewers' availability on the day in form of ([not] start_hour:start_min-end_hour:end_min)+. It could also be empty for the default period, and "not" for blocking out an entire day

Put all files in the same directory where the code is and run. The code will print various assignments. 



