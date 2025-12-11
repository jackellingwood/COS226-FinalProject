from csv import reader
from typing import Callable
from hashtable import HashTable, DataItem, DataType
from btree import BTree, BucketNode, TreeItem # TreeVisualizer
from math import floor

def quick_sort(myList : list, sortFunc : Callable):
    if len(myList) <= 1:
        return myList
    
    pivot = myList[0] # simple pivot selection for now
    
    left = [item for item in myList[1:] if sortFunc(item) < sortFunc(pivot)]
    right = [item for item in myList[1:] if sortFunc(item) >= sortFunc(pivot)]
    
    return quick_sort(left, sortFunc) + [pivot] + quick_sort(right, sortFunc)

def index_column(col : list, sortBy) -> BTree:
    # troy's idea: make internal bucket add function that just doesn't search through the list
    # TODO keeps duplicate keys in internal nodes, what to do?

    sortKeyFunc = print # just wanted to set it to something
    # provides the ability to sort by different attributes of DataItem
    if sortBy == "release_date":
        sortKeyFunc = lambda x: int(x.releaseDate[-4:]) # sort by year (rip those in 10000 AD)
    elif sortBy == "box_office_revenue":
        sortKeyFunc = lambda x: float(x.revenue[1:]) # minus dollar sign
    elif sortBy == "rating":
        sortKeyFunc = lambda x: float(x.rating)
    elif sortBy == "duration_minutes":
        sortKeyFunc = lambda x: int(x.durationMins)
    else:
        return -1
    col = quick_sort(col, sortKeyFunc)
    tree = BTree(3) # md 3, 10 data for testing tree stucture
    tree.root = BucketNode(tree.maxdegree)
    curBucket : BucketNode = tree.root
    for item in col: # make sure every item is used
        if len(curBucket.keys) == floor(tree.maxdegree * (3/4)): # fill buckets to 3/4
            if not curBucket.parent: # no parent, don't add key yet (next bucket gets that spot)
                curBucket.parent = BucketNode(tree.maxdegree)
                curBucket.parent.is_leaf = False
                curBucket.parent.links.append(curBucket)
                tree.root = curBucket.parent
                curBucket.next = BucketNode(tree.maxdegree)
                curBucket.next.parent = curBucket.parent
                curBucket = curBucket.next
            else:
                curBucket.parent.keys.append(curBucket.keys[0].key)
                curBucket.parent.links.append(curBucket)
                curBucket.next = BucketNode(tree.maxdegree)
                curBucket.next.parent = curBucket.parent
                curBucket = curBucket.next
                if len(curBucket.parent.keys) >= tree.maxdegree:
                    tree.split_internal_node(curBucket.parent)
        curBucket.add(TreeItem(float(sortKeyFunc(item)), item))
    if curBucket.parent: # finished adding, ensure last bucket gets tacked on
        curBucket.parent.keys.append(curBucket.keys[0].key)
        curBucket.parent.links.append(curBucket)

    return tree

def main():
    dataFile = None
    while dataFile == None:
        try:
            # path = input("File path of .csv file? : ")
            path = "m.csv"
            with open(path, 'r', encoding='UTF-8') as f:
                dataFile = list(reader(f))
        except FileNotFoundError:
            print("File", path, "not found.")

    
    hashTables : dict[str, HashTable] = dict()
    hashTables["title"] = HashTable(20000, DataType.movieName)
    hashTables["quote"] = HashTable(20000, DataType.quote)
    indexibleColumns = ["release_date", "box_office_revenue", "rating", "duration_minutes"]
    
    titleRow = dataFile[0]
    dataList : list[DataItem] = []
    for row in dataFile[1:]:
        dataList.append(DataItem(row))
        hashTables["title"].store(DataItem(row))
        hashTables["quote"].store(DataItem(row))

    indexedColumns = dict()

    print("Dataset loaded, which option would you like to perform?")
    attempt = ""
    while not attempt == "quit":
        print("Options: [index, search, range, quit]")
        if (indexedColumns.keys()):
            print(f"Indexed Columns: {', '.join(indexedColumns.keys())}")
        attempt = input("> ")
        match attempt:
            case "index":
                print("Index which column?")
                print(f"[{', '.join(titleRow)}]")
                indexAttempt = input("> ")
                if indexAttempt not in indexibleColumns:
                    print("Invalid column.")
                    continue
                else:
                    indexedColumn = index_column(dataList, indexAttempt)
                    if (indexedColumn == -1):
                        print(f"Column {indexAttempt} is not indexible.")
                        continue
                    else:
                        indexedColumns[indexAttempt] = indexedColumn
            case "search":
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
                        print(f"Could not find movie with {searchAttempt} {itemQuery}.")
                        continue
                    searchedItem.printInfo()
            case "range":
                print("Range not implemented.")
            case "quit":
                continue
            case _:
                print(f"I don't understand '{attempt}'.")


    # tree = index_column(dataList[:10], "rating")
    # print(tree.range_search(8.0, 8.0))
    # visualizer = TreeVisualizer()
    # visualizer.add_to_stack(tree)
    # visualizer.visualize()


if __name__ == "__main__":
    main()