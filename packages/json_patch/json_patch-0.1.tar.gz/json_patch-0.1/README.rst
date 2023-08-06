.. image:: https://drone.io/bitbucket.org/eodolphi/json-patch/status.png
   :target: https://drone.io/bitbucket.org/eodolphi/json-patch/latest

JSON Patch
=============

Implementation of json-patch draft 04:

http://tools.ietf.org/html/draft-pbryan-json-patch-04

Installation
------------

 $ pip install json_patch

Usage
------------

JSON patch makes it possible to patch arbitrary json objects

>>> from json_patch import Patch
>>> patch = Patch([
        {
            'op': 'add'
            'path': '/c',
            'value': 'f'
        },
        {
            'op': 'remove': 
            'path': '/a'
        },
        {
            'op': 'replace'
            'path': '/b',
            'value': 'g'
        }
    ])
 >>> data = {'a': 'd', 'b': 'e'}
 >>> print patch.apply(data)
    {'b': 'g', 'c': 'f'}
