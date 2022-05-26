import csv
import math
import os
import time

bPlusTrees = {}
record_len = 6

# Node creation
class Node:
    def __init__(self, order):
        self.order = order
        self.values = []
        self.keys = []
        self.nextKey = None
        self.parent = None
        self.check_leaf = False

    # Insert at the leaf
    def insert_at_leaf(self, leaf, value, key):
        if (self.values):
            temp1 = self.values
            for i in range(len(temp1)):
                if (value == temp1[i]):
                    self.keys[i].append(key)
                    break
                elif (value < temp1[i]):
                    self.values = self.values[:i] + [value] + self.values[i:]
                    self.keys = self.keys[:i] + [[key]] + self.keys[i:]
                    break
                elif (i + 1 == len(temp1)):
                    self.values.append(value)
                    self.keys.append([key])
                    break
        else:
            self.values = [value]
            self.keys = [[key]]


# B plus tree
class BPlusTree:
    def __init__(self, order):
        self.root = Node(order)
        self.root.check_leaf = True

    # Insert operation
    def insert(self, value, key):
        value = str(value)
        old_node = self.search(value)
        old_node.insert_at_leaf(old_node, value, key)

        if (len(old_node.values) == old_node.order):
            node1 = Node(old_node.order)
            node1.check_leaf = True
            node1.parent = old_node.parent
            mid = int(math.ceil(old_node.order / 2)) - 1
            node1.values = old_node.values[mid + 1:]
            node1.keys = old_node.keys[mid + 1:]
            node1.nextKey = old_node.nextKey
            old_node.values = old_node.values[:mid + 1]
            old_node.keys = old_node.keys[:mid + 1]
            old_node.nextKey = node1
            self.insert_in_parent(old_node, node1.values[0], node1)

    # Search operation for different operations
    def search(self, value):
        current_node = self.root
        while(current_node.check_leaf == False):
            temp2 = current_node.values
            for i in range(len(temp2)):
                if (value == temp2[i]):
                    current_node = current_node.keys[i + 1]
                    break
                elif (value < temp2[i]):
                    current_node = current_node.keys[i]
                    break
                elif (i + 1 == len(current_node.values)):
                    current_node = current_node.keys[i + 1]
                    break
        return current_node

    # Find the node
    def find(self, value, key):
        l = self.search(value)
        for i, item in enumerate(l.values):
            if item == value:
                if key in l.keys[i]:
                    return True
                else:
                    return False
        return False

    # Inserting at the parent
    def insert_in_parent(self, n, value, nDash):
        if (self.root == n):
            rootNode = Node(n.order)
            rootNode.values = [value]
            rootNode.keys = [n, nDash]
            self.root = rootNode
            n.parent = rootNode
            nDash.parent = rootNode
            return

        parentNode = n.parent
        temp3 = parentNode.keys
        for i in range(len(temp3)):
            if (temp3[i] == n):
                parentNode.values = parentNode.values[:i] + \
                    [value] + parentNode.values[i:]
                parentNode.keys = parentNode.keys[:i +
                                                  1] + [nDash] + parentNode.keys[i + 1:]
                if (len(parentNode.keys) > parentNode.order):
                    parentDash = Node(parentNode.order)
                    parentDash.parent = parentNode.parent
                    mid = int(math.ceil(parentNode.order / 2)) - 1
                    parentDash.values = parentNode.values[mid + 1:]
                    parentDash.keys = parentNode.keys[mid + 1:]
                    value_ = parentNode.values[mid]
                    if (mid == 0):
                        parentNode.values = parentNode.values[:mid + 1]
                    else:
                        parentNode.values = parentNode.values[:mid]
                    parentNode.keys = parentNode.keys[:mid + 1]
                    for j in parentNode.keys:
                        j.parent = parentNode
                    for j in parentDash.keys:
                        j.parent = parentDash
                    self.insert_in_parent(parentNode, value_, parentDash)

    # Delete a node
    def delete(self, value, key):
        node_ = self.search(value)

        temp = 0
        for i, item in enumerate(node_.values):
            if item == value:
                temp = 1

                if key in node_.keys[i]:
                    if len(node_.keys[i]) > 1:
                        node_.keys[i].pop(node_.keys[i].index(key))
                    elif node_ == self.root:
                        node_.values.pop(i)
                        node_.keys.pop(i)
                    else:
                        node_.keys[i].pop(node_.keys[i].index(key))
                        del node_.keys[i]
                        node_.values.pop(node_.values.index(value))
                        self.deleteEntry(node_, value, key)
                else:
                    print("Value not in Key")
                    return
        if temp == 0:
            print("Value not in Tree")
            return

    # Delete an entry
    def deleteEntry(self, node_, value, key):

        if not node_.check_leaf:
            for i, item in enumerate(node_.keys):
                if item == key:
                    node_.keys.pop(i)
                    break
            for i, item in enumerate(node_.values):
                if item == value:
                    node_.values.pop(i)
                    break

        if self.root == node_ and len(node_.keys) == 1:
            self.root = node_.keys[0]
            node_.keys[0].parent = None
            del node_
            return
        elif (len(node_.keys) < int(math.ceil(node_.order / 2)) and node_.check_leaf == False) or (len(node_.values) < int(math.ceil((node_.order - 1) / 2)) and node_.check_leaf == True):

            is_predecessor = 0
            parentNode = node_.parent
            PrevNode = -1
            NextNode = -1
            PrevK = -1
            PostK = -1
            for i, item in enumerate(parentNode.keys):

                if item == node_:
                    if i > 0:
                        PrevNode = parentNode.keys[i - 1]
                        PrevK = parentNode.values[i - 1]

                    if i < len(parentNode.keys) - 1:
                        NextNode = parentNode.keys[i + 1]
                        PostK = parentNode.values[i]

            if PrevNode == -1:
                nDash = NextNode
                value_ = PostK
            elif NextNode == -1:
                is_predecessor = 1
                nDash = PrevNode
                value_ = PrevK
            else:
                if len(node_.values) + len(NextNode.values) < node_.order:
                    nDash = NextNode
                    value_ = PostK
                else:
                    is_predecessor = 1
                    nDash = PrevNode
                    value_ = PrevK

            if len(node_.values) + len(nDash.values) < node_.order:
                if is_predecessor == 0:
                    node_, nDash = nDash, node_
                nDash.keys += node_.keys
                if not node_.check_leaf:
                    nDash.values.append(value_)
                else:
                    nDash.nextKey = node_.nextKey
                nDash.values += node_.values

                if not nDash.check_leaf:
                    for j in nDash.keys:
                        j.parent = nDash

                self.deleteEntry(node_.parent, value_, node_)
                del node_
            else:
                if is_predecessor == 1:
                    if not node_.check_leaf:
                        nDashPm = nDash.keys.pop(-1)
                        nDashKm_1 = nDash.values.pop(-1)
                        node_.keys = [nDashPm] + node_.keys
                        node_.values = [value_] + node_.values
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = nDashKm_1
                                break
                    else:
                        nDashPm = nDash.keys.pop(-1)
                        nDashKm = nDash.values.pop(-1)
                        node_.keys = [nDashPm] + node_.keys
                        node_.values = [nDashKm] + node_.values
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = nDashKm
                                break
                else:
                    if not node_.check_leaf:
                        nDashP0 = nDash.keys.pop(0)
                        nDashK0 = nDash.values.pop(0)
                        node_.keys = node_.keys + [nDashP0]
                        node_.values = node_.values + [value_]
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = nDashK0
                                break
                    else:
                        nDashP0 = nDash.keys.pop(0)
                        nDashK0 = nDash.values.pop(0)
                        node_.keys = node_.keys + [nDashP0]
                        node_.values = node_.values + [nDashK0]
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = nDash.values[0]
                                break

                if not nDash.check_leaf:
                    for j in nDash.keys:
                        j.parent = nDash
                if not node_.check_leaf:
                    for j in node_.keys:
                        j.parent = node_
                if not parentNode.check_leaf:
                    for j in parentNode.keys:
                        j.parent = parentNode


# Print the tree
def printTree(tree):
    lst = [tree.root]
    level = [0]
    leaf = None
    flag = 0
    lev_leaf = 0

    node1 = Node(str(level[0]) + str(tree.root.values))

    while (len(lst) != 0):
        x = lst.pop(0)
        lev = level.pop(0)
        if (x.check_leaf == False):
            for i, item in enumerate(x.keys):
                print(item.values)
        else:
            for i, item in enumerate(x.keys):
                print(item.values)
            if (flag == 0):
                lev_leaf = lev
                leaf = x
                flag = 1

prefix = 'B+TreeFile_'
for i in os.listdir('./'):
    if os.path.isfile(os.path.join('./',i)) and prefix in i:
        tree = BPlusTree(record_len)
        bTreeFile = open(i, 'r')
        typeName = bTreeFile.readline().strip()
        while True:
            line = bTreeFile.readline()
            lineWords = line.strip().split()
            if not line or len(lineWords) < 2:
                break
            tree.insert(lineWords[0], lineWords[1])
        bPlusTrees[typeName] = tree

storageFiles = []

#TODO:
prefix = 'storage_file_'
for i in os.listdir('./'):
    if os.path.isfile(os.path.join('./',i)) and prefix in i:
        storageFiles.append(i)

if storageFiles:
    print(os.stat(storageFiles[len(storageFiles)-1]).st_size)
    #TODO: Son eleman dolu değilse oradan devam, dolu ise yeni file
else:
    newFileName = prefix + str(len(storageFiles) + 1) + '.txt'
    with open(newFileName, 'wb') as f:
        storageFiles.append(newFileName)
        num_chars = 1024
        #TODO: eğer full boş değilse dolu olmayan kısımların boyutu öğrenilip o kadar doldurulacak, devamına geçilmeyecek
        f.write(b'asdsa' * num_chars)

inputFile = open("input.txt", "r")
outputFileName = "output.txt"
outputFile = open(outputFileName, "w")
fLog = open('horadrimLog.csv', "a")
logFile = csv.writer(fLog)
systemCatalogFileName = "attribute_catalog.txt"
indexCatalogFileName = "index_catalog.txt"
systemCatalogFileWrite = open(systemCatalogFileName, "a")
systemCatalogFileRead = open(systemCatalogFileName, "r")
indexCatalogFileWrite = open(indexCatalogFileName, "a")
indexCatalogFileRead = open(indexCatalogFileName, "r")

createdFiles = set()

logFileTitles = ["occurrence", "operation", "status"]
logFileEntries = []

attributeCatalogTitles = ["attr_name", "rel_name", "type", "position", "is_primary"]
attributeCatalogSubRows = [
  ["attr_name", "Attribute_Cat", "string", "1", "True"], 
  ["rel_name", "Attribute_Cat", "string", "2", "False"], 
  ["type", "Attribute_Cat", "string", "3", "False"], 
  ["position", "Attribute_Cat", "integer", "4", "False"]
]
attributeCatalogValues = []
newAttributeCatalogValues = []

indexCatalogTitles = ["index_name", "table_name", "column_name", "type_desc"]
indexCatalogSubRows = [
  ["Attribute_Cat_attr_name", "Attribute_Cat", "attr_name", "Non-clustered"],
]
indexCatalogValues = []
newIndexCatalogValues = []

def fileNotExists(fileName):
    print(fileName)
    print(createdFiles)
    if fileName in createdFiles:
        return False
    return os.stat(fileName).st_size == 0

def findBTreeFileName(typeName):
    return 'B+TreeFile_' + typeName + '.txt'

def tableAlignedText(strList, length=5):
  formatString = "{: >25}"
  for i in range(1, length):
    formatString += " {: >25}"
  formatString += "\n"
  return formatString.format(*strList)

def checkInteger(fieldType, fieldName):
    if fieldType == "int":
        try:
            intField = int(fieldName)
            return True
        except:
            global isSuccess
            isSuccess = False
            return False
    return True

def createType(params):
    typeName = params[0]
    for el in attributeCatalogValues:
        elements = el.split()
        if elements[1] == typeName:
            global isSuccess
            isSuccess = False
            return
    numOfFields = int(params[1])
    primaryKeyOrder = int(params[2])
    fields = params[3:]
    fieldNames = []
    fieldTypes = []
    tableAlignedValueRowList = []
    for i in range(0, numOfFields):
        fieldName = fields[2*i]
        fieldType = fields[2*i + 1]
        fieldNames.append(fieldName)
        fieldTypes.append(fieldType)
        attributeValueRow = [fieldName, typeName, fieldType, str(i+1), "False"]
        if primaryKeyOrder-1 == i:
            attributeValueRow[4] = "True"
        tableAlignedValueRowList.append(tableAlignedText(attributeValueRow))
    bTreeFileName = findBTreeFileName(typeName)
    bTreeFile = open(bTreeFileName, "w")
    createdFiles.add(bTreeFileName)
    bTreeFile.write(typeName)
    tree = BPlusTree(record_len)
    bPlusTrees[typeName] = tree
    for tableAlignedValueRow in tableAlignedValueRowList:
        if tableAlignedValueRow.strip() not in attributeCatalogValues:
            attributeCatalogValues.append(tableAlignedValueRow.strip())
            newAttributeCatalogValues.append(tableAlignedValueRow)
    indexRow = [typeName + '_' + fieldNames[primaryKeyOrder-1], typeName, fieldNames[primaryKeyOrder-1], "Non-clustered"]
    tableAlignedIndexRow = tableAlignedText(indexRow, 4)
    if tableAlignedIndexRow.strip() not in indexCatalogValues:
        indexCatalogValues.append(tableAlignedIndexRow.strip())
        newIndexCatalogValues.append(tableAlignedIndexRow)

def createRecord(params):
    typeName = params[0]
    fieldValues = params[1:]
    foundType = False
    primaryKey = '-1 NOT FOUND'
    for el in attributeCatalogValues:
        elements = el.split()
        if elements[1] == typeName:
            elTypeIndex = int(elements[3])-1
            if elements[4] == 'True':
                primaryKey = fieldValues[elTypeIndex]
            shouldContinue = checkInteger(elements[2], fieldValues[int(elements[3])-1])
            if not shouldContinue:
                return
            foundType = True
    global isSuccess
    if not foundType:
        isSuccess = False
        return
    tree = bPlusTrees.get(typeName)
    #TODO:  Find fonksiyonuna value olarak page-id slot ikilisi verilecek
    itemFound = tree.find(typeName, primaryKey)
    if itemFound:
        isSuccess = False
        return
    tree.insert(typeName, primaryKey)
    bTreeFileName = findBTreeFileName(typeName)
    bTreeFile = open(bTreeFileName, "a")
    #TODO: Dosyaya yazış tarzı değişecek
    createdFiles.add(bTreeFileName)
    bTreeFile.write("\nkey - " + primaryKey)
    #TODO: Write to a record/page file
    #TODO: Kaç boş olduğunu gösteren sayıyı azaltacağız
    #TODO: Delete bitini değiştireceğiz
    

def deleteType(params):
    typeName = params[0]
    foundType = False
    for el in attributeCatalogValues:
        elements = el.split()
        if elements[1] == typeName:
            foundType = True
    if not foundType:
        global isSuccess
        isSuccess = False
        return
    bPlusTrees.pop(typeName)
    bTreeFileName = findBTreeFileName(typeName)
    os.remove(bTreeFileName)
    #TODO: Remove all records with this type.


def deleteRecord(params):
    typeName = params[0]
    primaryKey = params[1]
    tree = bPlusTrees.get(typeName)
    itemFound = tree.find(typeName, primaryKey)
    if not itemFound:
        global isSuccess
        isSuccess = False
        return
    tree.delete(typeName, primaryKey)
    #TODO: Tree dosyasından da sileceğiz
    #TODO: Page header'da silme bitini işaretleyeceğiz
    #TODO: Kaç boş olduğunu gösteren sayıyı artıracağız


def updateRecord(params):
    typeName = params[0]
    primaryKey = params[1]
    fieldValues = params[1:]
    tree = bPlusTrees.get(typeName)
    itemFound = tree.find(typeName, primaryKey)
    if not itemFound:
        global isSuccess
        isSuccess = False
        return
    #TODO: Sonrasında search ile page id-slot bulunacak, tree'den bulunan page-id slot ikilisi kullanılarak
    #TODO: ilgili file'da update edeceğiz


def searchRecord(params):
    typeName = params[0]
    primaryKey = params[1]
    tree = bPlusTrees.get(typeName)
    itemFound = tree.find(typeName, primaryKey)
    if not itemFound:
        global isSuccess
        isSuccess = False
        return
    doesFileNotExist = fileNotExists(outputFileName)
    itemSelf = tree.search(typeName).values[0]
    if not doesFileNotExist:
        createdFiles.add(outputFileName)
        outputFile.write('\n')
        doesFileNotExist = False
    #TODO: Itemself typename yazıyor şu anda, tree'den bulunan page-id slot ikilisi kullanılarak
    #TODO: ilgili file'dan veriler çekilecek ve tüm field'lar dosyaya yazılacak
    createdFiles.add(outputFileName)
    outputFile.write(itemSelf)
    doesFileNotExist = False
    return itemSelf


def filterRecord(params):
  typeName = params[0]
  condition = params[1]
  #TODO: Search'tekilerin aynısı


def listRecord(params):
  typeName = params[0]
  #TODO: Bütün search tree taranıp tek tek kontrol edilerek çekilecek


def listType():
    typeSet = set()
    for el in attributeCatalogValues[1:]:
        elements = el.split()
        typeSet.add(elements[1])
    doesFileNotExist = fileNotExists(outputFileName)
    for type in typeSet:
        if not doesFileNotExist:
            createdFiles.add(outputFileName)
            outputFile.write('\n')
        createdFiles.add(outputFileName)
        outputFile.write(type)
        doesFileNotExist = False
    return typeSet


isSuccess = True
def handleOperation(line):
    words = line.split()
    operationType = words[0]
    itemType = words[1]
    remainingParams = words[2:]
    if(operationType == "create"):
        if(itemType == "record"):
            createRecord(remainingParams)
        elif(itemType == "type"):
            createType(remainingParams)
    elif(operationType == "update"):
        if(itemType == "record"):
            updateRecord(remainingParams)
    elif(operationType == "list"):
        if(itemType == "record"):
            listRecord(remainingParams)
        elif(itemType == "type"):
            listType()
    elif(operationType == "filter"):
        if(itemType == "record"):
            filterRecord(remainingParams)
    elif(operationType == "delete"):
        if(itemType == "record"):
            deleteRecord(remainingParams)
        elif(itemType == "type"):
            deleteType(remainingParams)
    elif(operationType == "search"):
        if(itemType == "record"):
            searchRecord(remainingParams)
    logInfo = [str(int(time.time())), line, "success"]
    if not isSuccess:
        logInfo[2] = "failure"
    logFileEntries.append(logInfo)

if fileNotExists(systemCatalogFileName):
    cateRelString = "# Attr_Cat("
    cateRelString += ', '.join(attributeCatalogTitles)
    cateRelString += ")\n"
    createdFiles.add(systemCatalogFileName)
    systemCatalogFileWrite.write(cateRelString)
    systemCatalogFileWrite.write(tableAlignedText(attributeCatalogTitles))
    systemCatalogFileWrite.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    for row in attributeCatalogSubRows:
        systemCatalogFileWrite.write(tableAlignedText(row))

    cateIndString = "# Index_Cat("
    cateIndString += ', '.join(indexCatalogTitles)
    cateIndString += ")\n"
    createdFiles.add(indexCatalogFileName)
    indexCatalogFileWrite.write(cateIndString)
    indexCatalogFileWrite.write(tableAlignedText(indexCatalogTitles, 4))
    indexCatalogFileWrite.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    for row in indexCatalogSubRows:
        indexCatalogFileWrite.write(tableAlignedText(row, 4))

    logFile.writerow(logFileTitles)

readRowNum = 0
while True:
    readRowNum += 1
    line = systemCatalogFileRead.readline().strip()
    if not line:
      break
    if readRowNum < 7:
      continue
    attributeCatalogValues.append(line.strip())

readRowNum = 0
while True:
    readRowNum += 1
    line = indexCatalogFileRead.readline().strip()
    if not line:
      break
    if readRowNum < 3:
      continue
    indexCatalogValues.append(line.strip())
 
while True:
    isSuccess = True
    line = inputFile.readline().strip()
    if not line:
        break
    handleOperation(line)

for el in newAttributeCatalogValues:
    createdFiles.add(systemCatalogFileName)
    systemCatalogFileWrite.write(el)

for el in newIndexCatalogValues:
    createdFiles.add(indexCatalogFileName)
    indexCatalogFileWrite.write(el)

logFile.writerows(logFileEntries)

inputFile.close()

outputFile.close()
systemCatalogFileRead.close()
systemCatalogFileWrite.close()
indexCatalogFileRead.close()
indexCatalogFileWrite.close()
fLog.close()
