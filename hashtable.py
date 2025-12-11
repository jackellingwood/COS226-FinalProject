# Author: Jack Ellingwood
# Date: 11/18/25
# Assignment: COS226 HW 5: Hash Something Out 

from csv import reader
from enum import Enum
import sys
import time


class DataType(Enum): # datatype enum as comparison by string seemed to slow down the store function
    movieName = 0
    genre = 1
    releaseDate = 2
    director = 3
    revenue = 4
    rating = 5
    durationMins = 6
    productionCompany = 7
    quote = 8


class DataItem:
    def __init__(self, line):
        self.movieName = line[0]
        self.genre = line[1]
        self.releaseDate = line[2]
        self.director = line[3]
        self.revenue = line[4]
        self.rating = line[5]
        self.durationMins = line[6]
        self.productionCompany = line[7]
        self.quote = line[8]

    def printInfo(self):
        print("Title: ", self.movieName)
        print("Genre: ", self.genre)
        print("Release Date: ", self.releaseDate)
        print("Director: ", self.director)
        print("Revenue: ", self.revenue)
        print("Rating: ", self.rating)
        print("Duration (Mins): ", self.durationMins)
        print("Production Company: ", self.productionCompany)
        print("Quote: ", self.quote)



class LinkedNode:
    def __init__(self, data: DataItem):
        self.data: DataItem = data
        self.next: LinkedNode = None
        self.last: LinkedNode = self


class HashTable(): #TODO linked list instead, linear probing is a nightmare
    def __init__(self, length: int, indexBy: DataType = DataType.movieName):
        self.length = length
        self.indexBy = indexBy
        self.table: list[LinkedNode] = [None] * length
        self.collisions = 0

    # store value at its hash or next available spot in linear probed list, can hash by either quote or title depending on self.indexBy
    def store(self, value: DataItem):
        if self.indexBy == DataType.movieName:
            key = self._hash(value.movieName)
        elif self.indexBy == DataType.quote:
            key = self._hash(value.quote)

        if self.table[key] != None:
            self.collisions += 1
        
        originalKey = key
        while self.table[key]: # loops through filled slots
            key += 1
            if key == self.length: # wrap key around if necessary
                key = 0
            if key == originalKey: # traversed whole list
                return "No more space, cannot store new value."

        self.table[key] = value

    def retrieve(self, strKey: str) -> DataItem:
        key = self._hash(strKey)
        originalKey = key
        while self.table[key]: # loops through filled slots 
            if self.indexBy == DataType.movieName:
                if self.table[key].movieName == strKey:
                    return self.table[key] # found it!
            elif self.indexBy == DataType.quote:
                if self.table[key].quote == strKey:
                    return self.table[key] # found it!
            key += 1
            if key == self.length: # wrap key around if necessary
                key = 0
            if key == originalKey: # traversed whole list
                return None
            
        return None # met with a None, the item is not here

    def _hash(self, data): # djb2 hash, from http://www.cse.yorku.ca/~oz/hash.html
        key = 5381
        if len(data) > 500: # if data is extraordinarily long (cough cough bee movie) just do one unique operation on it
            return len(data) * 33 % self.length
        for c in data:
            key = key * 33 + ord(c)
            # key %= sys.maxsize # perhaps not necessary as python can handle numbers above sys.maxsize
        return key % self.length
    
    def get_empty_slots(self):
        return self.table.count(None)


# def main():
#     print()

#     titleTable = HashTable(15000, DataType.movieName)
#     start = end = 0
#     with open("MOCK_DATA.csv", encoding="UTF-8") as f:
#         start = time.time_ns()
#         for row in list(reader(f))[1:]: # skip initial variables line
#             titleTable.store(DataItem(row))
#         end = time.time_ns() - start

#     print("Optimization 5, Title")
#     print("Time taken (s):", end / 10**9)
#     print("Collisions:", titleTable.collisions)
#     print("Wasted slots:", titleTable.get_empty_slots(), "/", titleTable.length)

#     print()

#     quoteTable = HashTable(15000, DataType.quote)
#     start = end = 0
#     with open("MOCK_DATA.csv", encoding="UTF-8") as f:
#         start = time.time_ns()
#         for row in list(reader(f))[1:]: # skip initial variables line
#             quoteTable.store(DataItem(row))
#         end = time.time_ns() - start

#     print("Optimization 5, Quote")
#     print("Time taken (s):", end / 10**9)
#     print("Collisions:", quoteTable.collisions)
#     print("Wasted slots:", quoteTable.get_empty_slots(), "/", quoteTable.length)

#     print()    


# if __name__ == "__main__":
#     main()