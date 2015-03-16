"""
    =========================================================
    GenOCL.py
    Generate a USE OCL specification from a UML package
    =========================================================
    
    FILL THIS SECTION AS SHOWN BELOW AND LINES STARTING WITH ###
    @author Xuan Shong TI WONG SHI <xuan.ti@mydomain.com>
    @author Maria Shohie CEZAR LOPEZ DE ANDERA <maria.cezar@ujf-grenoble.fr>
    @group  G99
    
    Current state of the generator
    ----------------------------------
    FILL THIS SECTION
    Explain which UML constructs are supported, which ones are not.
    What is good in your generator?
    What are the current limitations?
    
    Current state of the tests
    --------------------------
    FILL THIS SECTION
    Explain how did you test this generator.
    Which test are working?
    Which are not?
    
    Observations
    ------------
    Additional observations could go there
"""


#---------------------------------------------------------
#   Helpers on the source metamodel (UML metamodel)
#---------------------------------------------------------
# The functions below can be seen as extensions of the
# modelio metamodel. They define useful elements that
# are missing in the current metamodel but that allow to
# explorer the UML metamodel with ease.
# These functions are independent from the particular
# problem at hand and could be reused in other
# transformations taken UML models as input.
#---------------------------------------------------------

# example
def isAssociationClass(element):
    """
        Return True if and only if the element is an association
        that have an associated class, or if this is a class that
        has a associated association. (see the Modelio metamodel
        for details)
    """
# TODO


#---------------------------------------------------------
#   Application dependent helpers on the source metamodel
#---------------------------------------------------------
# The functions below are defined on the UML metamodel
# but they are defined in the context of the transformation
# from UML Class diagramm to USE OCL. There are not
# intended to be reusable.
#---------------------------------------------------------


def associationsInPackage(package):
    """
        Return the list of all associations that start or
        arrive to a class which is recursively contained in
        a package.
    """
    listAsso = []
    for clas in package.getOwnedElement():
        if isinstance(clas, Class) :
            for assoEnd in clas.getOwnedEnd():
                asso = assoEnd.getAssociation()
                if asso not in listAsso and isinstance(asso, Association) and not asso.getLinkToClass()  :
                    listAsso.append(asso)
            for assoEnd in clas.getOwnedNaryEnd():
                asso = assoEnd.getNaryAssociation()
                if asso not in listAsso :
                    listAsso.append(asso)
    return listAsso

def associationsInPackages(packages):
    """
        Return the list of all associations that start or
        arrive to a class which is recursively contained in
        all package.
    """
    listAsso = []
    for package in packages.getOwnedElement():
        for asso in associationsInPackage(package) :
            if asso not in listAsso :
                listAsso.append(asso)
    return listAsso


#---------------------------------------------------------
#   Helpers for the target representation (text)
#---------------------------------------------------------
# The functions below aims to simplify the production of
# textual languages. They are independent from the
# problem at hand and could be reused in other
# transformation generating text as output.
#---------------------------------------------------------


# for instance a function to indent a multi line string if
# needed, or to wrap long lines after 80 characters, etc.

#---------------------------------------------------------
#           Transformation functions: UML2OCL
#---------------------------------------------------------
# The functions below transform each element of the
# UML metamodel into relevant elements in the OCL language.
# This is the core of the transformation. These functions
# are based on the helpers defined before. They can use
# print statement to produce the output sequentially.
# Another alternative is to produce the output in a
# string and output the result at the end.
#---------------------------------------------------------



# examples

def umlEnumeration2OCL(enumeration):
    """
        Generate USE OCL code for the enumeration
    """
    x=""
    print "enum %s {" % enumeration.getName()
    for e in enumeration.getValue():
        x+= "\t%s,\n" % e.getName()
    x=x[:-2]
    print x
    print "}"

def umlBasicType2OCL(basicType):
    """
        Generate USE OCL basic type. Note that
        type conversions are required.
    """
    t = basicType.getName()
    if (t == "integer" or t=="") :
        return "Integer"
    elif (t == "string") :
        return "String"
    elif (t == "boolean") :
        return "Boolean"
    elif (t == "float") :
        return "Real"
    else:
        return t



def umlOperations2OCL(operations):
    """
        Generate USE OCL code for all operation of a class
    """
    if (operations):
        print "operations"
    for operation in operations:
        name = operation.getName()
        
        #recuperation des parametres
        parameters = ""
        for parameter in operation.getIO():
            parameters += "%s : %s," % (parameter.getName(),umlBasicType2OCL(parameter.getType()))
        if (operation.getIO()):
            parameters=parameters[:-1]

        #valeur de retour
        type = " : %s" % umlBasicType2OCL(operation.getReturn().getType()) if operation.getReturn() else ""
        print "\t%s(%s)%s" % (name,parameters,type)


def umlAttributes2OCL(attributes):
    """
        Generate USE OCL code for all attributes of a class
    """
    if (attributes):
        print "attributes"
    for attribute in attributes:
        name = attribute.getName()
        type = umlBasicType2OCL(attribute.getType())
        annotation = ""
        if attribute.isDerived :
            annotation += " @derived"
        if attribute.getVisibility() == VisibilityMode.PUBLIC :
            annotation += " @Public"
        elif attribute.getVisibility() == VisibilityMode.PRIVATE :
            annotation += " @Private"
        elif attribute.getVisibility() == VisibilityMode.PACKAGEVISIBILITY :
            annotation += " @Package"
        elif attribute.getVisibility() == VisibilityMode.PROTECTED :
            annotation += " @Protected"

        annotation = "" if annotation=="" else "  -- " + annotation
        print "\t%s : %s%s" % (name ,type,annotation)

def umlClass2OCL(clas):
    """
        Generate USE OCL code for the class
    """
    abstract = "abstract " if clas.isAbstract else ""
    if not clas.getLinkToAssociation() :
        inheritance = ""
        for parent in clas.getParent() :
            inheritance += " %s,"  % parent.getSuperType().getName()
        inheritance = "" if inheritance == "" else  " <" + inheritance[:-1]
        print "%sclass %s%s" % (abstract,clas.getName(),inheritance)
    else :
        print "%sassociationclass %s between" % (abstract,clas.getName())
        for end in clas.getLinkToAssociation().getAssociationPart().getEnd():
            umlAssociationEnd2OCL(end)
    umlAttributes2OCL(clas.getOwnedAttribute())
    umlOperations2OCL(clas.getOwnedOperation())
    print "end\n"

def umlAssociationEnd2OCL(end):
    if isinstance(end, AssociationEnd) :
        class_name = end.getOppositeOwner().getOwner().getName()
    else :
        class_name = end.getOwner().getName()
    #cardinality
    min = end.getMultiplicityMin()
    max = end.getMultiplicityMax()
    max = min if max == "" else max
    if max == min :
        multiplicity = "[%s]" % min
    elif min == "" :
        multiplicity = ""
    elif max == "*" and min == "0" :
        multiplicity = "[%s]" % max
    else :
        multiplicity = "[%s..%s]" % (min,max)
    
    role_name = end.getName()
    role = "" if role_name == "" else "role "+role_name
    order = " ordered" if end.isIsOrdered() else ""
    print "\t%s%s %s%s" % (class_name,multiplicity,role,order)

def umlAssociation2OCL(association):
    """
        Generate USE OCL code for the association
    """
    #type
    type = "association"
    if isinstance(association, Association) :
        for end in association.getEnd():
            if end.getAggregation() == AggregationKind.KINDISCOMPOSITION:
                type = "composition"
            if end.getAggregation() == AggregationKind.KINDISAGGREGATION:
                type = "aggregation"

    name = association.getName()
    name = association.getUuid().toString() if name=="" else name
    print "%s %s between" % (type, name)

    if isinstance(association, Association) :
        for end in association.getEnd():
            umlAssociationEnd2OCL(end)
    else :
        for end in association.getNaryEnd():
            umlAssociationEnd2OCL(end)

    print "end\n"



def package2OCL(package):
    """
        Generate a complete OCL specification for a given package.
        The inner package structure is ignored. That is, all
        elements useful for USE OCL (enumerations, classes,
        associationClasses, associations and invariants) are looked
        recursively in the given package and output in the OCL
        specification. The possibly nested package structure that
        might exist is not reflected in the USE OCL specification
        as USE is not supporting the concept of package.
        """
    for c in package.getOwnedElement():
        if isinstance(c, Enumeration) :
            umlEnumeration2OCL(c)
        if isinstance(c, Class):
            umlClass2OCL(c)
    for asso in associationsInPackage(package):
        umlAssociation2OCL(asso)


def packages2OCL(packages):
    """
        Generate a complete OCL specification for all packages
    """
    for package in packages.getOwnedElement():
        for c in package.getOwnedElement():
            if isinstance(c, Enumeration) :
                umlEnumeration2OCL(c)

    for package in packages.getOwnedElement():
        for c in package.getOwnedElement():
            if isinstance(c, Class):
                umlClass2OCL(c)

    for asso in associationsInPackages(packages):
        umlAssociation2OCL(asso)

def main():
    for c in selectedElements:
        print "\nmodel %s\n\n" % c.getName()
        packages2OCL(c)

def test():
    for c in selectedElements:
        package2OCL(c)

test()




#---------------------------------------------------------
#           User interface for the Transformation
#---------------------------------------------------------
# The code below makes the link between the parameter(s)
# provided by the user or the environment and the
# transformation functions above.
# It also produces the end result of the transformation.
# For instance the output can be written in a file or
# printed on the console.
#---------------------------------------------------------

# (1) computation of the 'package' parameter
# (2) call of package2OCL(package)
# (3) do something with the result
