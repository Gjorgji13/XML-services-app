import unittest
import re  # Import the re module for regular expressions
import os
import json
from app import app  # Import the Flask app
from io import BytesIO
import xml.etree.ElementTree as Et  # For XML normalization


class XMLProcessingTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_process_xml_strip_whitespace(self):
        response = self.client.post('/process_xml', data={
            'xml_data': '<root>\n    <child>Text</child>\n</root>',
            'preprocess_option': 'strip_whitespace'
        })
        self.assertEqual(response.status_code, 200)

        # Use regex to ignore whitespace differences around tags
        expected_pattern = re.compile(r"<Response><root><child>Text</child></root></Response>")
        self.assertRegex(response.data.decode('utf-8').replace(" ", ""), expected_pattern.pattern)

    def test_process_xml_remove_tags(self):
        response = self.client.post('/process_xml', data={
            'xml_data': '<root><remove>Text</remove><keep>Keep</keep></root>',
            'preprocess_option': 'remove_tags',
            'xpath_expression': './/remove'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<Response><root><keep>Keep</keep></root></Response>', response.data)

    def test_process_xml_extract_values(self):
        response = self.client.post('/process_xml', data={
            'xml_data': '<root><value>Extract Me</value><value>And Me</value></root>',
            'preprocess_option': 'extract_values',
            'xpath_expression': './/value'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Extract Me\nAnd Me', response.data)

    def test_process_xml_rename_tag(self):
        response = self.client.post('/process_xml', data={
            'xml_data': '<root><oldtag>Text</oldtag></root>',
            'preprocess_option': 'rename_tag',
            'xpath_expression': './/oldtag',
            'new_tag_name': 'newtag'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<Response><root><newtag>Text</newtag></root></Response>', response.data)

    def test_validate_xml(self):
        xsd_content = '''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                            <xs:element name="root">
                                <xs:complexType>
                                    <xs:sequence>
                                        <xs:element name="child" type="xs:string"/>
                                    </xs:sequence>
                                </xs:complexType>
                            </xs:element>
                         </xs:schema>'''
        with open("schema.xsd", "w") as f:
            f.write(xsd_content)

        response = self.client.post('/validate_xml', data={
            'xml_data': '<root><child>Content</child></root>',
            'xsdPath': 'schema.xsd'
        })
        self.assertEqual(response.status_code, 200)

        # Parse response JSON and check for "isValid" and "message" fields
        data = json.loads(response.data)
        self.assertTrue(data["isValid"])
        self.assertEqual(data["message"], "XML is valid.")

    def test_convert_to_json(self):
        response = self.client.post('/convert_to_json', data={
            'xml_data': '<root><child>Text</child></root>'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"json":"{\\"root\\": {\\"child\\": \\"Text\\"}}"', response.data)

    def test_clean_xml(self):
        response = self.client.post('/clean_xml', data={
            'xml_data': '<root><child>Some <script>malicious</script> content</child></root>'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"cleanedXml":"<root><child>Some content</child></root>"', response.data)

    def tearDown(self):
        if os.path.exists("schema.xsd"):
            os.remove("schema.xsd")


if __name__ == '__main__':
    unittest.main()
