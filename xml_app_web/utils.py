import xml.etree.ElementTree as Et
from xml import etree
import json
import re
import xmlschema


# New function: XML Schema Validation
# from lxml import etree  # Import lxml for advanced XML parsing

def parse_xml_request(xml_data):
    """
    Parse XML request and convert it into a dictionary.
    """
    try:
        root = Et.fromstring(xml_data)
        data = {}
        for child in root:
            data[child.tag] = child.text
        return data
    except Et.XMLSyntaxError:
        return None


def create_xml_response(data):
    """
    Create an XML response with a SOAP envelope and body.
    """
    envelope = Et.Element("soapenv:Envelope", xmlns="http://schemas.xmlsoap.org/soap/envelope/")
    body = Et.SubElement(envelope, "soapenv:Body")
    response = Et.SubElement(body, "Response")

    for key, value in data.items():
        element = Et.SubElement(response, key)
        element.text = value

    return Et.tostring(envelope, encoding='utf-8')


# Import lxml for advanced XML processing

def preprocess_xml(xml_data, xpath_expressions=None, rename_map=None):
    """
    Preprocess the XML by normalizing text and, if XPath expressions are provided,
    removing elements, renaming elements, or extracting elements that match the XPath.
    """
    try:
        # Parse XML and detect namespaces
        root = etree.fromstring(xml_data)
        namespaces = {k: v for k, v in root.nsmap.items() if k}  # Extract namespaces

        # Normalize text by stripping and converting to lowercase
        for elem in root.iter():
            if elem.text:
                elem.text = elem.text.strip().lower()
            if elem.tail:
                elem.tail = elem.tail.strip().lower()

        # Remove elements matching provided XPath expressions
        if xpath_expressions:
            for xpath in xpath_expressions:
                matches = root.xpath(xpath.strip(), namespaces=namespaces)
                for match in matches:
                    if isinstance(match, etree._Element):
                        parent = match.getparent()
                        if parent is not None:
                            parent.remove(match)

        # Rename elements based on the rename_map
        if rename_map:
            for xpath, new_tag in rename_map.items():
                matches = root.xpath(xpath.strip(), namespaces=namespaces)
                for match in matches:
                    if isinstance(match, etree._Element):
                        # Extract namespace from original tag and create new tag with it
                        ns_uri = etree.QName(match).namespace
                        if ns_uri:
                            new_tag = f"{{{ns_uri}}}{new_tag}"
                        match.tag = new_tag  # Rename the element

        # Return preprocessed XML as a string
        return etree.tostring(root, pretty_print=True, encoding='unicode').strip()

    except etree.XMLSyntaxError:
        return "<Error>Invalid XML for preprocessing</Error>"


def validate_xml(xml_data, xsd_path):
    try:
        schema = xmlschema.XMLSchema(xsd_path)
        schema.validate(xml_data)  # Validate XML
        return True, "XML is valid."
    except xmlschema.exceptions.XMLSchemaValidationError as e:
        return False, f"Schema validation error: {str(e)}"
    except Exception as e:
        return False, f"XML parsing error: {str(e)}"


# Function: Text Cleaning
def clean_text(text):
    """Cleans text data by removing stopwords and extra whitespace."""
    stopwords = {"a", "an", "the", "and", "or"}  # Add more as needed
    words = text.split()
    return ' '.join(word for word in words if word.lower() not in stopwords).strip()


# Function: XML Sanitization
def sanitize_xml(xml_data):
    """Sanitizes XML to prevent potential security vulnerabilities."""
    xml_data = re.sub(r'<script.*?>.*?</script>', '', xml_data, flags=re.DOTALL)
    return xml_data


# Function: XML to JSON Conversion
def xml_to_json(xml_data):
    """Converts XML data to JSON format."""
    try:
        xml_tree = Et.fromstring(xml_data)  # Parse XML with ElementTree
        return json.dumps(xml_to_dict(xml_tree))
    except Et.ParseError as e:
        return f"Conversion error: {str(e)}"


# Helper function for XML to JSON Conversion
def xml_to_dict(element):
    """Recursively converts XML elements to a dictionary."""
    return {
        element.tag: {
            child.tag: xml_to_dict(child) if len(child) > 0 else child.text
            for child in element
        }
    }
