tree = [0]*1000

# function to build the segmenttree array
def buildTree(a):
    # insert leaf nodes in tree
    for i in range(n):
        tree[n + i] = a[i]

    # creating parent node by adding left and right child
    for i in range(n - 1, 0, -1):
        tree[i] = tree[2*i] + tree[2*i+1]

# function to update a node of the tree
def updateTree(index, value):
    # set value at position index
    tree[index + n] = value
    index=index+n

    # after updating the child node,update parents
    i = index

    while i > 1:
        #update parent by adding new left and right child
        tree[i//2] = tree[i] + tree[i^1]
        i =i//2

#function to find sum on different range
def queryTree(l, r):
    sum = 0

    #to find the sum in the range [l,r)
    l = l + n
    r = r + n

    while l < r:

        if ((l & 1)>0):
            sum = sum + tree[l]
            l =l+ 1

        if ((r & 1)>0):
            r = r- 1
            sum = sum + tree[r]

        l =l// 2
        r =r// 2

    return sum

if __name__ == "__main__":
    A = [1, 2, 3, 4, 5, 6, 7,8]
    n = len(A)
    buildTree(A)
    print(queryTree(1, 4))
    updateTree(2, 5)
    print(queryTree(1, 4))