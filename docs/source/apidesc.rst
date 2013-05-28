API Description Language
========================

All REST Coder tools take an API description (specification) as input. These API descriptions should be specified in a JSON based language, as described below.

The JSON based API description language captures all the resources, operations and data types related to a web API. It also captures a wide range of non-functional properties of APIs such as licensing information, ownership information and SLA details. These API descriptions can be compiled manually or generated automatically by analyzing the source code of the web API/service implementations.

The high-level grammar/structure of this API description language is described in the next section.

Language Grammar
----------------

API
^^^
::

  {
    "name" : "string",
    "description" : "string",
    "version": {
        "identifier" : "string",
        "scheme" : "BaseAppend|Header|None",
        "compatibility" : [ "string", "string", "string" ]
    },
    "base" : [ "url", "url" ],
    "state" : "active|deprecated|retired",

    "resources" : [...],
    "dataTypes" : [...],

    "security" : {
        "ssl" : "Always|Never|Optional",
        "auth" : "Basic|OAuth",
        "credentials" : "url"
    },

    "license" : "string",
    "ownership" : [...],
    "categories" : [ "string", "string", "string" ],
    "tags" : [ "string", "string", "string" ],
    "community" : "url"
    "sla" : [...]
  }

Resource
^^^^^^^^
::

  {
    "name" : "string",
    "path" : "uri-template",
    "inputBindings" : [...],
    "operations" : [...]
  }

Input Binding
^^^^^^^^^^^^^
::

  {
    "id" : "string",
    "mode" : "url|query|header",
    "name" : "string",
    "type" : "TypeRef|TypeDef",
  }

Operation
^^^^^^^^^
::

  {
    "name" : "string",
    "method" : "GET|POST|PUT|DELETE|OPTIONS|HEAD",
    "description" : "string",
    "input" : {
        "contentType" : [ "mime-type", "mime-type" ],
        "type" : "TypeDef|TypeRef",
        "params" : [...]   
    },
    "output" : {
        "status" : HTTP status code,
        "contentType" : [ "mime-type", "mime-type" ],
        "model" : "TypeDef|TypeRef",
        "headers" : [...]
    },
    "errors" : [...]
  } 

Parameter
^^^^^^^^^
::

  {
    "binding" : "string",
    "description" : "string"
    "optional" : true|false
  }

Or::

  {
    "mode" : "url|query|header",
    "name" : "string",
    "type" : "TypeRef|TypeDef",
    "description" : "string"
    "optional" : true|false
  }

Header
^^^^^^
::

  {
    "name" : "string",
    "type" : TypeRef|TypeDef,
    "ref" : "string",
    "description" : "string"
  }

Error
^^^^^
::

  {
    "status" : HTTP status code,
    "cause" : "string"
  }

Type Definition (TypeDef)
^^^^^^^^^^^^^^^^^^^^^^^^^
::

  {
    "name" : "string",
    "description" : "string",
    "fields" : [...]
  }

Field
^^^^^
::

  {
    "name" : "string",
    "description" : "string",
    "type" : "TypeRef | TypeDef",
    "optional" : true | false,
    "ref" : "string",
    "multi" : true | false
  }

Type Reference (TypeRef)
^^^^^^^^^^^^^^^^^^^^^^^^
A type reference is a string literal that points to a primitive type, container type or a user defined type. ::

  PrimitiveTypeName | ContainerTypeName | UserDefinedTypeName

This API description language supports following primitive types.

  * int
  * long
  * short
  * double
  * string
  * boolean
  * byte
  * binary
  * href

A container type is a type reference wrapped in one of the following containers.
 
  * list
  * set

SLA
^^^
::

  {
    "name" : "string",
    "availability" : percentage,
    "rateLimit" : int,
    "timeUnit" : "second|minute|hour|day",
    "costModel" : {
        "unitPrice" : double,
        "currency" : "string",
        "requestsPerUnit" : int
    }   
  }

Owner
^^^^^
::

  {
    "name" : "string",
    "email" : "string",
    "ownerType" : "string"
  }

Example API Description
-----------------------
This section further explains the syntax and semantics of the API description language using the specification of a hypothetical API named ``Starbucks`` as an example. ::

  {
    "name":"Starbucks",
    "resources":[
        {
            "name":"Order",
            "path":"/{orderId}",
            "operations":[
                {
                    "name":"getOrder",
                    "method":"GET",
                    "description":"Retrieve the order identified by the specified identifier",
                    "input":{
                        "params":[
                            {
                                "optional":false,
                                "binding":"orderIdBinding"
                            }
                        ]
                    },
                    "output":{
                        "type":"Order",
                        "contentType":["application/json"],
                        "status":200
                    },
                    "errors":[
                        {
                            "cause":"Specified order does not exist",
                            "status":404
                        },
                        {
                            "cause":"An unexpected runtime exception",
                            "status":500
                        }
                    ]
                },
                {
                    "name":"deleteOrder",
                    "method":"DELETE",
                    "description":"Remove the order identified by the specified ID from the system",
                    "input":{
                        "params":[
                            {
                                "optional":false,
                                "binding":"orderIdBinding"
                            }
                        ]
                    },
                    "output":{
                        "type":"Order",
                        "contentType":["application/json"],
                        "status":200
                    },
                    "errors":[
                        {
                            "cause":"Specified order does not exist",
                            "status":404
                        },
                        {
                            "cause":"An unexpected runtime exception",
                            "status":500
                        }
                    ]
                }
            ],
            "inputBindings":[
                {
                    "id":"orderIdBinding",
                    "name":"orderId",
                    "type":"string",
                    "mode":"url"
                }
            ]
        },
        {
            "name":"AllOrders",
            "path":"/",
            "operations":[
                {
                    "name":"submitOrder",
                    "method":"POST",
                    "description":"Place a new drink order.",
                    "input":{
                        "type":"OrderRequest",
                        "contentType":["application/json", "application/xml"]
                    },
                    "output":{
                        "type":"Order",
                        "contentType":["application/json"],
                        "headers":[
                            {
                                "name":"Location",
                                "type":"href",
                                "ref":"Order",
                                "description":"A URL pointer to the Order resource created by this operation"
                            }
                        ],
                        "status":201
                    },
                    "errors":[
                        {
                            "cause":"An unexpected runtime exception",
                            "status":500
                        }
                    ]
                },
                {
                    "name":"getAllOrders",
                    "method":"GET",
                    "description":"Retrieve all the orders currently pending in the system",
                    "output":{
                        "type":"list(Order)",
                        "contentType":["application/json"],
                        "status":200
                    },
                    "errors":[
                        {
                            "cause":"An unexpected runtime exception",
                            "status":500
                        }
                    ]
                }
            ]
        }
    ],
    "description":"Place and manage drink orders online.",
    "categories":["marketing", "retail"],
    "tags":["beverages", "recreation", "marketing", "sales"],
    "base":[
        "http://localhost:8080/starbucks-1.0-SNAPSHOT/starbucks",
        "https://localhost:8243/starbucks-1.0-SNAPSHOT/starbucks"
    ],
    "dataTypes":[
        {
            "name":"Order",
            "fields":[
                {
                    "name":"orderId",
                    "type":"string",
                    "description":"Unique system generated string identifier of the drink.",
                    "optional":false,
                    "unique":true
                },
                {
                    "name":"drink",
                    "type":"string",
                    "description":"Name of the drink",
                    "optional":false
                },
                {
                    "name":"additions",
                    "type":"list(string)",
                    "description":"List of additions (flavors) to be included in the drink",
                    "optional":true
                },
                {
                    "name":"cost",
                    "type":"double",
                    "description":"Cost of the drink in USD",
                    "optional":false
                },
                {
                    "name":"next",
                    "type":"href",
                    "ref":"Order",
                    "description":"A URL pointing to the next resource in the workflow"
                }
            ],
            "description":"Describes an order submitted to the system."
        },
        {
            "name":"OrderRequest",
            "fields":[
                {
                    "name":"drink",
                    "type":"string",
                    "description":"Name of the drink to order",
                    "optional":false
                },
                {
                    "name":"additions",
                    "type":"list(string)",
                    "description":"A list of additions to be included in the drink",
                    "optional":true
                }
            ],
            "description":"Describes an order that can be submitted to the system by a client application."
        }
    ]
  }

This specification describes an API with two resources.

  * Order
  * AllOrders

The ``AllOrders`` resource can be used to submit orders (``submitOrder`` operation) and retrieve a list of all pending orders (``getAllOrders`` operation). The ``input`` section of the ``submitOrder`` operation indicates that the operation takes a JSON or XML payload and that payload should describe an ``OrderRequest`` object. The type ``OrderRequest`` is fully defined in the ``dataTypes`` section of the API specification. The ``output`` section of the ``submitOrder`` operation indicates that upon successful completion of the request, the API returns a ``HTTP 201 Created`` response with a JSON payload. This output JSON payload encodes an ``Order`` object, whose type is also defined in the ``dataTypes`` section. The ``output`` configuration of the ``submitOrder`` operation further specifies that the response from the API contains a HTTP ``Location`` header.

Now lets take a close look at a data type definition. ::

  {
    "name":"OrderRequest",
    "fields":[
      {
        "name":"drink",
        "type":"string",
        "description":"Name of the drink to order",
        "optional":false
      },
      {
        "name":"additions",
        "type":"list(string)",
        "description":"A list of additions to be included in the drink",
        "optional":true
      }
    ],
    "description":"Describes an order that can be submitted to the system by a client application."
  }

Above TypeDef element defines a complex type named ``OrderRequest``, which is the type of the input payload to the ``submitOrder`` operation. According to this type definition, an object of type ``OrderRequest`` contains two data fields. The ``drink`` field is a simple string field and is required. The ``additions`` field is a list of string values and is optional. Following JSON string specifies a payload that adheres to the above type definition. ::

  {
    "drink" : "Frapacinno",
    "additions" : [ "caramel", "whip cream" ]
  }

When serialized into XML the same object may look something like this. ::

  <OrderRequest>
    <drink>Frapacinno>
    <additions>caramel</additions>
    <additions>whip cream</additions>
  </OrderRequest>

The API description language also allows defines anonymous types inside operations, bindings and other data type definitions. ::

  {
    "name":"Foo",
    "fields":[
      {
        "name":"foo",
        "type": {
	  "fields" : [
	    {
	      "name":"bar",
	      "type":int
	    }
	  ]
        },
      }
    ]
  }

The input bindings are used to define operation input parameters that are extracted from non-payload elements of the HTTP request. For instance an operation may extract certain input data items from the HTTP header or URL of the request. As a more concrete example, take a look at the ``getOrder`` operation of the above ``Starbucks`` API specification. This operation extracts the ``orderId`` value from the request URL and therefore the ``orderId`` parameter has been defined as a reference to an externally defined input binding. Also note that several operations make use of the same URL based input parameters and therefore, defining this piece of information as an external input binding, makes it possible to share that definition across multiple operations.

The ``Starbucks`` API specification defines two base URLs for the API. When invoking a particular operation of the API, the URL path of the corresponding resource must be appended to these base URLs. For example if the ``getOrders`` operation is needed to be invoked, the URL fragment ``/{orderId}``, should be appended to one of the base URLs to construct the full URL of the request. Further note that ``/{orderId}`` itself is a URI template with the variable ``orderId``. This value should be filled in by the client during invocation time.

Validity of an API Description
------------------------------
An API description is valid if it satisfies the following conditions.

 * API has a name (has a ``name`` attribute)
 * API has at least one base URL (has a ``base`` attribute pointing to a non-empty array)
 * API has at least one resource (has a ``resources`` attribute pointing to a non-empty array)
 * Each resource has at least one operation (each ``resource`` element has an ``operations`` attribute pointing to a non-empty array)
 * Each operation has a HTTP method (each ``operation`` element has a ``method`` attribute)
 * There are no references to undefined types
 * There are no references to undefined input bindings

Note that the above conditions allow for many information (fields) to be left out from an API specification. For instance all the description fields, error fields and header fields can be left out. Also all the non-functional fields such as ``license``, ``community`` and ``tags`` can be left out from an API specification.
