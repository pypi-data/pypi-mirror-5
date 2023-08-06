JSON Resource
=============

JSON resources are `dict`-like objects that have a schema associated with it. Resources can be validated, patched. Resources can also be indexed by JSON Pointers.

Resources can be stored. Currently only mongodb is supported as a database backend.

Installation
------------

pip install json_resource


Basic Usage
----------

>>> from json_resource import Resource
>>> from json_pointer import Pointer
>>> from json_hyper_schema import Schema

>>> class TestResource(Resource):
    schema = Schema({
        'id': 'test',
        'properties': {
            'test': {'name': 'string'},
            'missing': {'required': True}
        },
        'links': [{'self': '/{name}'}]
    })

>>> resource = TestResource({'name': 'bla'})
>>> pointer = Pointer('/name')
>>> resource[pointer]
 'bla'

>>> from json_patch import Patch
>>> patch = [{'op': 'add': 'path': '/value', 'value': 'bli'}]
>>> data.patch(patch)
>>> data['value']
 'bli'

>>> data.validate()
    ValidationError(....)


Stored Resources
-----

This package also provides a plugable store for resources.

>>> from json_instance.mongo import MongoResource
>>> from json_schema import Schema
>>> from pymongo import MongoClient

>>> schema = Schema({'links': {'rel': 'self', 'href': 'id/{a}'}})
>>> class TestResource(MongoResource):
        schema = schema
        db = MongoClient().test

>>> resource = TestResource.create({'a': 'b'})
>>> resource
{'a': 'b'}
>>> resource.url
'id/b'
>>> resource = TestResource.get('id/b')
>>> resource.exists
True
>>> for resource in TestResource.objects: print resource
{'a': 'b'}
>>> for resource in TestResource.objects.filter({'a': 'c'}): print resource
>>> resource.delete()
>>> for resource in TestResource.objects: print resource

