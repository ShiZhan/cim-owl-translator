#-------------------------------------------------------------------------------
# Name:        CIM translator
# Purpose:     translate dmtf cim model to rdf/owl
# Dependency:  rdflib version: 3.3.0-dev https://github.com/RDFLib/rdflib
#
# Author:      ShiZhan
#
# Created:     08/08/2012
# Copyright:   (c) ShiZhan 2012
# Licence:     Apache License, Version 2.0
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    pass

if __name__ == '__main__':
    main()

import logging

# Configure how we want rdflib logger to log messages
_logger = logging.getLogger("rdflib")
_logger.setLevel(logging.DEBUG)
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter('%(name)s %(levelname)s: %(message)s'))
_logger.addHandler(_hdlr)

from rdflib.graph import Graph
from rdflib.term import URIRef, Literal, BNode
from rdflib.namespace import Namespace, RDF, RDFS, OWL, XSD

import time

from lxml import etree

print "Loading CIM XML ..."

# input CIM/XML model from all_classes.xml published on:
# http://www.dmtf.org/standards/cim
try:
    doc = etree.parse('all_classes.xml')
except etree.XMLSyntaxError, error_loading:
    print "error while loading."
    pass

print "Initializing RDF framework ..."

# output RDF/OWL model
store = Graph()

# Create a namespace object for the ontology namespace.
# RDF, RDFS, OWL and XSD are available by directly importing from rdflib
#RDF     = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
#RDFS    = Namespace("http://www.w3.org/2000/01/rdf-schema#")
#OWL     = Namespace("http://www.w3.org/2002/07/owl#")
#XSD     = Namespace("http://www.w3.org/2001/XMLSchema#")
DC      = Namespace("http://purl.org/dc/elements/1.1/")
TERMS   = Namespace("http://purl.org/dc/terms/")
# Newly created ontology
baseURI = "http://www.storagekb.org/ontologies/2012/dmtf_cim.owl"
BASE    = URIRef(baseURI)
CIM     = Namespace(baseURI+'#')

# Bind a few prefix, namespace pairs.
store.bind("rdf",   "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
store.bind("rdfs",  "http://www.w3.org/2000/01/rdf-schema#")
store.bind("xsd",   "http://www.w3.org/2001/XMLSchema#")
store.bind("owl",   "http://www.w3.org/2002/07/owl#")
store.bind("dc",    "http://purl.org/dc/elements/1.1/")
store.bind("terms", "http://purl.org/dc/terms/")
store.bind("cim",   CIM)

# declare metadata
store.add((BASE, RDF.type, OWL["Ontology"]))
store.add((BASE, RDFS["comment"], Literal("Computer system management ontology"
    " translated from DMTF CIM Schema, all in one version.", lang="EN")))
store.add((BASE, DC["date"], Literal("2011-3-28")))
store.add((BASE, DC["creator"], Literal("Shi.Zhan")))
store.add((BASE, DC["created"], Literal(
    time.strftime(u'%Y-%m-%d %H:%M:%S'.encode('utf-8'),
    time.localtime(time.time())).decode('utf-8'))))
store.add((BASE, TERMS["license"], Literal("Copyright 2011 Shi.Zhan."
    " Licensed under the Apache License, Version 2.0 (the \"License\");"
    " you may not use this file except in compliance with the License."
    " You may obtain a copy of the License at\n\n"
    "   http://www.apache.org/licenses/LICENSE-2.0.\n\n"
    " Unless required by applicable law or agreed to in writing,"
    " software distributed under the License is distributed on"
    " an \"AS IS\" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
    " either express or implied. See the License for the specific language"
    " governing permissions and limitations under the License.")))

# declare data types: <rdfs:Datatype rdf:about="&xsd;anyType"/>
# how to use &xsd directly? as mentioned in http://www.w3.org/TR/rdf-primer/
# solution1: use full URI
store.add((XSD.anyType, RDF.type, RDFS.Datatype))
# data type mapping
data_type_map =  ({
    # CIM       XSD
    'string':   'string',
    'boolean':  'boolean',
    'datetime': 'dateTime',
    'uint16':   'unsignedShort',
    'uint32':   'unsignedLong',
    'uint64':   'unsignedInt'
    })

# declare base classes

#<Class rdf:about="http://www.storagekb.org/ontologies/2011/cim_smis_all.owl#CIM_Meta_Class"/>
store.add((CIM["CIM_Meta_Class"], RDF.type, OWL.Class))
store.add((CIM["CIM_Association"], RDF.type, OWL.Class))
store.add((CIM["CIM_Association"], RDFS.subClassOf, CIM["CIM_Meta_Class"]))

print "Parsing and translating ..."

# import class hierarchy
try:
    classes = doc.findall("//VALUE.OBJECT/CLASS")

    for class_i in classes:
        assert class_i.attrib['NAME']!=None, 'IN CIM, Class aways has a Name.'

        # declare Class here
        class_i_uri = CIM[class_i.attrib['NAME']]
        store.add((class_i_uri, RDF.type, OWL.Class))
        # and then class hierarchy
        if class_i.find(".[@SUPERCLASS]") is not None:
            # this one has a Super Class
##            print class_i.attrib['NAME'], " is a ", class_i.attrib['SUPERCLASS']
            store.add((class_i_uri, RDFS.subClassOf, CIM[(class_i.attrib['SUPERCLASS'])]))
        else:
            # this one is on the top
            if class_i.find("./QUALIFIER[@NAME='Association']") is not None:
                # top level Association
##                print class_i.attrib['NAME'], " is an *Association"
                store.add((class_i_uri, RDFS.subClassOf, CIM["CIM_Association"]))
            else:
                # top level Meta Class
##                print class_i.attrib['NAME'], " is a *Meta Class"
                store.add((class_i_uri, RDFS.subClassOf, CIM["CIM_Meta_Class"]))

        # covert ./QUALIFIER[@NAME='Description'] to class annotation
        description_i = class_i.find("./QUALIFIER[@NAME='Description']/VALUE")
        if description_i is not None:
            # add rdfs:comment triple
            store.add((class_i_uri, RDFS.comment, Literal(description_i.text)))

        # assign restrictions (properties) to class
        # object properties
        references_i = class_i.xpath("./PROPERTY.REFERENCE")
        if references_i is not None:
            for reference_i in references_i:
                reference_i_name = reference_i.attrib['NAME']
                reference_i_obj  = reference_i.attrib['REFERENCECLASS']
                # ignore the min/max qualifiers to reduce model complexity
                restriction_node = BNode()
                store.add((restriction_node, RDF.type, OWL.Restriction))
                store.add((restriction_node, OWL.onProperty, CIM[reference_i_name]))
                store.add((restriction_node, OWL.allValuesFrom, CIM[reference_i_obj]))
                store.add((class_i_uri, RDFS.subClassOf, restriction_node))
        # data properties
        properties_i = class_i.xpath("./PROPERTY|./PROPERTY.ARRAY")
        if properties_i is not None:
            for property_i in properties_i:
                property_i_name = property_i.attrib['NAME']
                property_i_type = data_type_map.get(property_i.attrib['TYPE'], 'anyType')
                # ignore various qualifiers to reduce model complexity
                restriction_node = BNode()
                store.add((restriction_node, RDF.type, OWL.Restriction))
                store.add((restriction_node, OWL.onProperty, CIM[property_i_name]))
                store.add((restriction_node, OWL.allValuesFrom, XSD[property_i_type]))
                store.add((class_i_uri, RDFS.subClassOf, restriction_node))

    # pick out distictive properties
    # when a named property is used in different classes, they are treated as
    # different in DMTF CIM, since they work in different domains.
    # However, properties should be unique in RDF/OWL, so same-named properties
    # can be either 'renamed in different classes' or simply 'reused'
    references = doc.xpath('//VALUE.OBJECT/CLASS/PROPERTY.REFERENCE/@NAME[.]')
    object_properties = set(references)
    for object_property_i in object_properties:
        # object property declaration
##        print object_property_i
        store.add((CIM[object_property_i], RDF.type, OWL.ObjectProperty))
        store.add((CIM[object_property_i], RDFS.range,  CIM["CIM_Meta_Class"]))
        store.add((CIM[object_property_i], RDFS.domain, CIM["CIM_Association"]))

    properties = doc.xpath( '//VALUE.OBJECT/CLASS/PROPERTY/@NAME[.]|'
                            '//VALUE.OBJECT/CLASS/PROPERTY.ARRAY/@NAME[.]')
    datatype_properties = set(properties)
    for datatype_property_i in datatype_properties:
        # data property declaration
##        print datatype_property_i
        store.add((CIM[datatype_property_i], RDF.type, OWL.DatatypeProperty))
        store.add((CIM[datatype_property_i], RDFS.domain, CIM["CIM_Meta_Class"]))

except etree.XMLSyntaxError, error_parsing:
    print "error while parsing."
    pass

print "RDF Serialization ..."

# Serialize the store as RDF/XML to file.
store.serialize("dmtf_cim.owl", format="pretty-xml")

print "Produced %d Triples." % len(store)
print "----------"
print "%8d CIM Classes converted to owl:Class." % len(classes)
print "%8d CIM References converted to owl:ObjectProperty." % len(object_properties)
print "%8d CIM Properties converted to owl:DatatypeProperty." % len(datatype_properties)
