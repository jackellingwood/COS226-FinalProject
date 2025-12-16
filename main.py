# Author: Jack Ellingwood
# Date: 12/19/2025
# Program: main.py
# Project: COS226 Final Project

from csv import reader, writer
from typing import Callable
from hashtable import HashTable, DataItem, DataType
from btree import BTree, BucketNode, TreeItem, TreeVisualizer
from math import floor

def quick_sort(myList : list, sortFunc : Callable): # recursive, sorts myList by attribute defined by sortFunc
    if len(myList) <= 1:
        return myList
    
    pivot = myList[0] # simple pivot selection for now
    
    left = [item for item in myList[1:] if sortFunc(item) < sortFunc(pivot)]
    right = [item for item in myList[1:] if sortFunc(item) >= sortFunc(pivot)]
    
    return quick_sort(left, sortFunc) + [pivot] + quick_sort(right, sortFunc)

def index_column(col : list, sortBy) -> BTree: # creates a btree for a column, sorted by key (this is bulk load)
    tree = BTree(100) # debug: md 3, 10 data for testing tree stucture

    # provides the ability to sort by different attributes of DataItem
    if sortBy == "release_date":
        tree.sortKeyFunc = lambda x: int(x.releaseDate[-4:]) # sort by year (rip those in 10000 AD)
    elif sortBy == "box_office_revenue":
        tree.sortKeyFunc = lambda x: float(x.revenue[1:]) # minus dollar sign
    elif sortBy == "rating":
        tree.sortKeyFunc = lambda x: float(x.rating)
    elif sortBy == "duration_minutes":
        tree.sortKeyFunc = lambda x: int(x.durationMins)
    else:
        return -1
    col = quick_sort(col, tree.sortKeyFunc)
    # tree setup
    tree.root = BucketNode(tree.maxdegree)
    curBucket : BucketNode = tree.root
    # fill tree
    for item in col: # make sure every item is used
        if len(curBucket.keys) == floor(tree.maxdegree * (3/4)): # fill buckets to 3/4
            # if we are full, move on to next, creating parent if necessary
            if not curBucket.parent: # no parent, make parent but don't add key yet (next bucket gets that spot)
                curBucket.parent = BucketNode(tree.maxdegree)
                curBucket.parent.is_leaf = False
                curBucket.parent.links.append(curBucket)
                tree.root = curBucket.parent
                # link both ways
                curBucket.next = BucketNode(tree.maxdegree)
                curBucket.next.prev = curBucket
                # fix parent
                curBucket.next.parent = curBucket.parent
                curBucket = curBucket.next
            else: # we have a parent, add to parent and split if necessary
                curBucket.parent.keys.append(curBucket.keys[0].key)
                curBucket.parent.links.append(curBucket)
                # link both ways
                curBucket.next = BucketNode(tree.maxdegree)
                curBucket.next.prev = curBucket
                # fix parent
                curBucket.next.parent = curBucket.parent
                curBucket = curBucket.next
                if len(curBucket.parent.keys) >= tree.maxdegree: # split if too large
                    tree.split_internal_node(curBucket.parent)
        curBucket.add(TreeItem(float(tree.sortKeyFunc(item)), item)) # add item with proper key
    if curBucket.parent: # finished adding, ensure last bucket gets tacked on
        curBucket.parent.keys.append(curBucket.keys[0].key)
        curBucket.parent.links.append(curBucket)

    return tree

def main(): # takes care of the user interface, calling other function when necessary

    # load data file and handle errors
    dataFile = None
    while dataFile == None:
        try:
            path = input("File path of .csv file? : ")
            # path = "m.csv"
            with open(path, 'r', encoding='UTF-8') as f:
                dataFile = list(reader(f))
        except FileNotFoundError:
            print("File", path, "not found.")

    # set up hashTable dict and other data that can be pulled
    hashTables : dict[str, HashTable] = dict()
    hashTables["title"] = HashTable(20000, DataType.movieName)
    hashTables["quote"] = HashTable(20000, DataType.quote)
    indexableColumns = ["release_date", "box_office_revenue", "rating", "duration_minutes"]
    titleRow = dataFile[0]
    dataList : list[DataItem] = []
    for row in dataFile[1:]:
        dataList.append(DataItem(row))
        hashTables["title"].store(DataItem(row))
        hashTables["quote"].store(DataItem(row))
    indexedColumns : dict[str, BTree] = dict()

    # User Interface loop
    print("Dataset loaded, which option would you like to perform?")
    attempt = ""
    while not attempt == "quit":
        print() # to allow extra space in output
        print("Options: [index, search, range, debug, quit]")
        if (indexedColumns.keys()): # print indexed columns so that the user is aware
            print(f"Indexed Columns: [{', '.join(indexedColumns.keys())}]")
        attempt = input("> ")
        match attempt:

            case "index": # create a b tree for column
                print("Index which column?")
                print(f"[{', '.join(indexableColumns)}]")
                indexAttempt = input("> ")
                if indexAttempt not in indexableColumns:
                    print("Invalid column.")
                    continue
                else:
                    indexedColumn = index_column(dataList, indexAttempt)
                    if (indexedColumn == -1):
                        print(f"Column {indexAttempt} is not indexable.")
                        continue
                    else:
                        indexedColumns[indexAttempt] = indexedColumn

            case "search": # search hash table for single value
                print("Search which column?")
                print(f"[{', '.join(hashTables.keys())}]")
                searchAttempt = input("> ")
                if searchAttempt not in hashTables.keys():
                    print("Invalid column.")
                    continue
                else:
                    print(f"Find movie with what {searchAttempt}?")
                    itemQuery = input("> ")
                    searchedItem = hashTables[searchAttempt].retrieve(itemQuery)
                    if not searchedItem:
                        print(f"Could not find movie with {searchAttempt} \"{itemQuery}\".")
                        continue
                    print(f"Found movie with {searchAttempt} \"{itemQuery}\".")
                    print("What to do with the results?")
                    print("[print, delete, save]")
                    saveAttempt = input("> ")
                    match saveAttempt:
                        case "print": # print searched item
                            searchedItem.printInfo()
                        case "delete": # delete searched item
                            for column in indexedColumns.keys():
                                print(indexedColumns[column].remove(indexedColumns[column].sortKeyFunc(searchedItem.value)))
                            hashTables["title"].remove(searchedItem.value.movieName)
                            hashTables["quote"].remove(searchedItem.value.quote)
                        case "save": # save results to new csv (export)
                            print("Save to what file?")
                            filename = ""
                            data = None
                            while data == None:
                                try: # for validating filename
                                    filename = input("> ")
                                    with open(filename, 'x', newline='', encoding='UTF-8') as f:
                                        data = [titleRow, searchedItem.info()]
                                        filewriter = writer(f)
                                        # Write all rows at once
                                        filewriter.writerows(data)
                                except FileExistsError:
                                    print(f"{filename} already exists.")
                                except FileNotFoundError:
                                    print(f"Please enter a file name.")
                        case _: # don't recognize query, restart
                            print(f"I don't understand '{attempt}'.")
                            continue
            # TODO error when ranging and deleting but only sometimes, is probably tree generation issue
            case "range": # search a b tree over a single or double bound range
                if len(indexedColumns) == 0: # No columns indexed, back to beginning
                    print("No columns indexed, use \"index\".")
                    continue
                print("Range search which column?")
                print(f"[{', '.join(indexedColumns)}]")
                rangeAttempt = input("> ")
                if rangeAttempt not in indexedColumns: # Column requested wasn't indexed, start over
                    print("Column not indexed, use \"index\".")
                    continue
                else:
                    print("What mode? [<,2bound,>]")
                    mode = input("> ")
                    try:
                        match mode:
                            case "<":
                                print(f"Upper Bound?")
                                ub = float(input("> "))
                                lb = float('-inf')
                            case ">":
                                print(f"Lower Bound?")
                                lb = float(input("> "))
                                ub = float('inf')
                            case "2bound":
                                print(f"Lower Bound?")
                                lb = float(input("> "))
                                print(f"Upper Bound?")
                                ub = float(input("> "))
                            case _:
                                print("Mode not recognized.") # start over if mode isn't in the above
                                continue
                    except ValueError: # for if float() doesn't work (input is non-numeric)
                        print("Bound should be a number.")
                        continue
                    rangeResult = indexedColumns[rangeAttempt].range_search(lb, ub)
                    if len(rangeResult) == 0: # Nothing found
                        print(f"No items found between {rangeAttempt} ({lb} - {ub}).")
                        continue
                    print(f"Found {len(rangeResult)} items between {rangeAttempt} ({lb} - {ub}).")
                    print("What to do with the results?")
                    print("[print, delete, save]")
                    saveAttempt = input("> ")
                    match saveAttempt:
                        case "print": # print ranged items
                            for item in rangeResult:
                                item.value.printInfo()
                                print()
                        case "delete": # delete ranged items from all structures
                            for item in rangeResult:
                                for column in indexedColumns.keys():
                                    print(indexedColumns[column].remove(indexedColumns[column].sortKeyFunc(item.value)))
                                hashTables["title"].remove(item.value.movieName)
                                hashTables["quote"].remove(item.value.quote)
                        case "save": # save range query to csv
                            print("Save to what file?")
                            filename = ""
                            data = None
                            while data == None:
                                try: # for validating filename
                                    filename = input("> ")
                                    with open(filename, 'x', newline='', encoding='UTF-8') as f:
                                        data = [titleRow] # add title row
                                        data.extend([x.value.info() for x in rangeResult]) # and rest of data
                                        filewriter = writer(f)
                                        # write all rows at once
                                        filewriter.writerows(data)
                                except FileExistsError: # occurs if file exists
                                    print(f"{filename} already exists.")
                                except FileNotFoundError: # only occurs if user enters ""
                                    print(f"Please enter a file name.")
                        case _: # don't recognize query, restart
                            print(f"I don't understand '{attempt}'.")
                            continue

            case "debug":
                # Will not work if trees are large at all, very useless
                if len(indexedColumns) == 0:
                    print("No columns indexed.")
                    continue
                visualizer = TreeVisualizer()
                for tree in indexedColumns:
                    visualizer.add_to_stack(indexedColumns[tree])
                visualizer.visualize()

            case "quit": # attempt will be "quit" on next loop
                continue

            case _: # don't recognize query, restart
                print(f"I don't understand '{attempt}'.")


    # tree = index_column(dataList[:10], "rating")
    # print([x.value.movieName for x in tree.range_search(8.0, 8.0)])
    # visualizer = TreeVisualizer()
    # visualizer.add_to_stack(tree)
    # visualizer.visualize()


if __name__ == "__main__":
    main()