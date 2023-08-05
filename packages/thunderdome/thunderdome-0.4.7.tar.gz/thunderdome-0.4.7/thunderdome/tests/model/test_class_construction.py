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

from thunderdome.tests.base import BaseThunderdomeTestCase

from thunderdome.exceptions import ModelException, ThunderdomeException
from thunderdome.models import Vertex, Edge
from thunderdome import properties, ValidationError
import thunderdome

from thunderdome.tests.models import TestModel

class WildDBNames(Vertex):
    content = properties.Text(db_field='words_and_whatnot')
    numbers = properties.Integer(db_field='integers_etc')
            
class Stuff(Vertex):
    num = properties.Integer()

class TestModelClassFunction(BaseThunderdomeTestCase):
    """
    Tests verifying the behavior of the Model metaclass
    """

    def test_column_attributes_handled_correctly(self):
        """
        Tests that column attributes are moved to a _columns dict
        and replaced with simple value attributes
        """

        #check class attibutes
        self.assertHasAttr(TestModel, '_columns')
        self.assertHasAttr(TestModel, 'vid')
        self.assertHasAttr(TestModel, 'text')

        #check instance attributes
        inst = TestModel()
        self.assertHasAttr(inst, 'vid')
        self.assertHasAttr(inst, 'text')
        self.assertIsNone(inst.vid)
        self.assertIsNone(inst.text)

    def test_db_map(self):
        """
        Tests that the db_map is properly defined
        -the db_map allows columns
        """


        db_map = WildDBNames._db_map
        self.assertEquals(db_map['words_and_whatnot'], 'content')
        self.assertEquals(db_map['integers_etc'], 'numbers')

    def test_attempting_to_make_duplicate_column_names_fails(self):
        """
        Tests that trying to create conflicting db column names will fail
        """

        with self.assertRaises(ModelException):
            class BadNames(Vertex):
                words = properties.Text()
                content = properties.Text(db_field='words')

    def test_value_managers_are_keeping_model_instances_isolated(self):
        """
        Tests that instance value managers are isolated from other instances
        """
        inst1 = TestModel(count=5)
        inst2 = TestModel(count=7)

        self.assertNotEquals(inst1.count, inst2.count)
        self.assertEquals(inst1.count, 5)
        self.assertEquals(inst2.count, 7)

class RenamedTest(thunderdome.Vertex):
    element_type = 'manual_name'
    
    vid = thunderdome.UUID(primary_key=True)
    data = thunderdome.Text()
        
class TestManualTableNaming(BaseThunderdomeTestCase):
    
    def test_proper_table_naming(self):
        assert RenamedTest.get_element_type() == 'manual_name'

class BaseAbstractVertex(thunderdome.Vertex):
    __abstract__ = True
    data = thunderdome.Text()

class DerivedAbstractVertex(BaseAbstractVertex): pass

class TestAbstractElementAttribute(BaseThunderdomeTestCase):

    def test_abstract_property_is_not_inherited(self):
        assert BaseAbstractVertex.__abstract__
        assert not DerivedAbstractVertex.__abstract__

    def test_abstract_element_persistence_methods_fail(self):
        bm = BaseAbstractVertex(data='something')

        with self.assertRaises(ThunderdomeException):
            bm.save()

        with self.assertRaises(ThunderdomeException):
            bm.delete()

        with self.assertRaises(ThunderdomeException):
            bm.update(data='something else')



class TestValidationVertex(Vertex):
    num     = thunderdome.Integer(required=True)
    num2    = thunderdome.Integer(required=True)

    def validate_num(self, value):
        val = self.validate_field('num', value)
        return 5

    def validate_num2(self, value):
        return 5

class TestValidation(BaseThunderdomeTestCase):

    def test_custom_validation_method(self):
        v = TestValidationVertex.create(num=6)
        assert v.num == 5
        assert v.num2 == 5

        with self.assertRaises(ValidationError):
            TestValidationVertex.create()










