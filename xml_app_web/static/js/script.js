document.getElementById("xmlForm").onsubmit = function(event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(this);

    fetch("/process_xml", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error("Error processing the XML data.");
        }
    })
    .then(data => {
        document.getElementById("responseContent").innerText = data;
        document.getElementById("response").style.display = "block"; // Show response div
    })
    .catch(error => {
        document.getElementById("responseContent").innerText = error.message;
        document.getElementById("response").style.display = "block"; // Show response div
    });
};

// Function: Validate XML
function validateXML() {
    const formData = new FormData(document.getElementById("xmlForm"));

    // Capture and log the XSD path value
    const xsdPath = document.getElementById("xsdPath").value;
    console.log("Retrieved XSD Path:", xsdPath);  // Debug log for XSD path

    if (xsdPath) {
        formData.append("xsdPath", xsdPath);
        console.log("Appended XSD Path to FormData:", formData.get("xsdPath"));  // Confirm it was added
    } else {
        alert("Please provide an XSD path for validation.");
        return;
    }

    // Check all FormData contents before sending
    for (let pair of formData.entries()) {
        console.log(pair[0]+ ': ' + pair[1]);
    }

    fetch("/validate_xml", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.isValid !== undefined && data.message) {
            if (data.isValid) {
                alert("XML is valid.");
            } else {
                alert(`Validation error: ${data.message}`);
            }
        } else {
            alert("Unexpected response structure from server.");
        }
    })
    .catch(error => alert("Error validating XML: " + error.message));
}


// Function: Convert XML to JSON
function convertToJson() {
    const formData = new FormData(document.getElementById("xmlForm"));

    fetch("/convert_to_json", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.json) {
            document.getElementById("responseContent").innerText = JSON.stringify(data.json, null, 2);
        } else if (data.error) {
            document.getElementById("responseContent").innerText = `Error: ${data.error}`;
        }
        document.getElementById("response").style.display = "block";
    })
    .catch(error => {
        document.getElementById("responseContent").innerText = "Unexpected response received from the server.";
        document.getElementById("response").style.display = "block";
    });
}

// Function: Clean and sanitize XML
function cleanXML() {
    const formData = new FormData(document.getElementById("xmlForm"));

    fetch("/clean_xml", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.cleanedXml) {
            document.getElementById("responseContent").innerText = data.cleanedXml;
        } else if (data.error) {
            document.getElementById("responseContent").innerText = `Error: ${data.error}`;
        }
        document.getElementById("response").style.display = "block";
    })
    .catch(error => {
        document.getElementById("responseContent").innerText = "Unexpected response received from the server.";
        document.getElementById("response").style.display = "block";
    });
}