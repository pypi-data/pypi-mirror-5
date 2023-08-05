from thunderdome.tests.base import BaseThunderdomeTestCase
from thunderdome.spec import SpecParser, Property, Edge


class SpecParserTest(BaseThunderdomeTestCase):
    """Test spec parsing from dictionary objects"""

    def setUp(self):
        self.spec_parser = SpecParser()
        self.property_spec = {
            'type': 'property',
            'name': 'updated_at',
            'data_type': 'Integer',
            'functional': True,
            'locking': True
        }
        self.edge_spec = {
            'type': 'edge',
            'label': 'subscribed_to',
            'primary_key': 'updated_at'
        }
        self.key_index_spec = {
            'type': 'key_index',
            'name': 'email',
            'data_type': 'Vertex'
        }
        
    def test_should_return_error_if_stmt_contains_no_type(self):
        """Should raise error if statement contains no type"""
        with self.assertRaises(TypeError):
            self.spec_parser.parse_statement({'name': 'todd'})

    def test_should_raise_error_if_type_is_invalid(self):
        """Should raise error if type is invalid"""
        with self.assertRaises(ValueError):
            self.spec_parser.parse_statement({'type': 'sugar'})

    def test_should_raise_error_for_duplicate_names(self):
        """Should raise error if duplicate names given"""
        self.edge_spec['label'] = 'updated_at'
        with self.assertRaises(ValueError):
            self.spec_parser.parse_statement(self.property_spec)
            self.spec_parser.parse_statement(self.edge_spec)

    def test_should_return_correct_gremlin_for_property(self):
        """Should construct the correct Gremlin code for a property"""
        expected = 'updated_at = g.makeType().name("updated_at").dataType(Integer.class).functional(true).makePropertyKey()'
        prop = self.spec_parser.parse_property(self.property_spec)
        assert prop.gremlin == expected

        expected = 'updated_at = g.makeType().name("updated_at").dataType(Integer.class).functional(false).makePropertyKey()'
        self.property_spec['locking'] = False
        self.spec_parser._properties = {} # Reset saved properties
        self.spec_parser._names = []
        prop = self.spec_parser.parse_property(self.property_spec)
        assert prop.gremlin == expected

        expected = 'updated_at = g.makeType().name("updated_at").dataType(Integer.class).functional(false).indexed().makePropertyKey()'
        self.property_spec['locking'] = False
        self.property_spec['indexed'] = True
        self.spec_parser._properties = {} # Reset saved properties
        self.spec_parser._names = []
        prop = self.spec_parser.parse_property(self.property_spec)
        assert prop.gremlin == expected

        expected = 'updated_at = g.makeType().name("updated_at").dataType(Integer.class).makePropertyKey()'
        self.property_spec['functional'] = False
        self.property_spec['indexed'] = False
        self.spec_parser._properties = {} # Reset saved properties
        self.spec_parser._names = []
        prop = self.spec_parser.parse_property(self.property_spec)
        assert prop.gremlin == expected

        expected = 'updated_at = g.makeType().name("updated_at").dataType(Integer.class).unique().makePropertyKey()'
        self.property_spec['functional'] = False
        self.property_spec['indexed'] = False
        self.property_spec['unique'] = True
        self.spec_parser._properties = {} # Reset saved properties
        self.spec_parser._names = []
        prop = self.spec_parser.parse_property(self.property_spec)
        assert prop.gremlin == expected, prop.gremlin

    def test_should_return_correct_gremlin_for_edge(self):
        """Should return correct gremlin for an edge"""
        expected = 'subscribed_to = g.makeType().name("subscribed_to").primaryKey(updated_at).makeEdgeLabel()'
        edge = self.spec_parser.parse_edge(self.edge_spec)
        assert edge.gremlin == expected

        expected = 'subscribed_to = g.makeType().name("subscribed_to").makeEdgeLabel()'
        self.spec_parser._names = []
        del self.edge_spec['primary_key']
        edge = self.spec_parser.parse_edge(self.edge_spec)
        assert edge.gremlin == expected

    def test_functional_edge(self):
        expected = 'subscribed_to = g.makeType().name("subscribed_to").functional().makeEdgeLabel()'
        del self.edge_spec['primary_key']
        self.edge_spec['functional'] = True
        edge = self.spec_parser.parse_edge(self.edge_spec)
        assert edge.gremlin == expected

    def test_should_return_correct_gremlin_for_key_index_creation(self):
        """Should return correct gremlin for key index"""
        expected = 'g.createKeyIndex("email", Vertex.class)'
        key_index = self.spec_parser.parse_key_index(self.key_index_spec)
        assert key_index.gremlin == expected

    def test_should_return_appropriate_type(self):
        """Should return appropriate type when parsing a statement"""
        assert isinstance(self.spec_parser.parse_statement(self.edge_spec), Edge)
        assert isinstance(self.spec_parser.parse_statement(self.property_spec), Property)

    def test_should_raise_error_if_inconsistent_properties(self):
        """Should raise an error if a primary key is not defined"""
        edge_spec = {
            'type': 'edge',
            'label': 'subscribed_to',
            'primary_key': 'undefined'
        }

        results = [self.spec_parser.parse_statement(edge_spec)]
        results += [self.spec_parser.parse_statement(self.property_spec)]
        with self.assertRaises(ValueError):
            self.spec_parser.validate(results)

    def test_should_return_none_for_defaults(self):
        """Should return none for defaults"""
        default_spec = {
            'type': 'defaults',
            'spec_type': 'property',
            'functional': True
        }

        assert 'property' not in self.spec_parser._defaults
        assert self.spec_parser.parse_statement(default_spec) is None
        assert 'property' in self.spec_parser._defaults
        assert 'functional' in self.spec_parser._defaults['property']._values
