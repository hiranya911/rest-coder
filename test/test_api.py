#!/usr/bin/python

import os
import unittest
import sys

sys.path.append('../python-lib')
from api import parse, APIDescriptionException

class TestAPIDescriptionParser(unittest.TestCase):

  def load_api_description(self, name):
    path = os.path.join('../samples', name)
    return parse(path)

  def test_simple1(self):
    """
    Test for basic attributes - mainly name, base and resources
    """
    api = self.load_api_description('simple1.json')
    self.assertEqual(api.name, 'Starbucks')
    self.assertEqual(len(api.resources), 1)

    resource = api.resources[0]
    self.assertEqual(resource.name, 'AllOrders')
    self.assertEqual(resource.path, '/')
    self.assertEqual(len(resource.operations), 1)

    operation = resource.operations[0]
    self.assertEqual(operation.method, 'GET')
    self.assertIsNone(operation.input)
    output = operation.output
    self.assertEqual(output.status, 200)
    self.assertEqual(output.type.type.get_reference_name(), 'list(string)')
    self.assertEqual(len(output.contentType), 1)
    self.assertEqual(output.contentType[0], 'json')

    self.assertEqual(len(api.base), 1)
    self.assertEqual(api.base[0], 'http://test.com/starbucks')

  def test_simple2(self):
    """
    Test for multiple operations in the same resource and named data type
    definitions.
    """
    api = self.load_api_description('simple2.json')
    self.assertEqual(api.name, 'Starbucks')
    self.assertEqual(len(api.resources), 1)

    resource = api.resources[0]
    self.assertEqual(resource.name, 'AllOrders')
    self.assertEqual(resource.path, '/')
    self.assertEqual(len(resource.operations), 2)

    operation = resource.operations[0]
    self.assertEqual(operation.method, 'GET')
    self.assertIsNone(operation.input)
    output = operation.output
    self.assertEqual(output.status, 200)
    self.assertEqual(output.type.type.get_reference_name(), 'list(Order)')
    self.assertEqual(len(output.contentType), 1)
    self.assertEqual(output.contentType[0], 'json')

    operation = resource.operations[1]
    self.assertEqual(operation.method, 'POST')
    input = operation.input
    self.assertEqual(input.type.type.get_reference_name(), 'OrderRequest')
    self.assertEqual(input.contentType[0], 'json')
    output = operation.output
    self.assertEqual(output.status, 201)
    self.assertEqual(output.type.type.get_reference_name(), 'Order')
    self.assertEqual(len(output.contentType), 1)
    self.assertEqual(output.contentType[0], 'json')

    self.assertEqual(len(api.base), 1)
    self.assertEqual(api.base[0], 'http://test.com/starbucks')

    self.assertEqual(len(api.data_types), 2)
    self.assertEqual(len(api.data_types[0].fields), 5)
    self.assertEqual(len(api.data_types[1].fields), 2)
    self.assertFalse(api.data_types[1].fields[0].optional)
    self.assertTrue(api.data_types[1].fields[1].optional)

  def test_simple3(self):
    """
    Test for multiple resources, multiple base URLs, detailed input/output
    definitions and errors.
    """
    api = self.load_api_description('simple3.json')
    self.assertEqual(api.name, 'Starbucks')
    self.assertEqual(len(api.resources), 2)

    resource = api.resources[1]
    self.assertEqual(resource.name, 'AllOrders')
    self.assertEqual(resource.path, '/')
    self.assertEqual(len(resource.operations), 2)

    operation = resource.operations[0]
    self.assertEqual(operation.method, 'GET')
    self.assertIsNone(operation.input)
    output = operation.output
    self.assertEqual(output.status, 200)
    self.assertEqual(output.type.type.get_reference_name(), 'list(Order)')
    self.assertEqual(len(output.contentType), 1)
    self.assertEqual(output.contentType[0], 'json')

    operation = resource.operations[1]
    self.assertEqual(operation.method, 'POST')
    input = operation.input
    self.assertEqual(input.type.type.get_reference_name(), 'OrderRequest')
    self.assertEqual(input.contentType[0], 'json')
    output = operation.output
    self.assertEqual(output.status, 201)
    self.assertEqual(output.type.type.get_reference_name(), 'Order')
    self.assertEqual(len(output.contentType), 1)
    self.assertEqual(output.contentType[0], 'json')

    self.assertEqual(len(api.base), 2)
    self.assertEqual(api.base[0], 'http://test.com/starbucks')
    self.assertEqual(api.base[1], 'https://test.com/starbucks')

    self.assertEqual(len(api.data_types), 4)
    self.assertEqual(len(api.data_types[0].fields), 5)
    self.assertEqual(len(api.data_types[1].fields), 2)
    self.assertFalse(api.data_types[1].fields[0].optional)
    self.assertTrue(api.data_types[1].fields[1].optional)

    operation = api.resources[0].operations[0]
    self.assertEqual(len(operation.errors), 2)

  def test_simple4(self):
    """
    Test for named input binding definitions and binding references in
    operation input definitions. Also checks for header definitions in the
    output section.
    """
    api = self.load_api_description('simple4.json')
    self.assertEqual(api.name, 'Starbucks')
    self.assertEqual(len(api.resources), 2)

    resource = api.resources[1]
    self.assertEqual(resource.name, 'AllOrders')
    self.assertEqual(resource.path, '/')
    self.assertEqual(len(resource.operations), 2)

    operation = resource.operations[0]
    self.assertEqual(operation.method, 'GET')
    self.assertIsNone(operation.input)
    output = operation.output
    self.assertEqual(output.status, 200)
    self.assertEqual(output.type.type.get_reference_name(), 'list(Order)')
    self.assertEqual(len(output.contentType), 1)
    self.assertEqual(output.contentType[0], 'json')

    operation = resource.operations[1]
    self.assertEqual(operation.method, 'POST')
    input = operation.input
    self.assertEqual(input.type.type.get_reference_name(), 'OrderRequest')
    self.assertEqual(input.contentType[0], 'json')
    output = operation.output
    self.assertEqual(output.status, 201)
    self.assertEqual(output.type.type.get_reference_name(), 'Order')
    self.assertEqual(len(output.contentType), 1)
    self.assertEqual(output.contentType[0], 'json')
    self.assertEqual(len(output.headers), 1)
    header = output.headers[0]
    self.assertEqual(header.name, 'Location')
    self.assertEqual(header.type.type.get_reference_name(), 'href')
    self.assertEqual(header.type.ref, 'Order')

    self.assertEqual(len(api.base), 1)
    self.assertEqual(api.base[0], 'http://test.com/starbucks')

    self.assertEqual(len(api.data_types), 2)
    self.assertEqual(len(api.data_types[0].fields), 5)
    self.assertEqual(len(api.data_types[1].fields), 2)
    self.assertFalse(api.data_types[1].fields[0].optional)
    self.assertTrue(api.data_types[1].fields[1].optional)

    resource = api.resources[0]
    self.assertEqual(len(resource.input_bindings), 1)
    self.assertEqual(resource.input_bindings[0].id, 'orderIdBinding')
    self.assertEqual(len(resource.operations), 2)
    self.assertEqual(resource.operations[0].input.params[0].binding, 'orderIdBinding')
    self.assertEqual(resource.operations[1].input.params[0].binding, 'orderIdBinding')

  def test_simple5(self):
    """
    Test for non functional attributes - license, community, ownership,
    sla etc
    """
    api = self.load_api_description('simple5.json')
    self.assertEqual(api.name, 'Starbucks')
    self.assertEqual(api.license, 'apache2')
    self.assertEqual(api.community, 'http://community.test.com')

    self.assertEqual(len(api.ownership), 2)
    self.assertEqual(api.ownership[0].name, 'Peter Parker')
    self.assertEqual(api.ownership[1].name, 'Bruce Wayne')
    self.assertEqual(api.ownership[1].email, 'bat@jleague.com')
    self.assertEqual(api.ownership[1].ownerType, 'tech')
    self.assertEqual(len(api.sla), 3)

    sla = api.sla[2]
    self.assertEqual(sla.name, 'GOLD')
    self.assertEqual(sla.availability, 99.9)
    self.assertEqual(sla.rateLimit, 1000)
    self.assertEqual(sla.timeUnit, 'second')
    cost = sla.costModel
    self.assertEqual(cost.currency, 'USD')
    self.assertEqual(cost.unitPrice, 0.1)
    self.assertEqual(cost.requestsPerUnit, 1000)

    sla = api.sla[0]
    self.assertEqual(sla.name, 'FREE')
    self.assertIsNone(sla.costModel)

  def test_simple6(self):
    """
    Test for anonymous bindings, anonymous types and nested type definitions.
    """
    api = self.load_api_description('simple6.json')
    self.assertEqual(api.name, 'Starbucks')
    self.assertEqual(len(api.resources), 2)

    resource = api.resources[1]
    self.assertEqual(resource.name, 'AllOrders')
    self.assertEqual(resource.path, '/')
    self.assertEqual(len(resource.operations), 2)

    operation = resource.operations[0]
    self.assertEqual(operation.method, 'GET')
    self.assertIsNone(operation.input)
    output = operation.output
    self.assertEqual(output.status, 200)
    self.assertEqual(output.type.type.get_reference_name(), 'list(Order)')
    self.assertEqual(len(output.contentType), 1)
    self.assertEqual(output.contentType[0], 'json')

    operation = resource.operations[1]
    self.assertEqual(operation.method, 'POST')
    input = operation.input
    self.assertEqual(len(input.type.type.fields), 2)
    self.assertEqual(input.contentType[0], 'json')
    output = operation.output
    self.assertEqual(output.status, 201)
    self.assertEqual(output.type.type.get_reference_name(), 'Order')
    self.assertEqual(len(output.contentType), 1)
    self.assertEqual(output.contentType[0], 'json')

    self.assertEqual(len(api.base), 1)
    self.assertEqual(api.base[0], 'http://test.com/starbucks')

    self.assertEqual(len(api.data_types), 2)
    self.assertEqual(len(api.data_types[0].fields), 5)
    self.assertEqual(len(api.data_types[1].fields), 2)
    nested = api.data_types[1]
    field = nested.fields[1]
    self.assertEqual(len(field.type.type.fields), 1)

    resource = api.resources[0]
    self.assertEqual(len(resource.input_bindings), 1)
    self.assertEqual(resource.input_bindings[0].id, 'orderIdBinding')
    self.assertEqual(len(resource.operations), 2)
    binding = resource.operations[0].input.params[0].binding
    self.assertEqual(binding.mode, 'url')
    self.assertEqual(binding.name, 'orderId')
    self.assertEqual(binding.type.type.get_reference_name(), 'string')
    self.assertEqual(resource.operations[1].input.params[0].binding, 'orderIdBinding')

  def test_error1(self):
    """
    Test for undefined type references
    """
    try:
      api = self.load_api_description('error1.json')
      self.fail('No error thrown for undefined type')
    except APIDescriptionException:
      pass

  def test_error2(self):
    """
    Test for undefined input bindings
    """
    try:
      api = self.load_api_description('error2.json')
      self.fail('No error thrown for undefined binding')
    except APIDescriptionException:
      pass

  def test_error3(self):
    """
    Test for undefined input segment
    """
    try:
      api = self.load_api_description('error3.json')
      self.fail('No error thrown for undefined input segment')
    except APIDescriptionException:
      pass

if __name__ == '__main__':
    unittest.main()

