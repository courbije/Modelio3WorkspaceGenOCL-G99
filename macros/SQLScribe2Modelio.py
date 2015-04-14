"""
=========================================================
SQLScribe2OCL.py
Generate a Modelio Relational diagramme from a XML file produce by SQLScribe
=========================================================
"""

MODULES_TO_RELOAD = ["modelioscriptor"]

def startup():
    try:
        from org.modelio.api.modelio import Modelio
        orgVersion = True
    except:
        orgVersion = False
    import os
    import sys
    WORKSPACE_DIRECTORY=Modelio.getInstance().getContext().getWorkspacePath().toString()
    if orgVersion:
        MACROS_DIRECTORY=os.path.join(WORKSPACE_DIRECTORY,'macros')
    else:
        MACROS_DIRECTORY=os.path.join(WORKSPACE_DIRECTORY,'.config','macros')
    SCRIPT_LIBRARY_DIRECTORY=os.path.join(MACROS_DIRECTORY,'lib')
    sys.path.extend([MACROS_DIRECTORY,SCRIPT_LIBRARY_DIRECTORY])

try:
    CO_EXPLORER_EXECUTION += 1
# this is the not the first time
except:
    # this is the first time
    CO_EXPLORER_EXECUTION = 1
    startup()

if "modelioscriptor" in MODULES_TO_RELOAD:
    try: del sys.modules["modelioscriptor"] ; del modelioscriptor
    except: pass
from modelioscriptor import *

import xml.etree.ElementTree as ElementTree
package = instanceNamed(Package,"SQLscribe")


"""
=========================================================
Génération d'un diagramme pour modélio
=========================================================
"""

class Dependency :
    parent = None
    child = None

def SQLScribeType2ModelioType (t):
    types = theSession().getModel().getUmlTypes()
    if (t == "INT" or t == "BIGINT"):
        return types.getINTEGER()
    elif (t == "CHAR" or t == "VARCHAR"):
        return types.getSTRING()
    elif (t == "DATE"):
        return types.getDATE()

def generateClass(table,dependency):
    print table.name
    fact = theUMLFactory()
    newClass = fact.createClass(table.name, package)
    isTable=False
    for column in table.columns :
        if (column.isPK == False and column.isFK == False) :
            isTable = True
        addAttributeToClass(newClass,column,dependency)
    if isTable:
        newClass.addStereotype("LocalModule", "Table")

def addAttributeToClass(class_,column,dependency):
    fact = theUMLFactory()
    newAttribute = fact.createAttribute(column.name, SQLScribeType2ModelioType(column.type), class_)
    if (column.isPK) :
        newAttribute.addStereotype("LocalModule", "PK")
    if (column.isFK) :
        newAttribute.addStereotype("LocalModule", "FK")
    for child in column.child :
        if not (child in dependency.keys()) :
            dependency[child] = Dependency()
        dependency[child].child = newAttribute
    if column.parent != '' :
        if not (column.parent in dependency.keys()) :
            dependency[column.parent] = Dependency()
        dependency[column.parent].parent = newAttribute

def generateAllClass(tables,dependency):
    trans = theSession().createTransaction("generateAllClass")
    try :
        for table in tables :
            generateClass(table,dependency)
        trans.commit()
    except :
        print "transaction fail"
        trans.rollback()


def generateDependency(dependency):
    trans = theSession().createTransaction("generateDependency")
    try :
        fact = theUMLFactory()
        for dep in dependency.keys() :
            print dep
            fact.createDependency(dependency[dep].parent, dependency[dep].child, "LocalModule", "FKC")
        trans.commit()
    except:
        print "transaction fail"
        trans.rollback()


def init() :
    trans = theSession().createTransaction("clean package")
    try:
        for o in package.getOwnedElement(Class):
            o.delete()
        trans.commit()
    except:
        print "transaction fail"
        trans.rollback()

"""
=========================================================
Parcours du XML
=========================================================
"""

class Column:
    name = ''
    type = ''
    isPK = False
    isFK = False
    child = []
    parent = ''


class Table:
    columns = []
    name = ''

def parseColumn(column) :
    col = Column()
    col.child = []
    col.name = column.attrib.get('name')
    col.type = column.attrib.get('type')
    for child in column.findall('child') :
        col.child.append(child.attrib.get('foreignKey'))
    if column.find('parent') != None:
        col.parent=column.find('parent').attrib.get('foreignKey')
    return col

def parseTable(table) :
    res = Table()
    res.name =table.attrib.get('name')
    res.columns = []
    primaryKeys = []
    for pk in table.findall('primaryKey'):
        primaryKeys.append(pk.attrib.get('column'))
    for column in table.findall('column'):
        col = parseColumn(column)
        col.isPK = (column.attrib.get('name') in primaryKeys)
        col.isFK = (column.find('parent') != None)
        res.columns.append(col)
    return res

def parseTables(root) :
    tables = []
    for table in root.find('tables'):
        tables.append(parseTable(table))
    return tables

def main():
    XML_DIRECTORY = Modelio.getInstance().getContext().getWorkspacePath().toString() + "/macros/xml/library.xml"
    tree = ElementTree.parse(XML_DIRECTORY)
    init()
    dependency = {}
    tables = parseTables(tree.getroot())
    generateAllClass(tables,dependency)
    generateDependency(dependency)


main()

