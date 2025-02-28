import json
import requests

import sys
from json import loads as json_loads
from typing import TYPE_CHECKING

from defusedxml import ElementTree as SafeElementTree  # type:ignore[import-untyped]

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.model.bom import Bom
from cyclonedx.schema import OutputFormat, SchemaVersion
from cyclonedx.validation import make_schemabased_validator
from cyclonedx.validation.json import JsonStrictValidator


class DTModelAdapter():
    """
    A class implementing the adapter to translate different data models to the DT model and vice-versa.

    ...

    Attributes
    ----------
    __source_file : String
        a String defining...

    Methods
    -------
    translate(s, t, model)
        Method to...

    """


    def __init__(self):
        print("New DTModelAdapter instance created.")

    def send_to_controller1(self, payload):
        # print(payload)
        url = 'http://127.0.0.1:8005/api/create1/'
        try:
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            return r

            #session = requests.Session()
            #session.auth = ("ditto", "ditto")
            #r = session.post("http://10.0.1.174:8080/api/2/things/", json=payload, headers={'Content-Type': 'application/json'})

        except Exception as e:
            print(e)
        return

    def send_to_controller(self, payload):
        # print(payload)
        url = 'http://127.0.0.1:8005/api/create/'
        try:
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            return r

            #session = requests.Session()
            #session.auth = ("ditto", "ditto")
            #r = session.post("http://10.0.1.174:8080/api/2/things/", json=payload, headers={'Content-Type': 'application/json'})

        except Exception as e:
            print(e)
        return

    def from_clouditor(self, s):
        r = self.__from_clouditor(s)
        return r

    def to_clouditor(self, s):
        r = self.__to_clouditor(s)
        return r
    
    def from_cloud(self, s):
        r = self.__from_cloud(s)
        return r

    def __from_clouditor(self, s):
        translated=[]
        resource = "resource"
        attributes = [] #["id", "timestamp"]
        resource_attributes = ["@type", "id", "name", "creationTime", "labels", "internetAccessibleEndpoint", "raw"] #["@type", "creationTime", "internetAccessibleEndpoint", "labels", "name", "publicAccess","raw"]
        resource_excluded = []
        try:

            s_data = s
            '''
            with open(s, 'r') as json_data:
                s_data = json.loads(json_data.read())
                json_data.close()
            '''

            entry = {}
            #entry["thingId"] = "cobalt:" + s_data["id"]
            entry["policyId"] = "cobalt:policy"
            entry["definition"] = "cobalt:clouditor-resource:0.0.1"
            entry["attributes"] = {}
            for i in attributes:
                try:
                    entry["attributes"][i] = s_data[i]
                except Exception as e:
                    pass

            s_data = s_data[resource]
            for i in resource_attributes:
                try:
                    entry["attributes"][i] = s_data[i]
                except Exception as e:
                    pass

            entry["features"] = {}

            for i in s_data:
                if i not in resource_attributes:
                    if i not in resource_excluded:
                        try:
                            entry["features"][i] = {}
                            entry["features"][i]["properties"] = {}
                            if isinstance(s_data[i], dict):
                                entry["features"][i]["properties"] = {}
                                entry["features"][i]["properties"] = s_data[i]
                            else:
                                entry["features"][i]["properties"][i] = {}
                                entry["features"][i]["properties"][i] = s_data[i]
                        except Exception as e:
                            pass

            # t_json = json.dumps(entry)
            # with open('test.json', 'w', encoding='utf-8') as f:
            #    json.dump(entry,f,ensure_ascii=False, indent=4)

            # print(t_json)
            print(entry)
            translated.append(entry)
            return translated
        except Exception as e:
            print(e)

        # t_json = json.dumps(s_data["resource"])

        return None

    def __to_clouditor(self, s):
        resource = "resource"
        attributes = [] #["id", "timestamp"]
        resource_attributes = ["@type", "id", "name", "creationTime", "labels", "internetAccessibleEndpoint", "raw"] #["@type", "creationTime", "internetAccessibleEndpoint", "labels", "name", "publicAccess","raw"]
        resource_excluded = []
        try:

            s_data = s
            '''
            with open(s, 'r') as json_data:
                s_data = json.loads(json_data.read())
                json_data.close()
            '''

            entry = {}
            entry[s_data["definition"]] = []
            #entry[s_data["definition"]].append(s_data["attributes"])

            tmp = s_data["attributes"]

            tmp["properties"] = {}
            for i in s_data["features"]:
                tmp["properties"][i] = {}
                if i in s_data["features"][i]["properties"]:
                    tmp["properties"][i] = s_data["features"][i]["properties"][i]
                else:
                    tmp["properties"][i] = s_data["features"][i]["properties"]

            entry[s_data["definition"]].append(tmp)

            '''
            entry["definition"] = "cobalt:clouditor-resource:0.0.1"
            entry["attributes"] = {}
            for i in attributes:
                try:
                    entry["attributes"][i] = s_data[i]
                except Exception as e:
                    pass

            s_data = s_data[resource]
            for i in resource_attributes:
                try:
                    entry["attributes"][i] = s_data[i]
                except Exception as e:
                    pass

            entry["features"] = {}

            for i in s_data:
                if i not in resource_attributes:
                    if i not in resource_excluded:
                        try:
                            entry["features"][i] = {}
                            entry["features"][i]["properties"] = {}
                            if isinstance(s_data[i], dict):
                                entry["features"][i]["properties"] = {}
                                entry["features"][i]["properties"] = s_data[i]
                            else:
                                entry["features"][i]["properties"][i] = {}
                                entry["features"][i]["properties"][i] = s_data[i]
                        except Exception as e:
                            pass

            # t_json = json.dumps(entry)
            # with open('test.json', 'w', encoding='utf-8') as f:
            #    json.dump(entry,f,ensure_ascii=False, indent=4)
            '''
            # print(t_json)
            print(json.dumps(entry))
            #return json.dumps(entry)

        except Exception as e:
            print(e)

        # t_json = json.dumps(s_data["resource"])

        return None

    def __from_cloud(self, s):

        translated = []
        try:
            s_data = s
            for i in s_data:
                try:

                    n = -1
                    for j in s_data[i]:
                        n += 1

                        entry = {}
                        # entry["thingId"] = "cobalt:test"
                        entry["policyId"] = "cobalt:policy"
                        entry["definition"] = "cobalt:clouditor-resource:0.0.1"
                        entry["attributes"] = {}
                        entry["features"] = {}


                        #entry["features"][i]["properties"] = {}

                        for k in j:
                            if k != "properties":
                                entry["attributes"][k] = {}
                                entry["attributes"][k] = s_data[i][n][k]
                            else:
                                for l in s_data[i][n][k]:
                                    entry["features"][l] = {}
                                    entry["features"][l]["properties"] = {}
                                    if isinstance(s_data[i][n][k][l], dict):

                                        entry["features"][l]["properties"] = s_data[i][n][k][l]
                                    else:
                                        entry["features"][l]["properties"][l] = {}
                                        entry["features"][l]["properties"][l] = s_data[i][n][k][l]

                    '''
                    print(entry)
                    session = requests.Session()
                    session.auth = ("ditto", "ditto")
                    r = session.post("http://10.0.1.174:8080/api/2/things/", json=entry, headers={'Content-Type': 'application/json'})
                    print(r.json())
                    '''

                    translated.append(json.dumps(entry))

                except Exception as e:
                    print(e)

            return translated

        except Exception as e:
            print(e)

        # t_json = json.dumps(s_data["resource"])

        return None


    def from_CCM_cbom(self, cbom_content):
        """
        Transforms a CBOM (Cryptographic Bill of Materials) file into a new structure with attributes and components.

        Args:
            cbom_content (dict): The parsed JSON content of the CBOM file.

        Returns:
            dict: A dictionary representing the transformed CBOM.
        """
        # Extract metadata and components
        metadata = cbom_content.get("metadata", {})
        components = cbom_content.get("components", [])

        # Create the attributes section from metadata
        attributes = {
            "bomFormat": cbom_content.get("bomFormat"),
            "specVersion": cbom_content.get("specVersion"),
            "serialNumber": cbom_content.get("serialNumber"),
            "version": cbom_content.get("version"),
            "timestamp": metadata.get("timestamp"),
            "component": metadata.get("component", {}).get("name"),
            "version": metadata.get("component", {}).get("version")
        }

        # Rename components to features
        features = {}
        for component in components:
            name = component.get("name")
            properties = component.get("cryptoProperties")
            features[name] = {
                "properties": properties
            }

        # Create the new structure
        transformed_cbom = {
            "policyId" : "cobalt:policy",
            "definition": "cobalt:clouditor-resource:0.0.1",
            "attributes": attributes,
            "features": features
        }

        return transformed_cbom

    def from_CCM_sbom(self, sbom_content):
        """
        Transforms an SBOM (Software Bill of Materials) file into a new structure with attributes and components.

        Args:
            sbom_content (dict): The parsed JSON content of the SBOM file.

        Returns:
            dict: A dictionary representing the transformed SBOM.
        """
        # Create the features section from Components, metadata and Dependencies
        features = {
            "sbom_metadata": {"properties": sbom_content.get("metadata", {})},
            "sbom_components": {"properties": {"components": sbom_content.get("components", [])}},
            "sbom_dependencies": {"properties": {"dependencies": sbom_content.get("dependencies", [])}}
        }

        # Create the attributes section
        attributes = {
            "serialNumber": sbom_content.get("serialNumber", ""),
            "version": sbom_content.get("version", ""),
            "bomFormat": sbom_content.get("bomFormat", ""),
            "specVersion": sbom_content.get("specVersion", ""),
            "schema": sbom_content.get("$schema", "")
        }
        
        # Create the new structure
        transformed_sbom = {
            "policyId" : "cobalt:policy",
            "definition" : "cobalt:clouditor-resource:0.0.1",
            "attributes": attributes,
            "features": features,
   
        }

        return transformed_sbom



def validate_cyclone(cyclone_content):
    """
    Validates a CycloneDX payload.

    Args:
        cyclone_content (dict): The parsed JSON content of the CycloneDX payload.

    Returns:
        bool: True if the payload is valid, False otherwise.
    """
    # Check if the payload has the required fields
    if "bomFormat" in cyclone_content and "specVersion" in cyclone_content and "serialNumber" in cyclone_content:
        return True


    my_json_validator = JsonStrictValidator(SchemaVersion.V1_4)
    try:
        json_data = json.dumps(cyclone_content)
        validation_errors = my_json_validator.validate_str(json_data)
        if validation_errors:
            print('JSON invalid', 'ValidationError:', repr(validation_errors), sep='\n', file=sys.stderr)
            sys.exit(2)
        print('JSON valid')
    except MissingOptionalDependencyException as error:
        print('JSON-validation was skipped due to', error)
    bom_from_json = Bom.from_json(json_loads(json_data))
    print('bom_from_json', repr(bom_from_json))

    return False


def from_cyclone(cyclone_json, name):
    """
    Transforms a CycloneDX payload (JSON string) conforming to the 1.6 schema from any BOM type 
    (CBOM, SBOM, SaaSBOM, VEX, VDR, HBOM, etc.) into a unified structure with attributes and features,
    including every detail present in the input.
    
    Args:
        cyclone_json (str): The JSON string of the CycloneDX BOM.
    
    Returns:
        str: A JSON string representing the transformed CycloneDX BOM in a standardized format with full details.
    """
    # Parse the JSON input
    cyclone_content = json.loads(cyclone_json)
    
    # Extract core BOM fields
    bom_format = cyclone_content.get("bomFormat", "CycloneDX")
    spec_version = cyclone_content.get("specVersion", "1.6")
    serial_number = cyclone_content.get("serialNumber")
    bom_type = detect_bom_type(cyclone_content)
    # Extract metadata (if available) and its component information
    metadata = cyclone_content.get("metadata", {})
    
    convert_serial_number = convert_urn(serial_number)

    # Set up the attributes section based on CycloneDX 1.6, including full metadata
    attributes = {
        "bomFormat": bom_format,
        "specVersion": spec_version,
        "serialNumber": serial_number,
        # "metadata": metadata,
        "BomType": bom_type
    }
    
    # Initialize features dictionary
    features = {}

    # Process metadata
    if metadata:
        features["metadata"] = {
            "properties": metadata
        }
    
    components = cyclone_content.get("components", [])
    if components:
        features["components"] = {
            "properties": {"components": components}
        }
    
    dependencies = cyclone_content.get("dependencies", [])
    if dependencies:
        features["dependencies"] = {
            "properties": {"dependencies": dependencies}
        }
    
    services = cyclone_content.get("services", [])
    if services:
        features["services"] = {
            "properties": {"services": services}
        }

    compositions = cyclone_content.get("compositions", [])
    if compositions:
        features["compositions"] = {
            "properties": {"compositions": compositions}
        }

    vulnerabilities = cyclone_content.get("vulnerabilities", [])
    if vulnerabilities:
        features["vulnerabilities"] = {
            "properties": {"vulnerabilities": vulnerabilities}
        }

    formulations = cyclone_content.get("formulations", [])
    if formulations:
        features["formulations"] = {
            "properties": {"formulations":formulations}
        }

    annotations = cyclone_content.get("annotations", [])
    if annotations:
        features["annotations"] = {
            "properties": {"annotations": annotations}
        }

    definitions = cyclone_content.get("definitions", [])
    if definitions:
        features["definitions"] = {
            "properties": {"definitions": definitions}
        }

    declarations = cyclone_content.get("declarations", [])
    if declarations:
        features["declarations"] = {
            "properties": {"declarations": declarations}
        }

    extensions = cyclone_content.get("extensions", [])
    if extensions:
        features["extensions"] = {
            "properties": {"extensions": extensions}
        }
    
    # Create the unified structure, including the full raw input for reference
    transformed_cyclone = {
        "thingId": "TOE." + (name or "none") + "." + (bom_type or "bom") + "." + (convert_serial_number or "urn"),
        "policyId" : "cobalt:policy",
        "attributes": attributes,
        "features": features,
        "_metadata": cyclone_content
    }
    
    # Return the transformed structure as a JSON string
    return transformed_cyclone, convert_serial_number , bom_type


def detect_bom_type(cyclone_content):
    """
    Detects the BOM type from the CycloneDX content.

    Args:
        cyclone_content (dict): The parsed JSON content of the CycloneDX payload.

    Returns:
        str: The detected BOM type.
    """
    if "components" in cyclone_content:
        components = cyclone_content.get("components", [])
        for component in components:
            if component.get("type") == "cryptographic-asset":
                if component.get("cryptoProperties", {}).get("assetType") == "algorithm":
                    n="cbom.algorithm"
                    if "dependencies" in cyclone_content:
                        return n + ".dependencies"
                    else:
                        return n
                elif component.get("cryptoProperties", {}).get("assetType") == "certificate":
                    n = "cbom.certificate"
                    if "dependencies" in cyclone_content:
                        return n + ".dependencies"
                    else:
                        return n
            elif component.get("type") == "library":
                return "sbom"
            elif component.get("type") == "device":
                return "hbom"
    elif "dependencies" in cyclone_content and "services" in cyclone_content:
        return "saasbom"
    elif "vulnerabilities" in cyclone_content:
        return "vex"
    else:
        return "boms"

def convert_urn(input_str):
    parts = input_str.split(":", 2)  # Split into max 3 parts
    if len(parts) == 3:
        return f"{parts[0]}.{parts[1]}:{parts[2]}"
    return input_str  # Return original if format is unexpected


def to_cyclone(cyclone_content):
    """
    Transforms a new structure with attributes and components into a CycloneDX payload.

    Args:
        cyclone_content (dict): A dictionary representing the transformed CycloneDX payload.

    Returns:
        dict: The parsed JSON content of the CycloneDX payload.
    """
    # Extract attributes and features
    attributes = cyclone_content.get("attributes", {})
    features = cyclone_content.get("features", {})

    # Create the metadata section
    metadata = {
        "version": attributes.get("version"),
        "timestamp": attributes.get("timestamp"),
        "component": {
            "name": attributes.get("component"),
            "version": attributes.get("version")
        }
    }

    # Rename features to components
    components = []
    for name, feature in features.items():
        component = {
            "name": name,
            "properties": feature.get("properties")
        }
        components.append(component)

    # Create the new structure
    transformed_cyclone = {
        "bomFormat": attributes.get("bomFormat"),
        "specVersion": attributes.get("specVersion"),
        "serialNumber": attributes.get("serialNumber"),
        "metadata": metadata,
        "components": components
    }

    return transformed_cyclone
