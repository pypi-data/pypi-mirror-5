.. image:: https://drone.io/bitbucket.org/eodolphi/json-reference/status.png
   :target: https://drone.io/bitbucket.org/eodolphi/json-reference/latest

JSON Reference
=============

Simple implementation of the json-pointer spec:

 http://tools.ietf.org/html/draft-pbryan-zyp-json-ref-00


Usage
------------

JSON reference makes it possible to retrieve (parts of) json-objects 

>>> import json_reference
>>> json_reference.Reference('http://json-schema.org/draft-04/schema#/definitions').get()
 
It is also possible to register references for offline access

>>> json_reference.register('http://localhost/test', {'test': 'bli'})

>>> json_reference.Reference('http://localhost/test').get()
 {'test': 'bli'}

