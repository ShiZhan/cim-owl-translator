cim2rdf
=======

DMTF CIM to RDF (partially) translator

This project provides a [http://www.dmtf.org/standards/cim CIM]/[http://www.w3.org/TR/2009/REC-owl2-overview-20091027/ OWL] translator, covers class hierarchy, associations and properties. However the Qualifiers are currently ignored for model simplicity.

A brief history ...

The motivation is described [here](http://cdmd.cnki.com.cn/Article/CDMD-10487-1012268216.htm).

Original version was developed as a simple XQuery program during 2011.2~2011.8, and can be run from xquilla command line, the input source file must be compiled by OpenPegasus.

With Python and [https://github.com/RDFLib/rdflib RDFLib], the task can be much easier and open.