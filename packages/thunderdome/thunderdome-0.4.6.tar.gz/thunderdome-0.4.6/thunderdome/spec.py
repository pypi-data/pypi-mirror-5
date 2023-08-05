# Copyright (c) 2012-2013 SHIFT.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json


class Property(object):
    """Abstracts a property parsed from a spec file."""

    def __init__(self, name, data_type, functional=False, locking=True, indexed=False, unique=False):
        """
        Defines a property parsed from a spec file.

        :param name: The name of the property
        :type name: str
        :param data_type: The Java data type to be used for this property
        :type data_type: str
        :param functional: Indicates whether or not this is a functional property
        :type functional: boolean
        :param locking: Indicates whether or not to make this a locking property
        :type locking: boolean
        :param index: Indicates whether or not this field should be indexed
        :type index: boolean

        """
        self.name = name
        self.data_type = data_type
        self.functional = functional
        self.locking = locking
        self.indexed = indexed
        self.unique = unique

    @property
    def gremlin(self):
        """
        Return the gremlin code for creating this property.

        :rtype: str

        """
        initial = '{} = g.makeType().name("{}").dataType({}.class).{}{}{}makePropertyKey()'
        func = ''
        idx = ''
        if self.functional:
            func = 'functional({}).'.format("true" if self.locking else "false")
        if self.indexed:
            idx = 'indexed().'

        unique = "unique()." if self.unique else ""

        return initial.format(self.name, self.name, self.data_type, func, idx, unique)


class Edge(object):
    """Abstracts an edge parsed from a spec file."""

    def __init__(self, label, primary_key=None, functional=False):
        """
        Defines an edge parsed from a spec file.

        :param label: The label for this edge
        :type label: str
        :param primary_key: The primary key for this edge
        :type primary_key: thunderdome.spec.Property or None

        """
        self.label = label
        self.primary_key = primary_key
        self.functional = functional

    @property
    def gremlin(self):
        """
        Return the gremlin code for creating this edge.

        :rtype: str

        """
        initial = '{} = g.makeType().name("{}").{}{}makeEdgeLabel()'
        primary_key = ''
        if self.primary_key:
            primary_key = "primaryKey({}).".format(self.primary_key)

        functional = "functional()." if self.functional else ""

        return initial.format(self.label, self.label, primary_key, functional)


class KeyIndex(object):
    """Abstracts key index parsed from spec file."""

    def __init__(self, name, data_type="Vertex"):
        """
        Defines a key index parsed from spec file.

        :param name: The name for this key index
        :type name: str
        :param data_type: The data type for this key index
        :type data_type: str
        
        """
        self.name = name
        self.data_type = data_type

    @property
    def gremlin(self):
        """
        Return the gremlin code for creating this key index.

        :rtype: str
        
        """
        initial = 'g.createKeyIndex("{}", {}.class)'
        return initial.format(self.name, self.data_type)


class Default(object):
    """Abstracts defaults parsed from the spec file."""

    def __init__(self, spec_type, values):
        """
        Defines defaults for the given type.

        :param spec_type: The spec type these defaults are for
        (eg. property, edge)
        :type spec_type: str
        :param values: The default values
        :type values: dict
        
        """
        self._values = values
        self._spec_type = spec_type

    def get_spec_type(self):
        """
        Return the spec type this default is for.

        :rtype: str
        
        """
        return self._spec_type

    def get_default(self, stmt, key):
        """
        Return the default value for the given key on the given statement.
        Basically this will see if the stmt defines a value for the given
        key and if not use a default if possible.

        :param stmt: Single spec file statement
        :type stmt: dict
        :param key: The key to be searched for
        :type key: str

        :rtype: mixed
        
        """
        default = None
        if key in self._values:
            default = self._values[key]
        return stmt.get(key, default)


class SpecParser(object):
    """
    Parser for a spec file describing properties and primary keys for edges.
    This file is used to ensure duplicate primary keys are not created.

    File format:

    [
        {
            "type":"defaults",
            "spec_type": "property",
            "functional": false,
            "indexed": false,
            "locking": false
        },
        {
            "type":"property",
            "name":"updated_at",
            "data_type":"Integer",
            "functional":true,
            "locking": true,
            "indexed": true
        },
        {
            "type":"edge",
            "label":"subscribed_to",
            "primary_key":"updated_at"
        },
        {
            "type": "key_index",
            "name": "email",
            "type": "Vertex"
        }
    ]

    """

    def __init__(self, filename=None):
        """
        Pass in the filename of the spec to be parsed

        :param filename: The path to the file to be parsed
        :type filename: str

        """
        self._specs = self._load_spec(filename)
        self._properties = {}
        self._names = []
        self._defaults = {}

    def _load_spec(self, filename=None):
        """
        Loads the spec with the given filename or returns an empty
        list.

        :param filename: The filename to be opened (optional)
        :type filename: str or None
        :rtype: list

        """
        specs = []
        if filename:
            with open(filename) as spec_file:
                specs = json.load(spec_file)
        return specs

    def parse(self):
        """
        Parse the internal spec and return a list of gremlin statements.

        :rtype: list

        """
        self._properties = {}
        self._names = []

        self._results = []
        for x in self._specs:
            result = self.parse_statement(x)
            if result:
                self._results.append(result)
        self.validate(self._results)
        return self._results

    def validate(self, results):
        """
        Validate the given set of results.

        :param results: List of parsed objects
        :type results: list

        """
        edges = [x for x in results if isinstance(x, Edge)]
        props = {x.name: x for x in results if isinstance(x, Property)}

        for e in edges:
            if e.primary_key and e.primary_key not in props:
                raise ValueError('Missing primary key {} for edge {}'.format(e.primary_key, e.label))

    def parse_property(self, stmt):
        """
        Build object for a new property type.

        :param stmt: The statement to be parsed
        :type stmt: str

        :rtype: thunderdome.spec.Property

        """
        if stmt['name'] in self._properties:
            raise ValueError('There is already a property called {}'.format(stmt['name']))
        if stmt['name'] in self._names:
            raise ValueError('There is already a value with name {}'.format(stmt['name']))
        # Right now only support defaults for properties
        if 'property' in self._defaults:
            defaults = self._defaults['property']
            stmt['functional'] = defaults.get_default(stmt, 'functional')
            stmt['locking'] = defaults.get_default(stmt, 'locking')
            stmt['indexed'] = defaults.get_default(stmt, 'indexed')
            stmt['unique'] = defaults.get_default(stmt, 'unique')

        prop = Property(name=stmt['name'],
                        data_type=stmt['data_type'],
                        functional=stmt.get('functional', False),
                        locking=stmt.get('locking', True),
                        indexed=stmt.get('indexed', False),
                        unique=stmt.get('unique', False))

        self._properties[prop.name] = prop
        self._names += [prop.name]
        return prop

    def parse_edge(self, stmt):
        """
        Build object for a new edge with a primary key.

        :param stmt: The statement to be parsed
        :type stmt: str

        :rtype: thunderdome.spec.Edge

        """
        if stmt['label'] in self._names:
            raise ValueError('There is already a value with name {}'.format(stmt['label']))
        edge = Edge(label=stmt['label'],
                    primary_key=stmt.get('primary_key', None),
                    functional=stmt.get('functional', False))
        self._names += [edge.label]
        return edge

    def parse_key_index(self, stmt):
        """
        Takes the given spec statement and converts it into an object.

        :param stmt: The statement
        :type stmt: dict

        :rtype: thunderdome.spec.KeyIndex
        
        """
        if stmt['name'] in self._names:
            raise ValueError('There is already a value with name {}'.format(stmt['name']))
        key_index = KeyIndex(name=stmt['name'],
                             data_type=stmt.get('data_type', 'Vertex'))
        return key_index

    def parse_defaults(self, stmt):
        """
        Parses out statement containing default

        :param stmt: The statement
        :type stmt: dict

        :rtype: None
        
        """
        spec_type = stmt['spec_type']
        if spec_type in self._defaults:
            raise ValueError('More than one default for {}'.format(stmt['spec_type']))
        self._defaults[spec_type] = Default(spec_type, stmt)
        return None

    def parse_statement(self, stmt):
        """
        Takes the given spec statement and converts it into an object.

        :param stmt: The statement
        :type stmt: dict

        :rtype: thunderdome.spec.Property, thunderdome.spec.Edge, thunderdome.spec.KeyIndex

        """
        if 'type' not in stmt:
            raise TypeError('Type field required')

        if stmt['type'] == 'property':
            return self.parse_property(stmt)
        elif stmt['type'] == 'edge':
            return self.parse_edge(stmt)
        elif stmt['type'] == 'key_index':
            return self.parse_key_index(stmt)
        elif stmt['type'] == 'defaults':
            return self.parse_defaults(stmt)
        else:
            raise ValueError('Invalid `type` value {}'.format(stmt['type']))     


class Spec(object):
    """Represents a generic type spec for thunderdome."""

    def __init__(self, filename):
        """
        Parse and attempt to initialize the spec with the contents of the given
        file.

        :param filename: The spec file to be parsed
        :type filename: str

        """
        self._results = SpecParser(filename).parse()

    def sync(self, host, graph_name, username=None, password=None, dry_run=False):
        """
        Sync the current internal spec using the given graph on the given host.

        :param host: The host in <hostname>:<port> or <hostname> format
        :type host: str
        :param graph_name: The name of the graph as defined in rexster.xml
        :type graph_name: str
        :param username: The username for the rexster server
        :type username: str
        :param password: The password for the rexster server
        :type password: str
        :param dry_run: If true then the generated Gremlin will just be printed
        :type dry_run: boolean

        """
        def _get_name(x):
            """
            Return the name for the given object.

            :param x: The object
            :type x: Property, Edge, KeyIndex
            :rtype: str
            
            """
            if isinstance(x, Property) or isinstance(x, KeyIndex):
                return x.name
            elif isinstance(x, Edge):
                return x.label
            raise RuntimeError("Invalid object type {}".format(type(x)))
        
        if not dry_run:
            from thunderdome.connection import setup, execute_query
            setup(hosts=[host],
                  graph_name=graph_name,
                  username=username,
                  password=password,
                  index_all_fields=False)
        
        q = "def t = null"
        for x in self._results:
            name = _get_name(x)
            q += "t = g.getType('{}')\n".format(name)
            q += "if (t == null) {\n"
            q += "  {}\n".format(x.gremlin)
            q += "} else {\n"
            q += "  {} = g.getType('{}')\n".format(name, name)
            q += "}\n"
        q += "null"

        print q
        
        from thunderdome.connection import execute_query
        if not dry_run:
            return execute_query(q)
