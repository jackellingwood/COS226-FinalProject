# Author: Jack Ellingwood
# Date: 11/4
# Program: btree.py
# Assignment: Final Project

from btree_visualizer import Tree, TreeVisualizer, Bucket, TreeItem

treevisualizer = TreeVisualizer()

class BucketNode(Bucket):

    # add TreeItem to bucket in proper space
    def add(self, item: TreeItem, leftLink = None):
        target = 0
        if self.is_leaf:
            for data in self.keys:
                if item.key < data.key:
                    break
                target += 1
            self.keys.insert(target, item)
        else:
            for key in self.keys:
                if item < key:
                    break
                target += 1
            self.keys.insert(target, item)
            self.links.insert(target, leftLink)
        return len(self.keys)

    # remove TreeItem from bucket according to key, return -1 if not found, TreeItem if 
    def remove(self, key):
        # bucket remove.
        # Try to the TreeItem in .keys that matches "key"
        # pop it from the list if it exists. Return the popped TreeItem.
        # if it doesn't, return -1
        for i, item in enumerate(self.keys):
            if item.key == key:
                return self.keys.pop(i)
        return -1

class BTree(Tree):
    
    # searches the tree for a valid bucket to add a TreeItem to, may cause a leaf split
    def add(self, key, value):
        data = TreeItem(key, value)
        if not self.root:
            self.root = BucketNode(self.maxdegree)
            self.root.keys.append(data)
            return
        curBucket = self.root
        while not curBucket.is_leaf:
            targetLink = 0
            for key in curBucket.keys:
                if data.key < key:
                    break
                targetLink += 1
            curBucket = curBucket.links[targetLink]
        size = curBucket.add(data)
        if size >= self.maxdegree:
            self.split_leaf_node(curBucket)

    # splits a full leaf node into two leaf nodes and an internal parent 
    def split_leaf_node(self, node: BucketNode):
        newLeft = BucketNode(self.maxdegree)
        mI = self.maxdegree // 2
        newLeft.keys = node.keys[:mI]
        node.keys = node.keys[mI:]
        # fix next/prev connections
        newLeft.next = node
        newLeft.prev = node.prev
        if newLeft.prev:
            newLeft.prev.next = newLeft
        node.prev = newLeft
        # place split value in parent
        if node.parent == None:
            self.root = BucketNode(self.maxdegree)
            self.root.is_leaf = False
            node.parent = self.root
            newLeft.parent = self.root
            self.root.keys = [node.keys[0].key]
            self.root.links = [newLeft, node]
        else:
            newLeft.parent = node.parent
            split = node.parent.add(node.keys[0].key, newLeft)
            if split >= self.maxdegree:
                self.split_internal_node(node.parent)

    # splits a full internal node into two child internal nodes and an internal parent
    def split_internal_node(self, node: BucketNode):
        newLeft = BucketNode(self.maxdegree)
        newLeft.is_leaf = False
        mI = self.maxdegree // 2
        newLeft.keys = node.keys[:mI]
        middleBucket = node.keys[mI]
        node.keys = node.keys[mI + 1:]
        #copy links
        newLeft.links = node.links[:mI + 1]
        node.links = node.links[mI + 1:]
        if not node.parent:
            self.root = BucketNode(self.maxdegree)
            self.root.is_leaf = False
            node.parent = self.root
            self.root.links = [node]
                #fix parents
        for link in newLeft.links:
            link.parent = newLeft
        split = node.parent.add(middleBucket, newLeft)
        newLeft.parent = node.parent
        if split >= self.maxdegree:
            self.split_internal_node(node.parent)

    # searches for and removes a TreeItem with key, 
    #   may fix keys of parent nodes or the bucket it is removed from if necessary
    def remove(self, key):
        if not self.root:
            return "Literally nothing you could remove."
        
        curBucket = self.root

        memory = None # bucket where we find the key early
        memoryIndex = 0 # which index in the memory bucket

        # find the correct bucket based on the key
            # difference compared to the "add",
            # if you find the key you're looking for early
            # store the curBucket in memory, and target in memory_index

        while not curBucket.is_leaf:
            targetLink = 0
            for bucketKey in curBucket.keys:
                if bucketKey == key:
                    memory = curBucket
                    memoryIndex = targetLink
                if bucketKey > key:
                    break
                targetLink += 1
            curBucket = curBucket.links[targetLink]
        
        # If we're close to the bottom, it doesn't matter
        #if memory == curBucket.parent: commenting this out, we'll fix elsewhere
        #    memory = None


        if memory != None:
            # fix the memory node.
            nextKey = self.find_next_key(curBucket) #new line
            if nextKey != None: # new check
                memory.keys[memoryIndex] = nextKey
    
        # curBucket is the correct leaf where "key" *might* exist.
        remove = curBucket.remove(key)

        # remove will have -1 or an entire TreeItem.
        if remove != -1:
            # check if bucket is too small
            if (len(curBucket.keys) < (self.maxdegree-1)//2):
                self.fix_leaf_bucket(curBucket) # fix the leaf bucket
            return f"Found {key} and removed {remove.value}"
        else: 
            # didn't find it, let the outside world know
            return f"Did not find {key}"

    # either steal from left/right or merge left/right
    def fix_leaf_bucket(self, node: BucketNode):
        # if we're here, the node is too small

        if node == self.root: # root can't be too small
            return

        # grab the sibling info and where we are
        leftNode, rightNode = self.get_siblings(node)

        # check if we can... 
        # (make steal and merge seperate functions)
        # Have leaf_steal, leaf_merge
        # steal from left
        if self.is_valid_steal(leftNode):
            self.steal_leaf(node, "left")
        # steal from right
        elif self.is_valid_steal(rightNode):
            self.steal_leaf(node, "right")
        # merge to the left
        elif leftNode != None:
            self.merge_leaf(leftNode, node)
        # merge to the right
        else:
            self.merge_leaf(node, rightNode)

    # either steal from left/right or merge left/right
    def fix_internal_bucket(self, node):
        # if you reach this point, node is an internal bucket,
        #    and is too small

        if node == self.root: # root can't be too small
            return
        
        leftSib, rightSib = self.get_siblings(node)
        # check if...
        # you can steal left
        if self.is_valid_steal(leftSib):
            self.steal_internal(node, "left")
        # you can steal right
        elif self.is_valid_steal(rightSib):
            self.steal_internal(node, "right")
        # you can merge left
        elif leftSib != None:
            self.merge_internal(leftSib, node)
        # you can merge right
        else:
            self.merge_internal(node, rightSib)

    # steal key from left or right bucket
    def steal_leaf(self, node: BucketNode, direction): #does not check if right or left is valid steal
        if direction == "right":
            node.keys.append(node.next.keys.pop(0))
            #fix parent key to new head
            target = 0
            for link in node.parent.links:
                if link == node:
                    break
                target += 1
            node.parent.keys[target] = node.next.keys[0].key
        else:
            node.keys.insert(0, node.prev.keys.pop(-1))
            #fix parent key to new head
            target = 0
            for link in node.parent.links:
                if link == node:
                    break
                target += 1
            node.parent.keys[target - 1] = node.keys[0].key

    # merge rightNode into leftNode, pulling down a key from parent, then check if we've made parent too small
    def merge_leaf(self, leftNode: BucketNode, rightNode: BucketNode):
        # take everything in the rightNode, and stuff it into the left node

        leftNode.keys.extend(rightNode.keys)
        target = 0
        for link in leftNode.parent.links:
            if link == leftNode:
                break
            target += 1
        # now target is the index where leftNode is.
        leftNode.parent.keys.pop(target)
        leftNode.parent.links.pop(target+1)
        leftNode.next = rightNode.next  # fix the next/prev connections
        if leftNode.next:
            leftNode.next.prev = leftNode
        
        # check if bucket is too small
        if (len(leftNode.parent.keys) < (self.maxdegree-1)//2):
            self.fix_internal_bucket(leftNode.parent) # fix the leaf bucket

    # pull a node from left/right bucket and update parent accordingly
    def steal_internal(self, node: BucketNode, direction):
        target = 0
        for link in node.parent.links:
            if link == node:
                break
            target += 1
        if direction == "left":  # stealing from the left
            # now target = link index to node
            leftNode = node.parent.links[target - 1] # left sibling, that we steal from
            # the parent key at target-1, insert to start of keys in node
            node.keys.insert(0, node.parent.keys[target - 1])
            # the last link in leftNode, pop it, and insert at start of links in node
            node.links.insert(0, leftNode.links.pop())
            # leftNode last key, pop it, place in the parent key at target-1
            node.parent.keys[target - 1] = leftNode.keys.pop()
        else:       # stealing from the right
            # same as above but....
            # you're pulling from the start of the right node,
            #  and adding to the end of "node"
            rightNode = node.parent.links[target + 1]
            # the parent key at target+1, append to end of keys in node
            node.keys.append(node.parent.keys[target])
            # the first link in rightNode, pop it, and append at end of links in node
            node.links.append(rightNode.links.pop(0))
            # rightNode first key, pop it, place in the parent key at target+1
            node.parent.keys[target] = rightNode.keys.pop(0)

    # manage parent's association with rightNode then push all of rightNode's contents into leftNode
    def merge_internal(self, leftNode: BucketNode, rightNode: BucketNode):
        parent = rightNode.parent
        # take parent key between left and right, pop it, 
        #   and append to leftNode.keys
        parentKeyIndex = parent.links.index(leftNode)
        leftNode.keys.append(parent.keys.pop(parentKeyIndex))
        # pop the *link* in the parent.links that's pointing to rightNode
        parent.links.pop(parentKeyIndex + 1)
        # cycle through all links in rightNode, set their parent to leftNode
        for link in rightNode.links:
            link.parent = leftNode
        # stuff all keys in rightNode into leftNode
        leftNode.keys.extend(rightNode.keys)
        # stuff all links in rightNode into leftNode
        leftNode.links.extend(rightNode.links)

        # if parent.keys length is now 0 and it's the root, set root to leftNode
        if len(parent.keys) == 0 and parent == self.root:
            self.root = leftNode

        # check if parent too small (but not zero), 
        # if it is, another internal_fix
        elif len(parent.keys) < (self.maxdegree - 1) // 2:
            self.fix_internal_bucket(parent)

    # returns buckets to the left and right of node according to parent
    def get_siblings(self, node: BucketNode):
        # find out a valid left and right sibling.
        # also find out where "node" is in the parent.links
        leftNode = None
        rightNode = None

        # find out where we are
        target = 0
        for i in node.parent.links:
            if i == node:
                break
            target += 1
        
        if target > 0: # if it's possible to have a left sibling
            leftNode = node.parent.links[target-1]
        if target < len(node.parent.links)-1:
            # if it's possible to have a right sibling
            rightNode = node.parent.links[target+1]
        
        # return all info
        return leftNode, rightNode

    # returns next key in bucket or in the next bucket over
    def find_next_key(self, node: BucketNode): # only runs on leaf buckets
        # find the next key, after key
        # key is currently node.keys[0].key        

        if len(node.keys) > 1: # bucket is large enough, the next key is here
            return node.keys[1].key # return next key
        elif node.next != None: # check if there's a bucket to the right
            return node.next.keys[0].key
        else:
            return None

    # searches the tree for a value, returns a message based on its success.
    def search(self, key):
        if not self.root:
            print("Search: Tree empty.")
            return
        curBucket = self.root
        depth = 0
        while not curBucket.is_leaf:
            targetLink = 0
            for bucketKey in curBucket.keys:
                if key < bucketKey:
                    break
                targetLink += 1
            curBucket = curBucket.links[targetLink]
            depth += 1
        for bucketItem in curBucket.keys:
            if key == bucketItem.key:
                return bucketItem
        print(f"Search: {key} not found.")
        return
    
    def range_search(self, lower : float, upper : float):
        out = []
        curBucket = self.root
        while not curBucket.is_leaf: # search down the tree for the right bucket
            targetLink = 0
            for bucketKey in curBucket.keys:
                if lower < bucketKey:
                    break
                if lower == bucketKey: # for case with duplicates, check the bucket after lower bucket
                    targetLink += 1
                    break
                targetLink += 1
            curBucket = curBucket.links[targetLink]
        print(curBucket)
        targetItemIndex = 0
        for bucketItem in curBucket.keys: #search bucket for correct starting point
            if lower <= bucketItem.key:
                break
            targetItemIndex += 1
        if targetItemIndex >= len(curBucket.keys): # kind of like a do while here, check that if the for loop search has placed us in the next bucket
            if not curBucket.next:
                return []
            curBucket = curBucket.next
            targetItemIndex = 0
        print(curBucket)
        while curBucket.keys[targetItemIndex].key <= upper: # iterate through leaves until we have a full list.
            print(curBucket.keys[targetItemIndex].key)
            out.append(curBucket.keys[targetItemIndex])
            targetItemIndex += 1
            if targetItemIndex >= len(curBucket.keys):
                if not curBucket.next:
                    break
                curBucket = curBucket.next
                targetItemIndex = 0

        return out


        
        

    # returns whether a node can be stolen from (exists and has enough keys)
    def is_valid_steal(self, node):
        if node == None:
            return False
        if (len(node.keys) <= (self.maxdegree-1)//2):
            return False
        return True

# def main():
#     print("B+ Tree Example")

#     maxdegree = 5

#     # create a tree with a max degree of 5
#     tree = BTree(maxdegree)

#     # run all add calls according to file
#     with open("data.txt", "r") as f:
#         for i, dataToAdd in enumerate(f.readlines()):
#             dataToAdd = dataToAdd.split(',')
#             tree.add(int(dataToAdd[0]), dataToAdd[1].strip())
#             if (i + 1) % 10 == 0: 
#                 treevisualizer.add_to_stack(tree)

#     print(tree.search(75))
#     print(tree.search(99))

#     with open("remove_data.txt", "r") as f:
#         for i, dataToRemove in enumerate(f.readlines()):
#             print(tree.remove(int(dataToRemove)))
#             if (i + 1) % 6 == 0: 
#                 treevisualizer.add_to_stack(tree)

#     treevisualizer.visualize()

# if __name__ == "__main__":
#     main()