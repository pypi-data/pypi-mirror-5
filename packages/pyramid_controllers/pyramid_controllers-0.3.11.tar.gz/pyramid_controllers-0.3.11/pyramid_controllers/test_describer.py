# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  pyramid_controllers.test_dispatcher
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/03/20
# copy: (C) Copyright 2013 Cadit Inc., see LICENSE.txt
#------------------------------------------------------------------------------

'''
Unit test the pyramid-controllers RESTful controller helper class.
'''

import sys, re, unittest, urllib, json
import xml.etree.ElementTree as ET
from pyramid import testing
from pyramid.request import Request
from pyramid.response import Response
from pyramid.httpexceptions import \
    HTTPNotFound, HTTPFound, HTTPMethodNotAllowed, \
    HTTPException, WSGIHTTPException
from pyramid_controllers import \
    includeme, \
    Controller, RestController, DescribeController, Dispatcher, \
    expose, index, lookup, default, fiddle
from .util import adict, getVersion
from .test_helpers import TestHelper

# make the XML namespace output a bit easier to grok...
ET.register_namespace('wadl', 'http://research.sun.com/wadl/2006/10')
ET.register_namespace('xsd',  'http://www.w3.org/2001/XMLSchema')
ET.register_namespace('xsi',  'http://www.w3.org/2001/XMLSchema-instance')
ET.register_namespace('pc',   'http://github.com/cadithealth/pyramid_controllers/xmlns/0.1/doc')

class Rest(RestController):
  'A RESTful entry.'
  @expose
  def get(self, request):
    'Gets the current value.'
    return 'get!'
  @expose
  def put(self, request):
    'Updates the value.'
    return 'put!'
  @expose
  def post(self, request):
    'Creates a new entry.'
    return 'post!'
  @expose
  def delete(self, request):
    'Deletes the entry.'
    return 'delete!'
class SubIndex(Controller):
  @index(forceSlash=False)
  def myindex(self, request):
    'A sub-controller providing only an index.'
    return 'my.index'
class Sub(Controller):
  'A sub-controller.'
  @expose
  def method(self, request):
    'This method outputs a JSON list.'
    return '[3, "four"]'
  def helper(self): return 'not exposed'
class Unknown(Controller):
  'A dynamically generated sub-controller.'
class SimpleRoot(Controller):
  'A SimpleRoot controller (docs should come from index).'
  @index
  def index(self, request):
    'The default root.'
    return 'root.index'
  rest = Rest()
  sub  = Sub()
  swi  = SubIndex()
  unknown = Unknown

class StaticDescribeController(DescribeController):
  def decorateEntry(self, options, entry):
    entry = super(StaticDescribeController, self).decorateEntry(options, entry)
    if not entry or entry.path != '/rest?_method=POST':
      return entry
    entry.params = (
      adict(id='param-_2Frest_3F_5Fmethod_3DPOST-size', name='size', type='int', default=4096, optional=True, doc='The anticipated maximum size'),
      adict(id='param-_2Frest_3F_5Fmethod_3DPOST-text', name='text', type='str', optional=False, doc='The text content for the posting'),
      )
    entry.returns = (adict(id='return-_2Frest_3F_5Fmethod_3DPOST-0-str', type='str', doc='The ID of the new posting'),)
    entry.raises  = (
      adict(id='raise-_2Frest_3F_5Fmethod_3DPOST-0-HTTPUnauthorized', type='HTTPUnauthorized', doc='Authenticated access is required'),
      adict(id='raise-_2Frest_3F_5Fmethod_3DPOST-1-HTTPForbidden', type='HTTPForbidden', doc='The user does not have posting privileges'),
      )
    return entry

minRst = adict(format='rst', showSelf=False, showLegend=False,
               showGenerator=False, showLocation=False)

#------------------------------------------------------------------------------
class TestDescribeController(TestHelper):

  #----------------------------------------------------------------------------
  def test_version(self):
    v = getVersion()
    if v == 'unknown':
      # todo: this shouldn't really ever happen...
      return
    self.assertRegexpMatches(v, '^\d+(\.\d+)*$')

  #----------------------------------------------------------------------------
  def test_format_txt(self):
    'The Describer can emit a plain-text hierarchy'
    root = SimpleRoot()
    root.desc = DescribeController(root, doc='URL \t  tree\n    description.')
    self.assertResponse(self.send(root, '/desc'), 200, '''\
/                   # The default root.
|-- desc            # URL tree description.
|-- rest            # A RESTful entry.
|   |-- <DELETE>    # Deletes the entry.
|   |-- <GET>       # Gets the current value.
|   |-- <POST>      # Creates a new entry.
|   `-- <PUT>       # Updates the value.
|-- sub/
|   `-- method      # This method outputs a JSON list.
|-- swi             # A sub-controller providing only an index.
`-- ¿unknown?       # A dynamically generated sub-controller.
''')

  #----------------------------------------------------------------------------
  def test_include(self):
    'Setting the Describer `include` parameter is exclusive'
    root = SimpleRoot()
    root.desc = DescribeController(root, doc='URL tree description.',
                                   include='^/sub/method$'
                                   )
    self.assertResponse(self.send(root, '/desc'), 200, '''\
/
`-- sub/
    `-- method    # This method outputs a JSON list.
''')

  #----------------------------------------------------------------------------
  def test_exclude(self):
    'Setting the Describer `exclude` parameter is inclusive'
    root = SimpleRoot()
    root.desc = DescribeController(root, doc='URL tree description.',
                                   exclude='^/sub/method$'
                                   )
    self.assertResponse(self.send(root, '/desc'), 200, '''\
/                   # The default root.
|-- desc            # URL tree description.
|-- rest            # A RESTful entry.
|   |-- <DELETE>    # Deletes the entry.
|   |-- <GET>       # Gets the current value.
|   |-- <POST>      # Creates a new entry.
|   `-- <PUT>       # Updates the value.
|-- swi             # A sub-controller providing only an index.
`-- ¿unknown?       # A dynamically generated sub-controller.
''')

  #----------------------------------------------------------------------------
  def test_mixed_restful_and_dispatch_txt(self):
    'The Describer supports mixing RESTful and URL component methods'
    class Access(Controller):
      @index
      def index(self, request):
        'Access control'
    class Rest(RestController):
      'RESTful access, with sub-component'
      access = Access()
      @expose
      def put(self, request):
        'Modify this object'
        pass
      @expose
      def groups(self, request):
        'Return the groups for this object'
    class Root(Controller):
      rest = Rest()
    root = Root()
    root.desc = DescribeController(root, doc='URL tree description.')
    self.assertResponse(self.send(root, '/desc'), 200, '''\
/
|-- desc          # URL tree description.
`-- rest/         # RESTful access, with sub-component
    |-- <PUT>     # Modify this object
    |-- access    # Access control
    `-- groups    # Return the groups for this object
''')

  #----------------------------------------------------------------------------
  def test_mixed_restful_and_dispatch_rst(self):
    'The Describer supports mixing RESTful and URL component methods'
    class Access(Controller):
      @index
      def index(self, request):
        'Access control'
    class Rest(RestController):
      'RESTful access, with sub-component'
      access = Access()
      @expose
      def put(self, request):
        'Modify this object'
        pass
      @expose
      def groups(self, request):
        'Return the groups for this object'
    class Root(Controller):
      rest = Rest()
    root = Root()
    root.desc = DescribeController(root, doc='URL tree description.',
                                   override=minRst)
    self.assertResponse(self.send(root, '/desc'), 200, '''\
Contents of "/"
***************

/rest/
======

  RESTful access, with sub-component

  Supported Methods
  -----------------

  * **PUT**:

    Modify this object

/rest/access
============

  Access control

/rest/groups
============

  Return the groups for this object

''')

#   # TODO: enable this when txt is sensitive to forceSlash...
#   #----------------------------------------------------------------------------
#   def test_format_txt_differentiates_forced_slash_index(self):
#     'The Describer can differentiate a forced-slash index'
#     class SubIndexForceSlash(Controller):
#       @index
#       def myindex(self, request):
#         'A sub-controller providing only a slash-index.'
#         return 'my.index'
#     root = SimpleRoot()
#     root.swfs = SubIndexForceSlash()
#     root.desc = DescribeController(root, doc='URL tree description.')
#     self.assertResponse(self.send(root, '/desc'), 200, '''\
# /
# |-- desc
# |-- sub/
# |   `-- method
# |-- swfs/
# `-- swi
# ''')

  #----------------------------------------------------------------------------
  def test_format_rst(self):
    'The Describer can emit a reStructuredText description'
    root = SimpleRoot()
    root.desc = DescribeController(root, doc='URL tree description.',
                                   override=adict(format='rst'))
    self.assertResponse(self.send(root, '/desc'), 200, '''\
Contents of "/"
***************

/
=

  The default root.

/desc
=====

  URL tree description.

/rest
=====

  A RESTful entry.

  Supported Methods
  -----------------

  * **DELETE**:

    Deletes the entry.

  * **GET**:

    Gets the current value.

  * **POST**:

    Creates a new entry.

  * **PUT**:

    Updates the value.

/sub/method
===========

  This method outputs a JSON list.

/swi
====

  A sub-controller providing only an index.

/¿unknown?
==========

  A dynamically generated sub-controller.

Legend
******

  * `{{NAME}}`:

    Placeholder -- usually replaced with an ID or other identifier of a RESTful
    object.

  * `<NAME>`:

    Not an actual endpoint, but the HTTP method to use.

  * `¿NAME?`:

    Dynamically evaluated endpoint, so no further information can be determined
    without specific contextual request details.

  * `*`:

    This endpoint is a `default` handler, and is therefore free to interpret
    path arguments dynamically, so no further information can be determined
    without specific contextual request details.

  * `...`:

    This endpoint is a `lookup` handler, and is therefore free to interpret
    path arguments dynamically, so no further information can be determined
    without specific contextual request details.

.. generator: pyramid-controllers/{version} [format=rst]
.. location: http://localhost/desc
'''.format(version=getVersion()))

  #----------------------------------------------------------------------------
  def test_prune_index(self):
    'The Describer can collapse up index docs'
    class Root(Controller):
      'The Root'
      @index
      def method(self, request):
        'The index method'
        return 'ok.index'
    root = Root()
    root.desc = DescribeController(root, doc='URL tree description.',
                                   override=minRst.update())
    self.assertResponse(self.send(root, '/desc'), 200, '''\
Contents of "/"
***************

/
=

  The index method

''')

  #----------------------------------------------------------------------------
  def test_format_html(self):
    'The Describer can emit HTML'
    root = SimpleRoot()
    root.desc = StaticDescribeController(root, doc='URL tree description.',
                                         override=adict(format='html'))
    res = self.send(root, '/desc')
    chk = '''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
 <head>
  <title>Contents of "/"</title>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
  <meta name="generator" content="pyramid-controllers/{version}"/>
  <style type="text/css">
   dl{{margin-left: 2em;}}
   dt{{font-weight: bold;}}
   dd{{margin:0.5em 0 0.75em 2em;}}
  </style>
 </head>
 <body>
  <h1>Contents of "/"</h1>
  <dl class="endpoints">
   <dt id="endpoint-_2F">/</dt>
   <dd>
    <p>The default root.</p>
   </dd>
   <dt id="endpoint-_2Fdesc">/desc</dt>
   <dd>
    <p>URL tree description.</p>
   </dd>
   <dt id="endpoint-_2Frest">/rest</dt>
   <dd>
    <p>A RESTful entry.</p>
    <h3>Supported Methods</h3>
    <dl class="methods">
     <dt id="method-_2Frest-DELETE">DELETE</dt>
     <dd>
      <p>Deletes the entry.</p>
     </dd>
     <dt id="method-_2Frest-GET">GET</dt>
     <dd>
      <p>Gets the current value.</p>
     </dd>
     <dt id="method-_2Frest-POST">POST</dt>
     <dd>
      <p>Creates a new entry.</p>
      <h4>Parameters</h4>
      <dl class="params">
       <dt id="param-_2Frest_3F_5Fmethod_3DPOST-size">size</dt>
       <dd>
        <em>int, optional, default 4096</em>
        <br/>
        <p>The anticipated maximum size</p>
       </dd>
       <dt id="param-_2Frest_3F_5Fmethod_3DPOST-text">text</dt>
       <dd>
        <em>str</em>
        <br/>
        <p>The text content for the posting</p>
       </dd>
      </dl>
      <h4>Returns</h4>
      <dl class="returns">
       <dt id="return-_2Frest_3F_5Fmethod_3DPOST-0-str">str</dt>
       <dd>
        <p>The ID of the new posting</p>
       </dd>
      </dl>
      <h4>Raises</h4>
      <dl class="raises">
       <dt id="raise-_2Frest_3F_5Fmethod_3DPOST-0-HTTPUnauthorized">HTTPUnauthorized</dt>
       <dd>
        <p>Authenticated access is required</p>
       </dd>
       <dt id="raise-_2Frest_3F_5Fmethod_3DPOST-1-HTTPForbidden">HTTPForbidden</dt>
       <dd>
        <p>The user does not have posting privileges</p>
       </dd>
      </dl>
     </dd>
     <dt id="method-_2Frest-PUT">PUT</dt>
     <dd>
      <p>Updates the value.</p>
     </dd>
    </dl>
   </dd>
   <dt id="endpoint-_2Fsub_2Fmethod">/sub/method</dt>
   <dd>
    <p>This method outputs a JSON list.</p>
   </dd>
   <dt id="endpoint-_2Fswi">/swi</dt>
   <dd>
    <p>A sub-controller providing only an index.</p>
   </dd>
   <dt id="endpoint-_2Funknown">/¿unknown?</dt>
   <dd>
    <p>A dynamically generated sub-controller.</p>
   </dd>
  </dl>
  <h3>Legend</h3>
  <dl>
   <dt>{{NAME}}</dt>
   <dd>
    <p>Placeholder -- usually replaced with an ID or other identifier of a RESTful object.</p>
   </dd>
   <dt>&lt;NAME&gt;</dt>
   <dd>
    <p>Not an actual endpoint, but the HTTP method to use.</p>
   </dd>
   <dt>¿NAME?</dt>
   <dd>
    <p>Dynamically evaluated endpoint, so no further information can be determined without specific contextual request details.</p>
   </dd>
   <dt>*</dt>
   <dd>
    <p>This endpoint is a `default` handler, and is therefore free to interpret path arguments dynamically, so no further information can be determined without specific contextual request details.</p>
   </dd>
   <dt>...</dt>
   <dd>
    <p>This endpoint is a `lookup` handler, and is therefore free to interpret path arguments dynamically, so no further information can be determined without specific contextual request details.</p>
   </dd>
  </dl>
 </body>
</html>
'''.format(version=getVersion())

    chk = re.sub('>\s*<', '><', chk, flags=re.MULTILINE)
    res.body = re.sub('>\s*<', '><', res.body, flags=re.MULTILINE)
    self.assertResponse(res, 200, chk, xml=True)

  #----------------------------------------------------------------------------
  def test_format_xml(self):
    'The Describer can emit XML'
    root = SimpleRoot()
    root.desc = DescribeController(root, doc='URL tree description.',
                                   override=adict(format='xml'))
    res = self.send(root, '/desc')
    chk = '''\
<?xml version="1.0" encoding="UTF-8"?>
<application url="http://localhost">
 <endpoints>
  <endpoint name="" path="/" decorated-name="" decorated-path="/" id="endpoint-_2F">
   <doc>The default root.</doc>
   <method id="method-_2F-GET" name="GET"/>
  </endpoint>
  <endpoint name="desc" path="/desc" decorated-name="desc" decorated-path="/desc" id="endpoint-_2Fdesc">
   <doc>URL tree description.</doc>
   <method id="method-_2Fdesc-GET" name="GET"/>
  </endpoint>
  <endpoint name="rest" path="/rest" decorated-name="rest" decorated-path="/rest" id="endpoint-_2Frest">
   <doc>A RESTful entry.</doc>
   <method id="method-_2Frest-DELETE" name="DELETE"><doc>Deletes the entry.</doc></method>
   <method id="method-_2Frest-GET" name="GET"><doc>Gets the current value.</doc></method>
   <method id="method-_2Frest-POST" name="POST"><doc>Creates a new entry.</doc></method>
   <method id="method-_2Frest-PUT" name="PUT"><doc>Updates the value.</doc></method>
  </endpoint>
  <endpoint name="method" path="/sub/method" decorated-name="method" decorated-path="/sub/method" id="endpoint-_2Fsub_2Fmethod">
   <doc>This method outputs a JSON list.</doc>
   <method id="method-_2Fsub_2Fmethod-GET" name="GET"/>
  </endpoint>
  <endpoint name="swi" path="/swi" decorated-name="swi" decorated-path="/swi" id="endpoint-_2Fswi">
   <doc>A sub-controller providing only an index.</doc>
   <method id="method-_2Fswi-GET" name="GET"/>
  </endpoint>
  <endpoint name="unknown" path="/unknown" decorated-name="¿unknown?" decorated-path="/¿unknown?" id="endpoint-_2Funknown">
   <doc>A dynamically generated sub-controller.</doc>
   <method id="method-_2Funknown-GET" name="GET"/>
  </endpoint>
 </endpoints>
</application>
'''
    chk = ET.tostring(ET.fromstring(re.sub('>\s*<', '><', chk, flags=re.MULTILINE)), 'UTF-8')
    self.assertResponse(res, 200, chk, xml=True)

  #----------------------------------------------------------------------------
  def test_format_yaml(self):
    'The Describer can emit YAML'
    try:
      import yaml
    except ImportError:
      sys.stderr.write('*** YAML LIBRARY NOT PRESENT - SKIPPING *** ')
      return
    root = SimpleRoot()
    root.desc = StaticDescribeController(root, doc='URL tree description.',
                                         override=adict(format='yaml'))
    res = self.send(root, '/desc')
    chk = '''
application:
  url: 'http://localhost'
  endpoints:
    - name: ''
      id: 'endpoint-_2F'
      path: /
      decoratedName: ''
      decoratedPath: /
      doc: The default root.
    - name: desc
      id: 'endpoint-_2Fdesc'
      path: /desc
      decoratedName: desc
      decoratedPath: /desc
      doc: URL tree description.
    - name: rest
      id: 'endpoint-_2Frest'
      path: /rest
      decoratedName: rest
      decoratedPath: /rest
      doc: A RESTful entry.
      methods:
        - name: DELETE
          id: 'method-_2Frest-DELETE'
          doc: Deletes the entry.
        - name: GET
          id: 'method-_2Frest-GET'
          doc: Gets the current value.
        - name: POST
          id: 'method-_2Frest-POST'
          doc: Creates a new entry.
          params:
            - name: size
              id: 'param-_2Frest_3F_5Fmethod_3DPOST-size'
              type: int
              optional: true
              default: 4096
              doc: The anticipated maximum size
            - name: text
              id: 'param-_2Frest_3F_5Fmethod_3DPOST-text'
              type: str
              optional: false
              doc: The text content for the posting
          returns:
            - type: str
              id: 'return-_2Frest_3F_5Fmethod_3DPOST-0-str'
              doc: The ID of the new posting
          raises:
            - type: HTTPUnauthorized
              id: 'raise-_2Frest_3F_5Fmethod_3DPOST-0-HTTPUnauthorized'
              doc: Authenticated access is required
            - type: HTTPForbidden
              id: 'raise-_2Frest_3F_5Fmethod_3DPOST-1-HTTPForbidden'
              doc: The user does not have posting privileges
        - name: PUT
          id: 'method-_2Frest-PUT'
          doc: Updates the value.
    - name: method
      id: 'endpoint-_2Fsub_2Fmethod'
      path: /sub/method
      decoratedName: method
      decoratedPath: /sub/method
      doc: This method outputs a JSON list.
    - name: swi
      id: 'endpoint-_2Fswi'
      path: /swi
      decoratedName: swi
      decoratedPath: /swi
      doc: A sub-controller providing only an index.
    - name: unknown
      id: 'endpoint-_2Funknown'
      path: /unknown
      decoratedName: ¿unknown?
      decoratedPath: /¿unknown?
      doc: A dynamically generated sub-controller.
'''
    import yaml
    chk = yaml.dump(yaml.load(chk), default_flow_style=False)
    res.body = yaml.dump(yaml.load(res.body), default_flow_style=False)
    self.assertResponse(res, 200, chk)

  #----------------------------------------------------------------------------
  def test_format_yaml_dedent(self):
    'The Describer emits YAML with dedented documentation'
    try:
      import yaml
    except ImportError:
      sys.stderr.write('*** YAML LIBRARY NOT PRESENT - SKIPPING *** ')
      return
    class Root(Controller):
      @expose
      def describe(self, request):
        '''
        A multi-line
        comment.
        '''
        pass
    root = Root()
    root.desc = StaticDescribeController(root, doc='URL tree description.',
                                         override=adict(format='yaml'))
    res = self.send(root, '/desc')
    chk = '''
application:
  url: http://localhost
  endpoints:
    - name: desc
      id: 'endpoint-_2Fdesc'
      path: /desc
      decoratedName: desc
      decoratedPath: /desc
      doc: URL tree description.
    - name: describe
      id: 'endpoint-_2Fdescribe'
      path: /describe
      decoratedName: describe
      decoratedPath: /describe
      doc: "A multi-line\\ncomment."
'''
    self.assertEqual(yaml.load(res.body), yaml.load(chk))

  #----------------------------------------------------------------------------
  def test_format_json(self):
    'The Describer can emit JSON'
    root = SimpleRoot()
    root.desc = StaticDescribeController(root, doc='URL tree description.',
                                         override=adict(format='json'))
    res = self.send(root, '/desc')
    chk = '''{
  "application": {
    "url": "http://localhost",
    "endpoints": [
      { "name": "",
        "id": "endpoint-_2F",
        "path": "/",
        "decoratedName": "",
        "decoratedPath": "/",
        "doc": "The default root."
      },
      { "name": "desc",
        "id": "endpoint-_2Fdesc",
        "path": "/desc",
        "decoratedName": "desc",
        "decoratedPath": "/desc",
        "doc": "URL tree description."
      },
      { "name": "rest",
        "id": "endpoint-_2Frest",
        "path": "/rest",
        "decoratedName": "rest",
        "decoratedPath": "/rest",
        "doc": "A RESTful entry.",
        "methods": [
          { "name": "DELETE",
            "id": "method-_2Frest-DELETE",
            "doc": "Deletes the entry."
          },
          { "name": "GET",
            "id": "method-_2Frest-GET",
            "doc": "Gets the current value."
          },
          { "name": "POST",
            "id": "method-_2Frest-POST",
            "doc": "Creates a new entry.",
            "params": [
              { "name": "size",
                "id": "param-_2Frest_3F_5Fmethod_3DPOST-size",
                "type": "int",
                "optional": true,
                "default": 4096,
                "doc": "The anticipated maximum size"
              },
              { "name": "text",
                "id": "param-_2Frest_3F_5Fmethod_3DPOST-text",
                "type": "str",
                "optional": false,
                "doc": "The text content for the posting"
              }
            ],
            "returns": [
              { "type": "str",
                "id": "return-_2Frest_3F_5Fmethod_3DPOST-0-str",
                "doc": "The ID of the new posting"
              }
            ],
            "raises": [
              { "type": "HTTPUnauthorized",
                "id": "raise-_2Frest_3F_5Fmethod_3DPOST-0-HTTPUnauthorized",
                "doc": "Authenticated access is required"
              },
              { "type": "HTTPForbidden",
                "id": "raise-_2Frest_3F_5Fmethod_3DPOST-1-HTTPForbidden",
                "doc": "The user does not have posting privileges"
              }
            ]
          },
          { "name": "PUT",
            "id": "method-_2Frest-PUT",
            "doc": "Updates the value."
          }
        ]
      },
      { "name": "method",
        "id": "endpoint-_2Fsub_2Fmethod",
        "path": "/sub/method",
        "decoratedName": "method",
        "decoratedPath": "/sub/method",
        "doc": "This method outputs a JSON list."
      },
      { "name": "swi",
        "id": "endpoint-_2Fswi",
        "path": "/swi",
        "decoratedName": "swi",
        "decoratedPath": "/swi",
        "doc": "A sub-controller providing only an index."
      },
      { "name": "unknown",
        "id": "endpoint-_2Funknown",
        "path": "/unknown",
        "decoratedName": "¿unknown?",
        "decoratedPath": "/¿unknown?",
        "doc": "A dynamically generated sub-controller."
      }
    ]
  }
}
'''
    chk = json.dumps(json.loads(chk), sort_keys=True, indent=4)
    res.body = json.dumps(json.loads(res.body), sort_keys=True, indent=4)
    self.assertResponse(res, 200, chk)

  #----------------------------------------------------------------------------
  def test_format_wadl(self):
    'The Describer can emit WADL'
    root = SimpleRoot()
    root.desc = StaticDescribeController(root, doc='URL tree description.',
                                         override=adict(format='wadl'))
    res = self.send(root, '/desc')
    chk = '''
<application
 xmlns="http://research.sun.com/wadl/2006/10"
 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:pc="http://github.com/cadithealth/pyramid_controllers/xmlns/0.1/doc"
 xsi:schemaLocation="http://research.sun.com/wadl/2006/10 wadl.xsd"
 >
 <resources base="http://localhost">
  <resource id="endpoint-_2F" path="">
   <pc:doc>The default root.</pc:doc>
   <method id="method-_2F-GET" name="GET"/>
  </resource>
  <resource id="endpoint-_2Fdesc" path="desc">
   <pc:doc>URL tree description.</pc:doc>
   <method id="method-_2Fdesc-GET" name="GET"/>
  </resource>
  <resource id="endpoint-_2Frest" path="rest">
   <pc:doc>A RESTful entry.</pc:doc>
   <method id="method-_2Frest-DELETE" name="DELETE">
    <pc:doc>Deletes the entry.</pc:doc>
   </method>
   <method id="method-_2Frest-GET" name="GET">
    <pc:doc>Gets the current value.</pc:doc>
   </method>
   <method id="method-_2Frest-POST" name="POST">
    <pc:doc>Creates a new entry.</pc:doc>
    <request>
     <param id="param-_2Frest_3F_5Fmethod_3DPOST-size" name="size" type="xsd:int" required="false" default="4096">
      <pc:doc>The anticipated maximum size</pc:doc>
     </param>
     <param id="param-_2Frest_3F_5Fmethod_3DPOST-text" name="text" type="xsd:string" required="true">
      <pc:doc>The text content for the posting</pc:doc>
     </param>
    </request>
    <response>
     <representation id="return-_2Frest_3F_5Fmethod_3DPOST-0-str" element="xsd:string">
      <pc:doc>The ID of the new posting</pc:doc>
     </representation>
     <fault id="raise-_2Frest_3F_5Fmethod_3DPOST-0-HTTPUnauthorized" element="HTTPUnauthorized">
      <pc:doc>Authenticated access is required</pc:doc>
     </fault>
     <fault id="raise-_2Frest_3F_5Fmethod_3DPOST-1-HTTPForbidden" element="HTTPForbidden">
      <pc:doc>The user does not have posting privileges</pc:doc>
     </fault>
    </response>
   </method>
   <method id="method-_2Frest-PUT" name="PUT">
    <pc:doc>Updates the value.</pc:doc>
   </method>
  </resource>
  <resource id="endpoint-_2Fsub_2Fmethod" path="sub/method">
   <pc:doc>This method outputs a JSON list.</pc:doc>
   <method id="method-_2Fsub_2Fmethod-GET" name="GET"/>
  </resource>
  <resource id="endpoint-_2Fswi" path="swi">
   <pc:doc>A sub-controller providing only an index.</pc:doc>
   <method id="method-_2Fswi-GET" name="GET"/>
  </resource>
  <resource id="endpoint-_2Funknown" path="unknown">
   <pc:doc>A dynamically generated sub-controller.</pc:doc>
   <method id="method-_2Funknown-GET" name="GET"/>
  </resource>
 </resources>
</application>
'''
    # todo: what to do about mediaType, status, and namespaces?...
    # <representation mediaType="application/xml" element="yn:ResultSet"/>
    # <fault status="400" mediaType="application/xml" element="ya:Error"/>
    def roundtrip(xml):
      return ET.tostring(ET.fromstring(xml), 'UTF-8')
    chk = ET.tostring(ET.fromstring(re.sub('>\s*<', '><', chk, flags=re.MULTILINE)), 'UTF-8')
    res.body = roundtrip(res.body)
    self.assertResponse(res, 200, chk, xml=True)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
