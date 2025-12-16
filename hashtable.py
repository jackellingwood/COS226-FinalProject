# Author: Jack Ellingwood
# Date: 12/19/2025
# Program: hashtable.py
# Project: COS226 Final Project

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

    def printInfo(self): # prints attributes
        print("Title: ", self.movieName)
        print("Genre: ", self.genre)
        print("Release Date: ", self.releaseDate)
        print("Director: ", self.director)
        print("Revenue: ", self.revenue)
        print("Rating: ", self.rating)
        print("Duration (Mins): ", self.durationMins)
        print("Production Company: ", self.productionCompany)
        print("Quote: ", self.quote)

    def info(self) -> list: # returns attributes as list
        return [
            self.movieName,
            self.genre,
            self.releaseDate,
            self.director,
            self.revenue,
            self.rating,
            self.durationMins,
            self.productionCompany,
            self.quote
        ]



class LinkedNode:
    def __init__(self, data: DataItem):
        self.data: DataItem = data
        self.next: LinkedNode = None
        self.last: LinkedNode = self


class HashTable():
    def __init__(self, length: int, indexBy: DataType = DataType.movieName):
        self.length = length
        self.indexBy = indexBy
        self.table: list[LinkedNode] = [None] * length
        self.collisions = 0

    # adds a value to our hashTable, hashes by indexBy given at __init__
    def store(self, value: DataItem):
        # to allow sorting by different data types
        if self.indexBy == DataType.movieName:
            key = self._hash(value.movieName)
        elif self.indexBy == DataType.quote:
            key = self._hash(value.quote)

        # linkedNode approach, create linkedNode if one doesn't exist in slot or append to end of list
        if self.table[key] == None:
            self.table[key] = LinkedNode(value)
        else:
            self.collisions += 1

            # hopefully this makes it so that we do not have to traverse an entire linked list to find our last value
            curNode = self.table[key]
            curNode.last.next = LinkedNode(value)
            curNode.last = curNode.last.next

    # return a dataItem, attempted to find in linked list at key
    def retrieve(self, strKey: str) -> DataItem:
        key = self._hash(strKey)
        curNode = self.table[key]
        while curNode:
            if self.indexBy == DataType.movieName:
                if curNode.data.movieName == strKey:
                    return curNode.data # found it!
            elif self.indexBy == DataType.quote:
                if curNode.data.quote == strKey:
                    return curNode.data # found it!
            curNode = curNode.next
            
        return None # met with a None, the item is not here
    
    # same as retrieve except for extra logic that removes a node from the linked list if found.
    def remove(self, strKey: str):
        key = self._hash(strKey)
        curNode = self.table[key]
        lastNode = curNode
        if not curNode:
            print("Hash Table Error: Tried to remove value from nonexistent list.")
            return None
        # base case, curNode is the data we want (must change head)
        if self.indexBy == DataType.movieName:
            if curNode.data.movieName == strKey:
                self.table[key] = curNode.next # found it!
        elif self.indexBy == DataType.quote:
            if curNode.data.quote == strKey:
                self.table[key] = curNode.next # found it!
        # recursive case
        while curNode:
            if self.indexBy == DataType.movieName:
                if curNode.data.movieName == strKey:
                    lastNode.next = curNode.next # found it!
            elif self.indexBy == DataType.quote:
                if curNode.data.quote == strKey:
                    lastNode.next = curNode.next # found it!
            lastNode = curNode
            curNode = curNode.next
            
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