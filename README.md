# Instructions
## Initialization
- Type name of .csv file to load (m.csv provided)
## Menu Commands: (Commands that can be used from the main menu)
- index 
- - Indexes a numerical column, must be used before a range search.
- - Followup arguments: [Which column?]
- search.
- - Searches a string column for all matches of a value.
- - Followup arguments: [Which column? Which value?]
- range
- - Searches for a range of values in an indexed column.
- - Followup arguments: [Which column? What mode? What bound(s)?]
- quit
- - Quits the program.

## Result Commands: (Commands that can be used after either a search or a range search, provided the search returned values)
- print
- - Prints the searched value(s) to the console.
- delete
- - Deletes the searched value(s) from working memory.
- save
- - Saves the searched value(s) to the provided file in .csv format
- - Followup arguments: [What should the new file name be?]

# Explanation of efficiency
- On database creation, there are 2 hash tables created for our searchable columns. This has an efficiency of less than O(n) time (average O(1) time) for each store operation assuming our hash table has some collsions but not all collisions.
- On index creation, we bulk load a B+ tree. First, we must use quick sort, which has average efficiency of O(nlogn) time. Tree splits don't add any complexity because they are O(1) time. Then, we load the sorted items into our tree, which is about O(n) time, because we must do it for every item, occasionally splitting the tree but not really enough to add extra complexity (again, (O(1) time).
- For an exact search, we search our hash table, which has an average efficiency of O(1) time but can be as bad as O(n) time for maximum collisions.
- For an range search, we search the bottom of our B+ tree for the range of values. This is O(logn) time to find our leftmost value (just searching through the tree for the lower bound) and then O(L) time for the length of the search, where L is the number of items between the lower and upper bounds.
- For our deletions, we have to search the hash tables and B+ tree and original dataList (reference of original data used in indexing) and do our removals there. Hash table deletion is 0(1) average time for each item deleted. B+ Tree deletion is O(logn) average time for each item deleted. dataList deletion is O(L) time worst case for each item deleted, where L is the length of our database.

# Example commands:
- index; rating; range; rating; 2bound; 8.0; 8.1; print; quit
- - (Indexes movies by rating, performs a range search for movies between 8.0 and 8.1 stars and prints them to console.)
- search; title; Bee Movie; delete; quit
- - (Searches for the Bee Movie and deletes any matches.)
- search; quote; Monitored encompassing frame; save; quote_entry.csv; quit
- - (Searches for the movie(s) with quote Monitored encompassing frame and saves them to quote_entry.csv.)

# Hash table design choices:
- My hash tables use djb2 as a hash function because it is simple and fairly optimal as far as reducing collisions.
- My hash tables use a linked list approach to allow for easy deletion, the only thing they need to do is search for the item and connect the nodes at either side of them.

# B+ Tree design choices:
- My B+ trees use a bulk load function for quick creation and optimal fill size (3/4 full).
- - This allows less operations to be done on buckets when removing single values or values on a range.
- A B+ Tree is created for each column so that it can be range searched.

# Data structure choices:
- I chose a dict to hold my hashTables and B+ Trees for easy storage and lookup by name.
- I chose a list to hold my original data because it is easy to loop through when indexing a column or creating a hash table.

# Searchable vs Non-Searchable
- The columns title, quote and director are exact searchable (by hash table) as those have the least duplicate values. I don't expect a user to want to know which exact movie had a revenue of exactly $3916723.03, but I bet someone would want to know information about the Bee Movie or which movie was directed by Addy Gawn or which movie has the quote "Robust 5th generation paradigm".
- The columns release date, box office revenue, rating, and duration are range searchable (by B+ tree) as they are numerical and thus have values that can be sorted.
- Production company and genre are not conducive for any kind of search because I would not find it interesting to know which company made a move (as a user) and genre would return too many results.

# Limitations
- Release Date is only searchable by year.
- As mentioned above, production company and genre are not searchable.
- Text interface kicks you back to the main menu most times whenever something invalid is entered.
- On my machine, program does not seem to properly shut down when play button is hit during operation, likely because of dangling inputs. To avoid potential errors, quit the program before restarting.