from flask import Flask, request, render_template, Response, jsonify
from xml.etree import ElementTree as Et
from utils import validate_xml, clean_text, sanitize_xml, xml_to_json  # Importing new functions
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/process_xml', methods=['POST'])
def process_xml():
    # Proverka dali korisnikot ja prkachi datotekata
    xml_data = request.form.get("xml_data")
    xml_file = request.files.get("xml_file")

    if xml_file:
        try:
            # Read the XML file contents
            xml_data = xml_file.read().decode('utf-8')
        except Exception as e:
            return Response(f"<Error>Error reading file: {str(e)}</Error>", status=400, mimetype='application/xml')

    preprocess_option = request.form.get("preprocess_option")
    xpath_expressions = request.form.get("xpath_expression", "").splitlines()
    new_tag_name = request.form.get("new_tag_name")

    try:
        # Parsiranje na xml data
        root = Et.fromstring(xml_data)

        # Debug: Print na orginalnata xml
        print("Original XML Data:", xml_data)

        # Preprocesirachki opcii
        if preprocess_option == "strip_whitespace":
            xml_data = " ".join(xml_data.split())
        elif preprocess_option == "remove_tags":
            for xpath_expression in xpath_expressions:
                if ':' in xpath_expression:
                    prefix, tag_name = xpath_expression.split(':', 1)
                    namespaces = {prefix: 'http://schemas.xmlsoap.org/soap/envelope/'}  # Adjust to your namespace
                    for elem in root.findall(f".//{prefix}:{tag_name}", namespaces):
                        parent = root.find(f".//{prefix}:{tag_name}/..", namespaces)
                        if parent:
                            parent.remove(elem)
                else:
                    for elem in root.findall(xpath_expression):
                        parent = root.find(f".//{elem.tag}/..")
                        if parent:
                            parent.remove(elem)
            xml_data = Et.tostring(root, encoding='utf-8').decode('utf-8')
        elif preprocess_option == "extract_values":
            values = []
            for xpath_expression in xpath_expressions:
                if ':' in xpath_expression:
                    prefix, tag_name = xpath_expression.split(':', 1)
                    namespaces = {prefix: 'http://schemas.xmlsoap.org/soap/envelope/'}  # Adjust to your namespace
                    values.extend([elem.text for elem in root.findall(f".//{prefix}:{tag_name}", namespaces)])
                else:
                    values.extend([elem.text for elem in root.findall(xpath_expression)])
            xml_data = "\n".join(values)
        elif preprocess_option == "rename_tag":
            if new_tag_name:
                for xpath_expression in xpath_expressions:
                    if ':' in xpath_expression:
                        prefix, old_tag_name = xpath_expression.split(':', 1)
                        namespaces = {prefix: 'http://schemas.xmlsoap.org/soap/envelope/'}  # Adjust to your namespace
                        for elem in root.findall(f".//{prefix}:{old_tag_name}", namespaces):
                            elem.tag = f"{prefix}:{new_tag_name}"  # Rename with the same namespace prefix
                    else:
                        for elem in root.findall(xpath_expression):
                            elem.tag = new_tag_name
            xml_data = Et.tostring(root, encoding='utf-8').decode('utf-8')
        elif preprocess_option == "transform_to_text":
            response_data = []
            for elem in root.iter():
                if elem.text and elem.tag not in ['Envelope', 'Body']:  # Exclude Envelope and Body tags
                    response_data.append(f"{elem.tag}: {elem.text.strip()}")
            xml_data = "\n".join(response_data)

        # Debug: Print na procesiranata XML data
        print("Processed XML Data:", xml_data)

        response_data = f"<Response>{xml_data}</Response>"
        return Response(response_data, mimetype='application/xml')

    except Et.ParseError as e:
        return Response("<Error>Invalid XML format</Error>", status=400, mimetype='application/xml')
    except Exception as e:
        return Response(f"<Error>{str(e)}</Error>", status=500, mimetype='application/xml')


# New endpoint: Validiranje XML against XSD
@app.route('/validate_xml', methods=['POST'])
def validate_xml_endpoint():
    xml_data = request.form['xml_data']
    xsd_path = request.form.get('xsdPath')

    # Debugging: Print received XSD path
    print("Received XSD Path:", xsd_path)  # Check if xsdPath is received

    if not xsd_path:
        # Return JSON with "isValid" as False and a message explaining the error
        return jsonify({"isValid": False, "message": "XSD path is required for validation"}), 400

    is_valid, message = validate_xml(xml_data, xsd_path)
    return jsonify({"isValid": is_valid, "message": message})


# New endpoint: Convert XML to JSON
@app.route('/convert_to_json', methods=['POST'])
def convert_to_json_endpoint():
    xml_data = request.form['xml_data']
    json_data = xml_to_json(xml_data)

    # Check if conversion returned an error message
    if isinstance(json_data, str) and json_data.startswith("Conversion error"):
        return jsonify({"error": json_data}), 400

    return jsonify({"json": json_data})


# New endpoint: Clean and sanitize XML
@app.route('/clean_xml', methods=['POST'])
def clean_xml_endpoint():
    xml_data = request.form['xml_data']
    sanitized_data = sanitize_xml(xml_data)
    cleaned_data = clean_text(sanitized_data)
    return jsonify({"cleanedXml": cleaned_data})


if __name__ == '__main__':
    app.run(debug=True)
