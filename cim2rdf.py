#-------------------------------------------------------------------------------
# Name:        CIM translator
# Purpose:     translate dmtf cim and snia smi-s model to rdf/owl
# Dependency:  rdflib version: 3.1.0 https://github.com/RDFLib/rdflib
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
baseURI = "http://www.storagekb.org/ontologies/2011/cim_smis.owl"
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

# Create an identifier to use as the subject for ontology.
#ontology = BNode()

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
store.add((XSD["anyType"], RDF.type, RDFS["Datatype"]))

# declare classes

#<Class rdf:about="http://www.storagekb.org/ontologies/2011/cim_smis_all.owl#CIM_Meta_Class"/>
store.add((CIM["CIM_Meta_Class"], RDF.type, OWL["Class"]))
store.add((CIM["CIM_Association"], RDF.type, OWL["Class"]))
store.add((CIM["CIM_Association"], RDFS.subClassOf, CIM["CIM_Meta_Class"]))

# class hierachy

store.add((CIM["CIM_ManagedElement"], RDF.type, OWL["Class"]))
store.add((CIM["CIM_ManagedElement"], RDFS.subClassOf, CIM["CIM_Meta_Class"]))
tempNode = BNode()
store.add((tempNode, RDF.type, OWL.Restriction))
store.add((CIM["CIM_ManagedElement"], RDFS.subClassOf, tempNode))
store.add((tempNode, OWL.onProperty, CIM["has_InstanceID"]))
store.add((tempNode, OWL.someValuesFrom, XSD["string"]))


# declare properties
store.add((CIM["has_InstanceID"], RDF.type, OWL["DatatypeProperty"]))
store.add((CIM["has_InstanceID"], RDFS.domain, CIM["CIM_Meta_Class"]))

# Iterate over triples in store and print them out.
print "--- printing raw triples ---"
for s, p, o in store:
    print ((s, p, o))

# Serialize the store as RDF/XML to the file foaf.rdf.
#store.serialize("cim_smis.rdf", format="pretty-xml", max_depth=3)

# Let's show off the serializers

print
print "RDF Serializations:"
print

# Serialize as XML
print "--- start: rdf-xml ---"
print store.serialize(format="pretty-xml")
print "--- end: rdf-xml ---\n"

# Serialize as NTriples
print "--- start: ntriples ---"
print store.serialize(format="nt")
print "--- end: ntriples ---\n"
