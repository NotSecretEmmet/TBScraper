# TB Scraper:

## General information:
Web scraper assignment.

## Notes:
I was able to finish the 'scraping' part of the assignment.
The code has been written that loops through each delivery area and extracts all the required information from the various restaurant pages.

Next steps would be to design the database to store the information.
For now I have attached a sample_data text file containing the variable in the Restaurant class.
Seeing that the second bonus question deals with location and time specific queries, a relational database
would need to be designed with the following linked tables:
Restaurant, Menu, Menu items, delivery areas (zipcodes?), and delivery times.

Currently, data on delivery areas, delivery times, menu catagories, and menu items are stored as JSON.
Seeing that seperate tables would be created, these would need to be parsed further. 


## Please answer the following questions:
*1. How much time did it cost?*

I think I spend about 3.5 hours on it so far. To completely finish it (database design and possibly adding multi-threading) I would need another few hours.

*2. How difficult was this assignment to achieve?*

The actual extraction of the required information was quite straightforward. Dealing with the 503 HTTP response, and working around that took some time. All in all, not too difficult, but to complete the assignment in a satisfactory way would be time-consuming

*3. What did you think of the assignment?*

Very interesting. Although writing the whole program (scraper and relational database) from scratch within the allotted  time is somewhat of a challenge. 

