import unittest

import schema
from exceptions import ResourceNotDefined


class TestCreateDocument(unittest.TestCase):
    def test_create_document(self):

        document = {
            'id': 1,
        }
        self.assertRaises(AssertionError, schema.create_document, document)

        document = {
            'resourceType': 'MockModel01'
        }
        self.assertRaises(AssertionError, schema.create_document, document)

        document = {
            'id': 1,
            'resourceType': 'MockModelDontExists'
        }
        self.assertRaises(ResourceNotDefined, schema.create_document, document)

        document = {
            'id': 1,
            'resourceType': 'MockModel01'
        }
        doc = schema.create_document(document)

        self.assertEqual(type(doc), MockModel01)
        self.assertEqual(doc.id, 1)
        self.assertDictEqual(doc.data, document)

        document = {
            'id': '12345-QWERTY',
            'resourceType': 'MockModel01'
        }
        doc = schema.create_document(document)
        self.assertEqual(doc.id, document['id'])

    def test_search_documents(self):
        doc01 = schema.create_document({
            'id': 'aaa01',
            'resourceType': 'MockSearchModel01',
            'name': [{
                'given': ['Zoe', 'Zebra'],
                'family': 'Aberi'
            }]
        })

        doc02 = schema.create_document({
            'id': 'aaa02',
            'resourceType': 'MockSearchModel02',
            'name': [{
                'given': ['Zoe', 'Zebra'],
                'family': 'Aber'
            }]
        })

        doc03 = schema.create_document({
            'id': 'aai03',
            'resourceType': 'MockSearchModel01',
            'name': [{
                'given': ['Yoe', 'Yebra'],
                'family': 'Aber'
            }]
        })

        doc04 = schema.create_document({
            'id': 4,
            'resourceType': 'MockSearchModel01',
            'name': [{
                'given': ['louis'],
                'family': 'Hache'
            }]
        })

        results = MockSearchModel01.find('z')
        self.assertEqual(len(list(results)), 1)

        results = MockSearchModel01.find('zoe aber')
        self.assertEqual(len(list(results)), 1)

        results = MockSearchModel01.find(['zoe', 'aber'])
        results = list(results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], doc01)

        results = MockSearchModel01.find(3)
        results = list(results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], doc03)

        results = MockSearchModel01.find([3, 'aber'])
        results = list(results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], doc03)

        results = MockSearchModel01.find('ABER')
        self.assertEqual(len(list(results)), 2)

        results = MockSearchModel01.find('aber')
        self.assertEqual(len(list(results)), 2)

        results = MockSearchModel01.find('zebra yebra')
        self.assertEqual(len(list(results)), 0)

        result = MockSearchModel01.get('AAI03')
        self.assertEqual(result, doc03)

        result = MockSearchModel01.get('4')
        self.assertEqual(result, doc04)

        result = MockSearchModel01.get(4)
        self.assertEqual(result, doc04)

        results = MockSearchModel01.find('AAI03')
        self.assertEqual(list(results), [doc03])

        results = MockSearchModel02.find('zoe')
        results = list(results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], doc02)

    def test_references(self):

        parent = schema.create_document({
            'id': 101,
            'resourceType': 'MockReferenceParent',
            'patient': {'reference': 'MockReferencePatient/102'},
            'careteam': [
                {'reference': 'MockReferenceCareTeam/103'},
                {'reference': 'MockReferenceCareTeam/104'}
            ]
        })

        patient = schema.create_document({
            'id': 102,
            'resourceType': 'MockReferencePatient',
            'document': {'reference': 'MockReferenceDocument/105'}
        })

        careteam01 = schema.create_document({
            'id': 103,
            'resourceType': 'MockReferenceCareTeam'
        })

        careteam02 = schema.create_document({
            'id': 104,
            'resourceType': 'MockReferenceCareTeam'
        })

        document = schema.create_document({
            'id': 105,
            'resourceType': 'MockReferenceDocument',
        })

        parent_references = {
            'MockReferencePatient': {patient},
            'MockReferenceCareTeam': {careteam01, careteam02},
            'MockReferenceDocument': {document}
        }
        references = parent.get_connections()
        self.assertDictEqual(references, parent_references)

        patient_references = {
            'MockReferenceParent': {parent},
            'MockReferenceCareTeam': {careteam01, careteam02},
            'MockReferenceDocument': {document}
        }
        references = patient.get_connections()
        self.assertDictEqual(references, patient_references)


class MockModel01(schema.BaseModel):
    pass


class MockSearchModel01(schema.BaseModel):
    index = ['name.given', 'name.family', 'address.street.name']


class MockSearchModel02(schema.BaseModel):
    index = ['name.given', 'name.family', 'address.street.name']


class MockReferenceParent(schema.BaseModel):
    references = ['patient', 'careteam']


class MockReferencePatient(schema.BaseModel):
    references = ['document']


class MockReferenceCareTeam(schema.BaseModel):
    pass


class MockReferenceDocument(schema.BaseModel):
    pass


if __name__ == '__main__':
    unittest.main()
