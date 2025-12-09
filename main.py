from csv import reader
from typing import Callable
from hashtable import HashTable, DataItem
from btree import BTree, TreeVisualizer, BucketNode, TreeItem
from math import floor

def bubble_sort(myList : list, sortBy : Callable): # tried this and forgot the performance is abysmal
    n = len(myList)
    # Traverse through all array elements
    for i in range(n):
        for j in range(0, n - i - 1):
            if sortBy(myList[j]) > sortBy(myList[j + 1]):
                myList[j], myList[j + 1] = myList[j + 1], myList[j]

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

    bubble_sort(col, sortKeyFunc)
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
    
    titleRow = dataFile[0]
    dataList : list[DataItem] = []
    for row in dataFile[1:]:
        dataList.append(DataItem(row))

    indexedColumns = dict()

    # print("Dataset loaded, which option would you like to perform?")
    # attempt = ""
    # while not attempt == "quit":
    #     print("Options: [index, search, range, quit]")
    #     if (indexedColumns.keys()):
    #         print(f"Indexed Columns: {', '.join(indexedColumns.keys())}")
    #     attempt = input("> ")
    #     match attempt:
    #         case "index":
    #             print("Index which column?")
    #             print(f"[{', '.join(titleRow)}]")
    #             indexAttempt = input("> ")
    #             if indexAttempt not in titleRow:
    #                 print("Invalid column.")
    #                 continue
    #             else:
    #                 indexedColumn = index_column(dataList, indexAttempt)
    #                 if (indexedColumn == -1):
    #                     print(f"Column {indexAttempt} is not indexible.")
    #                     continue
    #                 else:
    #                     indexedColumns[indexAttempt] = indexedColumn
    #         case "search":
    #             print("Search not implemented.")
    #         case "range":
    #             print("Range not implemented.")
    #         case "quit":
    #             continue
    #         case _:
    #             print(f"I don't understand {attempt}.")


    tree = index_column(dataList[:10], "rating")
    print(tree.search(8.0))
    visualizer = TreeVisualizer()
    visualizer.add_to_stack(tree)
    visualizer.visualize()


if __name__ == "__main__":
    main()