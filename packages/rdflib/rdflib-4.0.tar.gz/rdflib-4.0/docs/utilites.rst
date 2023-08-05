

Serializing a single term to N3
-------------------------------

For simple output, or simple serialisation, you often want a nice
readable representation of a term.  All terms have a
``.n3(namespace_manager = None)`` method, which will return a suitable
N3 format::

   >>> from rdflib import Graph, URIRef, Literal, BNode
   >>> from rdflib.namespace import FOAF, NamespaceManager

   >>> person = URIRef('http://xmlns.com/foaf/0.1/Person')
   >>> person.n3()
   u'<http://xmlns.com/foaf/0.1/Person>'

   >>> g = Graph()
   >>> g.bind("foaf", FOAF)

   >>> person.n3(g.namespace_manager)
   u'foaf:Person'

   >>> l = Literal(2)
   >>> l.n3()
   u'"2"^^<http://www.w3.org/2001/XMLSchema#integer>'
   
   >>> l.n3(g.namespace_manager)
   u'"2"^^xsd:integer'



