# -*- coding: utf-8 -*-
import unittest
import warnings

from datetime import datetime

from tests.fixtures import Base

from mongoengine import Document, EmbeddedDocument, connect
from mongoengine.connection import get_db
from mongoengine.fields import (BooleanField, GenericReferenceField,
                                IntField, StringField)

__all__ = ('InheritanceTest', )


class InheritanceTest(unittest.TestCase):

    def setUp(self):
        connect(db='mongoenginetest')
        self.db = get_db()

    def tearDown(self):
        for collection in self.db.collection_names():
            if 'system.' in collection:
                continue
            self.db.drop_collection(collection)

    def test_superclasses(self):
        """Ensure that the correct list of superclasses is assembled.
        """
        class Animal(Document):
            meta = {'allow_inheritance': True}
        class Fish(Animal): pass
        class Guppy(Fish): pass
        class Mammal(Animal): pass
        class Dog(Mammal): pass
        class Human(Mammal): pass

        self.assertEqual(Animal._superclasses, ())
        self.assertEqual(Fish._superclasses, ('Animal',))
        self.assertEqual(Guppy._superclasses, ('Animal', 'Animal.Fish'))
        self.assertEqual(Mammal._superclasses, ('Animal',))
        self.assertEqual(Dog._superclasses, ('Animal', 'Animal.Mammal'))
        self.assertEqual(Human._superclasses, ('Animal', 'Animal.Mammal'))

    def test_external_superclasses(self):
        """Ensure that the correct list of super classes is assembled when
        importing part of the model.
        """
        class Animal(Base): pass
        class Fish(Animal): pass
        class Guppy(Fish): pass
        class Mammal(Animal): pass
        class Dog(Mammal): pass
        class Human(Mammal): pass

        self.assertEqual(Animal._superclasses, ('Base', ))
        self.assertEqual(Fish._superclasses, ('Base', 'Base.Animal',))
        self.assertEqual(Guppy._superclasses, ('Base', 'Base.Animal',
                                               'Base.Animal.Fish'))
        self.assertEqual(Mammal._superclasses, ('Base', 'Base.Animal',))
        self.assertEqual(Dog._superclasses, ('Base', 'Base.Animal',
                                             'Base.Animal.Mammal'))
        self.assertEqual(Human._superclasses, ('Base', 'Base.Animal',
                                               'Base.Animal.Mammal'))

    def test_subclasses(self):
        """Ensure that the correct list of _subclasses (subclasses) is
        assembled.
        """
        class Animal(Document):
            meta = {'allow_inheritance': True}
        class Fish(Animal): pass
        class Guppy(Fish): pass
        class Mammal(Animal): pass
        class Dog(Mammal): pass
        class Human(Mammal): pass

        self.assertEqual(Animal._subclasses, ('Animal',
                                         'Animal.Fish',
                                         'Animal.Fish.Guppy',
                                         'Animal.Mammal',
                                         'Animal.Mammal.Dog',
                                         'Animal.Mammal.Human'))
        self.assertEqual(Fish._subclasses, ('Animal.Fish',
                                       'Animal.Fish.Guppy',))
        self.assertEqual(Guppy._subclasses, ('Animal.Fish.Guppy',))
        self.assertEqual(Mammal._subclasses, ('Animal.Mammal',
                                         'Animal.Mammal.Dog',
                                         'Animal.Mammal.Human'))
        self.assertEqual(Human._subclasses, ('Animal.Mammal.Human',))

    def test_external_subclasses(self):
        """Ensure that the correct list of _subclasses (subclasses) is
        assembled when importing part of the model.
        """
        class Animal(Base): pass
        class Fish(Animal): pass
        class Guppy(Fish): pass
        class Mammal(Animal): pass
        class Dog(Mammal): pass
        class Human(Mammal): pass

        self.assertEqual(Animal._subclasses, ('Base.Animal',
                                              'Base.Animal.Fish',
                                              'Base.Animal.Fish.Guppy',
                                              'Base.Animal.Mammal',
                                              'Base.Animal.Mammal.Dog',
                                              'Base.Animal.Mammal.Human'))
        self.assertEqual(Fish._subclasses, ('Base.Animal.Fish',
                                            'Base.Animal.Fish.Guppy',))
        self.assertEqual(Guppy._subclasses, ('Base.Animal.Fish.Guppy',))
        self.assertEqual(Mammal._subclasses, ('Base.Animal.Mammal',
                                              'Base.Animal.Mammal.Dog',
                                              'Base.Animal.Mammal.Human'))
        self.assertEqual(Human._subclasses, ('Base.Animal.Mammal.Human',))

    def test_dynamic_declarations(self):
        """Test that declaring an extra class updates meta data"""

        class Animal(Document):
            meta = {'allow_inheritance': True}

        self.assertEqual(Animal._superclasses, ())
        self.assertEqual(Animal._subclasses, ('Animal',))

        # Test dynamically adding a class changes the meta data
        class Fish(Animal):
            pass

        self.assertEqual(Animal._superclasses, ())
        self.assertEqual(Animal._subclasses, ('Animal', 'Animal.Fish'))

        self.assertEqual(Fish._superclasses, ('Animal', ))
        self.assertEqual(Fish._subclasses, ('Animal.Fish',))

        # Test dynamically adding an inherited class changes the meta data
        class Pike(Fish):
            pass

        self.assertEqual(Animal._superclasses, ())
        self.assertEqual(Animal._subclasses, ('Animal', 'Animal.Fish',
                                              'Animal.Fish.Pike'))

        self.assertEqual(Fish._superclasses, ('Animal', ))
        self.assertEqual(Fish._subclasses, ('Animal.Fish', 'Animal.Fish.Pike'))

        self.assertEqual(Pike._superclasses, ('Animal', 'Animal.Fish'))
        self.assertEqual(Pike._subclasses, ('Animal.Fish.Pike',))

    def test_inheritance_meta_data(self):
        """Ensure that document may inherit fields from a superclass document.
        """
        class Person(Document):
            name = StringField()
            age = IntField()

            meta = {'allow_inheritance': True}

        class Employee(Person):
            salary = IntField()

        self.assertEqual(['_cls', 'age', 'id', 'name', 'salary'],
                         sorted(Employee._fields.keys()))
        self.assertEqual(Employee._get_collection_name(),
                         Person._get_collection_name())

    def test_inheritance_to_mongo_keys(self):
        """Ensure that document may inherit fields from a superclass document.
        """
        class Person(Document):
            name = StringField()
            age = IntField()

            meta = {'allow_inheritance': True}

        class Employee(Person):
            salary = IntField()

        self.assertEqual(['_cls', 'age', 'id', 'name', 'salary'],
                         sorted(Employee._fields.keys()))
        self.assertEqual(list(Person(name="Bob", age=35).to_mongo().keys()),
                         ['_cls', 'name', 'age'])
        self.assertEqual(list(Employee(name="Bob", age=35, salary=0).to_mongo().keys()),
                         ['_cls', 'name', 'age', 'salary'])
        self.assertEqual(Employee._get_collection_name(),
                         Person._get_collection_name())

    def test_indexes_and_multiple_inheritance(self):
        """ Ensure that all of the indexes are created for a document with
        multiple inheritance.
        """

        class A(Document):
            a = StringField()

            meta = {
                'allow_inheritance': True,
                'indexes': ['a']
            }

        class B(Document):
            b = StringField()

            meta = {
                'allow_inheritance': True,
                'indexes': ['b']
            }

        class C(A, B):
            pass

        A.drop_collection()
        B.drop_collection()
        C.drop_collection()

        C.ensure_indexes()

        self.assertEqual(
            sorted([idx['key'] for idx in list(C._get_collection().index_information().values())]),
            sorted([[('_cls', 1), ('b', 1)], [('_id', 1)], [('_cls', 1), ('a', 1)]])
        )

    def test_polymorphic_queries(self):
        """Ensure that the correct subclasses are returned from a query
        """

        class Animal(Document):
            meta = {'allow_inheritance': True}
        class Fish(Animal): pass
        class Mammal(Animal): pass
        class Dog(Mammal): pass
        class Human(Mammal): pass

        Animal.drop_collection()

        Animal().save()
        Fish().save()
        Mammal().save()
        Dog().save()
        Human().save()

        classes = [obj.__class__ for obj in Animal.objects]
        self.assertEqual(classes, [Animal, Fish, Mammal, Dog, Human])

        classes = [obj.__class__ for obj in Mammal.objects]
        self.assertEqual(classes, [Mammal, Dog, Human])

        classes = [obj.__class__ for obj in Human.objects]
        self.assertEqual(classes, [Human])

    def test_allow_inheritance(self):
        """Ensure that inheritance is disabled by default on simple
        classes and that _cls will not be used.
        """
        class Animal(Document):
            name = StringField()

        # can't inherit because Animal didn't explicitly allow inheritance
        with self.assertRaises(ValueError):
            class Dog(Animal):
                pass

        # Check that _cls etc aren't present on simple documents
        dog = Animal(name='dog').save()
        self.assertEqual(list(dog.to_mongo().keys()), ['_id', 'name'])

        collection = self.db[Animal._get_collection_name()]
        obj = collection.find_one()
        self.assertFalse('_cls' in obj)

    def test_cant_turn_off_inheritance_on_subclass(self):
        """Ensure if inheritance is on in a subclass you cant turn it off.
        """
        class Animal(Document):
            name = StringField()
            meta = {'allow_inheritance': True}

        with self.assertRaises(ValueError):
            class Mammal(Animal):
                meta = {'allow_inheritance': False}

    def test_allow_inheritance_abstract_document(self):
        """Ensure that abstract documents can set inheritance rules and that
        _cls will not be used.
        """
        class FinalDocument(Document):
            meta = {'abstract': True,
                    'allow_inheritance': False}

        class Animal(FinalDocument):
            name = StringField()

        with self.assertRaises(ValueError):
            class Mammal(Animal):
                pass

        # Check that _cls isn't present in simple documents
        doc = Animal(name='dog')
        self.assertFalse('_cls' in doc.to_mongo())

    def test_abstract_handle_ids_in_metaclass_properly(self):

        class City(Document):
            continent = StringField()
            meta = {'abstract': True,
                    'allow_inheritance': False}

        class EuropeanCity(City):
            name = StringField()

        berlin = EuropeanCity(name='Berlin', continent='Europe')
        self.assertEqual(len(berlin._db_field_map), len(berlin._fields_ordered))
        self.assertEqual(len(berlin._reverse_db_field_map), len(berlin._fields_ordered))
        self.assertEqual(len(berlin._fields_ordered), 3)
        self.assertEqual(berlin._fields_ordered[0], 'id')

    def test_auto_id_not_set_if_specific_in_parent_class(self):

        class City(Document):
            continent = StringField()
            city_id = IntField(primary_key=True)
            meta = {'abstract': True,
                    'allow_inheritance': False}

        class EuropeanCity(City):
            name = StringField()

        berlin = EuropeanCity(name='Berlin', continent='Europe')
        self.assertEqual(len(berlin._db_field_map), len(berlin._fields_ordered))
        self.assertEqual(len(berlin._reverse_db_field_map), len(berlin._fields_ordered))
        self.assertEqual(len(berlin._fields_ordered), 3)
        self.assertEqual(berlin._fields_ordered[0], 'city_id')

    def test_auto_id_vs_non_pk_id_field(self):

        class City(Document):
            continent = StringField()
            id = IntField()
            meta = {'abstract': True,
                    'allow_inheritance': False}

        class EuropeanCity(City):
            name = StringField()

        berlin = EuropeanCity(name='Berlin', continent='Europe')
        self.assertEqual(len(berlin._db_field_map), len(berlin._fields_ordered))
        self.assertEqual(len(berlin._reverse_db_field_map), len(berlin._fields_ordered))
        self.assertEqual(len(berlin._fields_ordered), 4)
        self.assertEqual(berlin._fields_ordered[0], 'auto_id_0')
        berlin.save()
        self.assertEqual(berlin.pk, berlin.auto_id_0)

    def test_abstract_document_creation_does_not_fail(self):
        class City(Document):
            continent = StringField()
            meta = {'abstract': True,
                    'allow_inheritance': False}

        bkk = City(continent='asia')
        self.assertEqual(None, bkk.pk)
        # TODO: expected error? Shouldn't we create a new error type?
        with self.assertRaises(KeyError):
            setattr(bkk, 'pk', 1)

    def test_allow_inheritance_embedded_document(self):
        """Ensure embedded documents respect inheritance."""
        class Comment(EmbeddedDocument):
            content = StringField()

        with self.assertRaises(ValueError):
            class SpecialComment(Comment):
                pass

        doc = Comment(content='test')
        self.assertFalse('_cls' in doc.to_mongo())

        class Comment(EmbeddedDocument):
            content = StringField()
            meta = {'allow_inheritance': True}

        doc = Comment(content='test')
        self.assertTrue('_cls' in doc.to_mongo())

    def test_document_inheritance(self):
        """Ensure mutliple inheritance of abstract documents
        """
        class DateCreatedDocument(Document):
            meta = {
                'allow_inheritance': True,
                'abstract': True,
            }

        class DateUpdatedDocument(Document):
            meta = {
                'allow_inheritance': True,
                'abstract': True,
            }

        try:
            class MyDocument(DateCreatedDocument, DateUpdatedDocument):
                pass
        except Exception:
            self.assertTrue(False, "Couldn't create MyDocument class")

    def test_abstract_documents(self):
        """Ensure that a document superclass can be marked as abstract
        thereby not using it as the name for the collection."""

        defaults = {'index_background': True,
                    'index_drop_dups': True,
                    'index_opts': {'hello': 'world'},
                    'allow_inheritance': True,
                    'queryset_class': 'QuerySet',
                    'db_alias': 'myDB',
                    'shard_key': ('hello', 'world')}

        meta_settings = {'abstract': True}
        meta_settings.update(defaults)

        class Animal(Document):
            name = StringField()
            meta = meta_settings

        class Fish(Animal): pass
        class Guppy(Fish): pass

        class Mammal(Animal):
            meta = {'abstract': True}
        class Human(Mammal): pass

        for k, v in defaults.items():
            for cls in [Animal, Fish, Guppy]:
                self.assertEqual(cls._meta[k], v)

        self.assertFalse('collection' in Animal._meta)
        self.assertFalse('collection' in Mammal._meta)

        self.assertEqual(Animal._get_collection_name(), None)
        self.assertEqual(Mammal._get_collection_name(), None)

        self.assertEqual(Fish._get_collection_name(), 'fish')
        self.assertEqual(Guppy._get_collection_name(), 'fish')
        self.assertEqual(Human._get_collection_name(), 'human')

        # ensure that a subclass of a non-abstract class can't be abstract
        with self.assertRaises(ValueError):
            class EvilHuman(Human):
                evil = BooleanField(default=True)
                meta = {'abstract': True}

    def test_abstract_embedded_documents(self):
        # 789: EmbeddedDocument shouldn't inherit abstract
        class A(EmbeddedDocument):
            meta = {"abstract": True}

        class B(A):
            pass

        self.assertFalse(B._meta["abstract"])

    def test_inherited_collections(self):
        """Ensure that subclassed documents don't override parents'
        collections
        """

        class Drink(Document):
            name = StringField()
            meta = {'allow_inheritance': True}

        class Drinker(Document):
            drink = GenericReferenceField()

        try:
            warnings.simplefilter("error")

            class AcloholicDrink(Drink):
                meta = {'collection': 'booze'}

        except SyntaxWarning:
            warnings.simplefilter("ignore")

            class AlcoholicDrink(Drink):
                meta = {'collection': 'booze'}

        else:
            raise AssertionError("SyntaxWarning should be triggered")

        warnings.resetwarnings()

        Drink.drop_collection()
        AlcoholicDrink.drop_collection()
        Drinker.drop_collection()

        red_bull = Drink(name='Red Bull')
        red_bull.save()

        programmer = Drinker(drink=red_bull)
        programmer.save()

        beer = AlcoholicDrink(name='Beer')
        beer.save()
        real_person = Drinker(drink=beer)
        real_person.save()

        self.assertEqual(Drinker.objects[0].drink.name, red_bull.name)
        self.assertEqual(Drinker.objects[1].drink.name, beer.name)


if __name__ == '__main__':
    unittest.main()
