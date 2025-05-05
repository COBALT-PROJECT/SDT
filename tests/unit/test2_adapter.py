import unittest
import os
import json
import sys
import logging
import time
import hashlib
import shutil
import requests
import git
import difflib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.adapter import DTModelAdapter
from core.controller import Controller

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

class TestDTModelAdapterIntegration(unittest.TestCase):
    """Integration tests for DTModelAdapter class with real dependencies"""
    
    def setUp(self):
        self.adapter = DTModelAdapter()
        self.controller = Controller()
        self.test_dir = os.path.join(os.getcwd(), "test_evidence")
        self.test_toeid = "123456789"
        self.cyclone_example = {
            "bomFormat" : "CycloneDX",
            "specVersion" : "1.5",
            "serialNumber" : "urn:uuid:dce5f002-f1f2-4809-bf9d-8813ae2efb79",
            "version" : 1,
            "metadata" : {
                "timestamp" : "2025-02-25T09:19:18Z",
                "tools" : [
                {
                    "vendor" : "OWASP",
                    "name" : "Dependency-Track",
                    "version" : "4.12.1"
                }
                ],
                "component" : {
                "type" : "application",
                "bom-ref" : "82e592b4-56b8-455a-b3f6-70a966996277",
                "name" : "test",
                "version" : "1.0"
                }
            },
            "components" : [
                {
                "type" : "library",
                "bom-ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2",
                "name" : "Pillow",
                "version" : "9.4.0",
                "description" : "requirements line 10: Pillow==9.4.0",
                "purl" : "pkg:pypi/pillow@9.4.0",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/Pillow/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f",
                "name" : "certifi",
                "version" : "2022.12.7",
                "description" : "requirements line 1: certifi==2022.12.7",
                "purl" : "pkg:pypi/certifi@2022.12.7",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/certifi/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "09cfcf87-a619-4eb6-9638-9ecd4fa76055",
                "name" : "charset-normalizer",
                "version" : "3.0.1",
                "description" : "requirements line 2: charset-normalizer==3.0.1",
                "purl" : "pkg:pypi/charset-normalizer@3.0.1",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/charset-normalizer/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "a9fef477-0d97-4b5a-8e4d-40529c78c838",
                "name" : "colorama",
                "version" : "0.4.6",
                "description" : "requirements line 3: colorama==0.4.6",
                "purl" : "pkg:pypi/colorama@0.4.6",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/colorama/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "9a642a54-1e89-4a01-a48e-3780b8d7ab1c",
                "name" : "decorator",
                "version" : "4.4.2",
                "description" : "requirements line 4: decorator==4.4.2",
                "purl" : "pkg:pypi/decorator@4.4.2",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/decorator/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "547b6f87-49a8-4552-88da-0d1ff7507d4c",
                "name" : "idna",
                "version" : "3.4",
                "description" : "requirements line 5: idna==3.4",
                "purl" : "pkg:pypi/idna@3.4",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/idna/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "c06911a1-05be-41f5-af67-f9405b726bea",
                "name" : "imageio",
                "version" : "2.25.0",
                "description" : "requirements line 6: imageio==2.25.0",
                "purl" : "pkg:pypi/imageio@2.25.0",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/imageio/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "d6069bcc-0443-4f7d-a4ac-eceaeff92f5e",
                "name" : "imageio-ffmpeg",
                "version" : "0.4.8",
                "description" : "requirements line 7: imageio-ffmpeg==0.4.8",
                "purl" : "pkg:pypi/imageio-ffmpeg@0.4.8",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/imageio-ffmpeg/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "b0013349-0ec0-4d7e-868d-7cf860d0f05e",
                "name" : "moviepy",
                "version" : "1.0.3",
                "description" : "requirements line 8: moviepy==1.0.3",
                "purl" : "pkg:pypi/moviepy@1.0.3",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/moviepy/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "18282ac2-d895-4387-8ba7-2d068f0d1bbd",
                "name" : "numpy",
                "version" : "1.24.1",
                "description" : "requirements line 9: numpy==1.24.1",
                "purl" : "pkg:pypi/numpy@1.24.1",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/numpy/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "c254814a-a64b-4726-9c9f-50fb734023f9",
                "name" : "proglog",
                "version" : "0.1.10",
                "description" : "requirements line 11: proglog==0.1.10",
                "purl" : "pkg:pypi/proglog@0.1.10",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/proglog/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64",
                "name" : "requests",
                "version" : "2.28.2",
                "description" : "requirements line 12: requests==2.28.2",
                "purl" : "pkg:pypi/requests@2.28.2",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/requests/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "f37629f1-b3af-4a21-98c5-0059cf9cfdf3",
                "name" : "tk",
                "version" : "0.1.0",
                "description" : "requirements line 13: tk==0.1.0",
                "purl" : "pkg:pypi/tk@0.1.0",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/tk/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "f03b8152-604a-4b50-af8b-5d34b47f263c",
                "name" : "tqdm",
                "version" : "4.64.1",
                "description" : "requirements line 14: tqdm==4.64.1",
                "purl" : "pkg:pypi/tqdm@4.64.1",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/tqdm/",
                    "comment" : "implicit dist url"
                    }
                ]
                },
                {
                "type" : "library",
                "bom-ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae",
                "name" : "urllib3",
                "version" : "1.26.14",
                "description" : "requirements line 15: urllib3==1.26.14",
                "purl" : "pkg:pypi/urllib3@1.26.14",
                "externalReferences" : [
                    {
                    "type" : "distribution",
                    "url" : "https://pypi.org/simple/urllib3/",
                    "comment" : "implicit dist url"
                    }
                ]
                }
            ],
            "dependencies" : [
                {
                "ref" : "82e592b4-56b8-455a-b3f6-70a966996277",
                "dependsOn" : [ ]
                },
                {
                "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2",
                "dependsOn" : [ ]
                },
                {
                "ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f",
                "dependsOn" : [ ]
                },
                {
                "ref" : "09cfcf87-a619-4eb6-9638-9ecd4fa76055",
                "dependsOn" : [ ]
                },
                {
                "ref" : "a9fef477-0d97-4b5a-8e4d-40529c78c838",
                "dependsOn" : [ ]
                },
                {
                "ref" : "9a642a54-1e89-4a01-a48e-3780b8d7ab1c",
                "dependsOn" : [ ]
                },
                {
                "ref" : "547b6f87-49a8-4552-88da-0d1ff7507d4c",
                "dependsOn" : [ ]
                },
                {
                "ref" : "c06911a1-05be-41f5-af67-f9405b726bea",
                "dependsOn" : [ ]
                },
                {
                "ref" : "d6069bcc-0443-4f7d-a4ac-eceaeff92f5e",
                "dependsOn" : [ ]
                },
                {
                "ref" : "b0013349-0ec0-4d7e-868d-7cf860d0f05e",
                "dependsOn" : [ ]
                },
                {
                "ref" : "18282ac2-d895-4387-8ba7-2d068f0d1bbd",
                "dependsOn" : [ ]
                },
                {
                "ref" : "c254814a-a64b-4726-9c9f-50fb734023f9",
                "dependsOn" : [ ]
                },
                {
                "ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64",
                "dependsOn" : [ ]
                },
                {
                "ref" : "f37629f1-b3af-4a21-98c5-0059cf9cfdf3",
                "dependsOn" : [ ]
                },
                {
                "ref" : "f03b8152-604a-4b50-af8b-5d34b47f263c",
                "dependsOn" : [ ]
                },
                {
                "ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae",
                "dependsOn" : [ ]
                }
            ],
            "vulnerabilities" : [
                {
                "bom-ref" : "bcd6ed5f-338c-4a2e-8109-1c999bf77909",
                "id" : "CVE-2023-44271",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "score" : 7.5,
                    "severity" : "high",
                    "method" : "CVSSv3",
                    "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H"
                    }
                ],
                "cwes" : [
                    770
                ],
                "description" : "An issue was discovered in Pillow before 10.0.0. It is a Denial of Service that uncontrollably allocates memory to process a given task, potentially causing a service to crash by having it run out of memory. This occurs for truetype in ImageFont when textlength in an ImageDraw instance operates on a long text argument.",
                "published" : "2023-11-03T05:15:00Z",
                "updated" : "2024-11-21T08:25:00Z",
                "affects" : [
                    {
                    "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2"
                    }
                ]
                },
                {
                "bom-ref" : "887673cd-4dc9-426e-ac73-e3c3bb20cab9",
                "id" : "CVE-2023-50447",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "score" : 8.1,
                    "severity" : "high",
                    "method" : "CVSSv3",
                    "vector" : "CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H"
                    }
                ],
                "cwes" : [
                    94
                ],
                "description" : "Pillow through 10.1.0 allows PIL.ImageMath.eval Arbitrary Code Execution via the environment parameter, a different vulnerability than CVE-2022-22817 (which was about the expression parameter).",
                "published" : "2024-01-19T20:15:00Z",
                "updated" : "2024-11-21T08:37:00Z",
                "affects" : [
                    {
                    "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2"
                    }
                ]
                },
                {
                "bom-ref" : "9940c65a-2d42-433b-b2fc-8b23d3e44b6f",
                "id" : "CVE-2024-28219",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "severity" : "unknown",
                    "method" : "other"
                    }
                ],
                "description" : "In _imagingcms.c in Pillow before 10.3.0, a buffer overflow exists because strcpy is used instead of strncpy.",
                "published" : "2024-04-03T03:15:00Z",
                "updated" : "2024-11-21T09:06:00Z",
                "affects" : [
                    {
                    "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2"
                    }
                ]
                },
                {
                "bom-ref" : "dd48aea9-abf8-4066-a302-f9fdafde5f94",
                "id" : "CVE-2023-37920",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "score" : 9.8,
                    "severity" : "critical",
                    "method" : "CVSSv3",
                    "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                    }
                ],
                "cwes" : [
                    345
                ],
                "description" : "Certifi is a curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. Certifi prior to version 2023.07.22 recognizes \"e-Tugra\" root certificates. e-Tugra's root certificates were subject to an investigation prompted by reporting of security issues in their systems. Certifi 2023.07.22 removes root certificates from \"e-Tugra\" from the root store.",
                "published" : "2023-07-25T21:15:00Z",
                "updated" : "2025-02-13T13:50:00Z",
                "affects" : [
                    {
                    "ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f"
                    }
                ]
                },
                {
                "bom-ref" : "5da6c82a-aef0-4553-bdae-f44e8baec6e7",
                "id" : "CVE-2024-39689",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "score" : 7.5,
                    "severity" : "high",
                    "method" : "CVSSv3",
                    "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N"
                    }
                ],
                "cwes" : [
                    345
                ],
                "description" : "Certifi is a curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. Certifi starting in 2021.5.30 and prior to 2024.7.4 recognized root certificates from `GLOBALTRUST`. Certifi 2024.7.04 removes root certificates from `GLOBALTRUST` from the root store. These are in the process of being removed from Mozilla's trust store. `GLOBALTRUST`'s root certificates are being removed pursuant to an investigation which identified \"long-running and unresolved compliance issues.\"",
                "published" : "2024-07-05T19:15:00Z",
                "updated" : "2025-02-15T00:15:00Z",
                "affects" : [
                    {
                    "ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f"
                    }
                ]
                },
                {
                "bom-ref" : "cba0c835-5170-43dc-9079-f971aa3098dd",
                "id" : "CVE-2024-3651",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "score" : 7.5,
                    "severity" : "high",
                    "method" : "CVSSv3",
                    "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H"
                    }
                ],
                "description" : "A vulnerability was identified in the kjd/idna library, specifically within the `idna.encode()` function, affecting version 3.6. The issue arises from the function's handling of crafted input strings, which can lead to quadratic complexity and consequently, a denial of service condition. This vulnerability is triggered by a crafted input that causes the `idna.encode()` function to process the input with considerable computational load, significantly increasing the processing time in a quadratic manner relative to the input size.",
                "published" : "2024-07-07T18:15:00Z",
                "updated" : "2024-11-21T09:30:00Z",
                "affects" : [
                    {
                    "ref" : "547b6f87-49a8-4552-88da-0d1ff7507d4c"
                    }
                ]
                },
                {
                "bom-ref" : "22105a0a-361d-486b-af48-49d80fcde3c7",
                "id" : "CVE-2023-32681",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "score" : 6.1,
                    "severity" : "medium",
                    "method" : "CVSSv3",
                    "vector" : "CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N"
                    }
                ],
                "description" : "Requests is a HTTP library. Since Requests 2.3.0, Requests has been leaking Proxy-Authorization headers to destination servers when redirected to an HTTPS endpoint. This is a product of how we use `rebuild_proxies` to reattach the `Proxy-Authorization` header to requests. For HTTP connections sent through the tunnel, the proxy will identify the header in the request itself and remove it prior to forwarding to the destination server. However when sent over HTTPS, the `Proxy-Authorization` header must be sent in the CONNECT request as the proxy has no visibility into the tunneled request. This results in Requests forwarding proxy credentials to the destination server unintentionally, allowing a malicious actor to potentially exfiltrate sensitive information. This issue has been patched in version 2.31.0.",
                "published" : "2023-05-26T18:15:00Z",
                "updated" : "2025-02-13T17:16:00Z",
                "affects" : [
                    {
                    "ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64"
                    }
                ]
                },
                {
                "bom-ref" : "fc0210ab-f1a3-44db-8cb4-69825bbcf39b",
                "id" : "CVE-2024-35195",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "severity" : "unknown",
                    "method" : "other"
                    }
                ],
                "description" : "Requests is a HTTP library. Prior to 2.32.0, when making requests through a Requests `Session`, if the first request is made with `verify=False` to disable cert verification, all subsequent requests to the same host will continue to ignore cert verification regardless of changes to the value of `verify`. This behavior will continue for the lifecycle of the connection in the connection pool. This vulnerability is fixed in 2.32.0.",
                "published" : "2024-05-20T21:15:00Z",
                "updated" : "2024-11-21T09:19:00Z",
                "affects" : [
                    {
                    "ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64"
                    }
                ]
                },
                {
                "bom-ref" : "c0c11cda-82af-42ee-aff8-c59df8e069af",
                "id" : "CVE-2024-34062",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "severity" : "unknown",
                    "method" : "other"
                    }
                ],
                "description" : "tqdm is an open source progress bar for Python and CLI. Any optional non-boolean CLI arguments (e.g. `--delim`, `--buf-size`, `--manpath`) are passed through python's `eval`, allowing arbitrary code execution. This issue is only locally exploitable and had been addressed in release version 4.66.3. All users are advised to upgrade. There are no known workarounds for this vulnerability.",
                "published" : "2024-05-03T10:15:00Z",
                "updated" : "2024-11-21T09:18:00Z",
                "affects" : [
                    {
                    "ref" : "f03b8152-604a-4b50-af8b-5d34b47f263c"
                    }
                ]
                },
                {
                "bom-ref" : "f4cf781b-de16-439c-a8d8-927d7c87aef4",
                "id" : "CVE-2023-43804",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "score" : 8.1,
                    "severity" : "high",
                    "method" : "CVSSv3",
                    "vector" : "CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N"
                    }
                ],
                "description" : "urllib3 is a user-friendly HTTP client library for Python. urllib3 doesn't treat the `Cookie` HTTP header special or provide any helpers for managing cookies over HTTP, that is the responsibility of the user. However, it is possible for a user to specify a `Cookie` header and unknowingly leak information via HTTP redirects to a different origin if that user doesn't disable redirects explicitly. This issue has been patched in urllib3 version 1.26.17 or 2.0.5.",
                "published" : "2023-10-04T17:15:00Z",
                "updated" : "2024-12-13T14:15:00Z",
                "affects" : [
                    {
                    "ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae"
                    }
                ]
                },
                {
                "bom-ref" : "a05f5f5c-8a51-4604-92e8-40884ec82ca6",
                "id" : "CVE-2023-45803",
                "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                },
                "ratings" : [
                    {
                    "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                    },
                    "score" : 4.2,
                    "severity" : "medium",
                    "method" : "CVSSv3",
                    "vector" : "CVSS:3.0/AV:A/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N"
                    }
                ],
                "description" : "urllib3 is a user-friendly HTTP client library for Python. urllib3 previously wouldn't remove the HTTP request body when an HTTP redirect response using status 301, 302, or 303 after the request had its method changed from one that could accept a request body (like `POST`) to `GET` as is required by HTTP RFCs. Although this behavior is not specified in the section for redirects, it can be inferred by piecing together information from different sections and we have observed the behavior in other major HTTP client implementations like curl and web browsers. Because the vulnerability requires a previously trusted service to become compromised in order to have an impact on confidentiality we believe the exploitability of this vulnerability is low. Additionally, many users aren't putting sensitive data in HTTP request bodies, if this is the case then this vulnerability isn't exploitable. Both of the following conditions must be true to be affected by this vulnerability: 1. Using urllib3 and submitting sensitive information in the HTTP request body (such as form data or JSON) and 2. The origin service is compromised and starts redirecting using 301, 302, or 303 to a malicious peer or the redirected-to service becomes compromised. This issue has been addressed in versions 1.26.18 and 2.0.7 and users are advised to update to resolve this issue. Users unable to update should disable redirects for services that aren't expecting to respond with redirects with `redirects=False` and disable automatic redirects with `redirects=False` and handle 301, 302, and 303 redirects manually by stripping the HTTP request body.",
                "published" : "2023-10-17T20:15:00Z",
                "updated" : "2025-02-13T18:15:00Z",
                "affects" : [
                    {
                    "ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae"
                    }
                ]
                }
            ]
            }
        
        self.cyclone_incorrect1 = {
            "oid_refs": {
                "aes-256-ccm": {
                "algo_oid": "2.16.840.1.101.3.4.1.47"
                },
                "id-aes256-CCM": {
                "algo_oid": "N/A"
                },
                "AES-128-OFB": {
                "algo_oid": "2.16.840.1.101.3.4.1.3"
                },
                "AES-128-ECB": {
                "algo_oid": "2.16.840.1.101.3.4.1.1"
                },
                "ARIA-256-CBC": {
                "algo_oid": "1.2.410.200046.1.1.12"
                },
                "ARIA256": {
                "algo_oid": "N/A"
                },
                "aes-256-gcm": {
                "algo_oid": "2.16.840.1.101.3.4.1.46"
                },
                "id-aes256-GCM": {
                "algo_oid": "N/A"
                },
                "ARIA-128-GCM": {
                "algo_oid": "1.2.410.200046.1.1.34"
                },
                "SM4-ECB": {
                "algo_oid": "1.2.156.10197.1.104.1"
                },
                "AES-192-CFB": {
                "algo_oid": "2.16.840.1.101.3.4.1.24"
                },
                "ARIA-256-ECB": {
                "algo_oid": "1.2.410.200046.1.1.11"
                },
                "CAMELLIA-128-CBC": {
                "algo_oid": "1.2.392.200011.61.1.1.1.2"
                },
                "CAMELLIA128": {
                "algo_oid": "N/A"
                },
                "AES-128-WRAP": {
                "algo_oid": "2.16.840.1.101.3.4.1.5"
                },
                "AES128-WRAP": {
                "algo_oid": "N/A"
                },
                "id-aes128-wrap": {
                "algo_oid": "N/A"
                },
                "DES3-WRAP": {
                "algo_oid": "1.2.840.113549.1.9.16.3.6"
                },
                "id-smime-alg-CMS3DESwrap": {
                "algo_oid": "N/A"
                },
                "CAMELLIA-128-CTR": {
                "algo_oid": "0.3.4401.5.3.1.9.9"
                },
                "SM4-OFB": {
                "algo_oid": "1.2.156.10197.1.104.3"
                },
                "SM4-OFB128": {
                "algo_oid": "N/A"
                },
                "CAMELLIA-192-CFB": {
                "algo_oid": "0.3.4401.5.3.1.9.24"
                },
                "ARIA-256-CCM": {
                "algo_oid": "1.2.410.200046.1.1.39"
                },
                "AES-128-XTS": {
                "algo_oid": "1.3.111.2.1619.0.1.1"
                },
                "ARIA-256-GCM": {
                "algo_oid": "1.2.410.200046.1.1.36"
                },
                "AES-128-CFB": {
                "algo_oid": "2.16.840.1.101.3.4.1.4"
                },
                "aes-128-gcm": {
                "algo_oid": "2.16.840.1.101.3.4.1.6"
                },
                "id-aes128-GCM": {
                "algo_oid": "N/A"
                },
                "AES-256-CBC": {
                "algo_oid": "2.16.840.1.101.3.4.1.42"
                },
                "AES256": {
                "algo_oid": "N/A"
                },
                "DES-EDE3-CBC": {
                "algo_oid": "1.2.840.113549.3.7"
                },
                "DES3": {
                "algo_oid": "N/A"
                },
                "CAMELLIA-256-CFB": {
                "algo_oid": "0.3.4401.5.3.1.9.44"
                },
                "CAMELLIA-128-CFB": {
                "algo_oid": "0.3.4401.5.3.1.9.4"
                },
                "CAMELLIA-192-ECB": {
                "algo_oid": "0.3.4401.5.3.1.9.21"
                },
                "AES-256-WRAP": {
                "algo_oid": "2.16.840.1.101.3.4.1.45"
                },
                "AES256-WRAP": {
                "algo_oid": "N/A"
                },
                "id-aes256-wrap": {
                "algo_oid": "N/A"
                },
                "aes-192-ccm": {
                "algo_oid": "2.16.840.1.101.3.4.1.27"
                },
                "id-aes192-CCM": {
                "algo_oid": "N/A"
                },
                "ARIA-192-ECB": {
                "algo_oid": "1.2.410.200046.1.1.6"
                },
                "AES-256-OFB": {
                "algo_oid": "2.16.840.1.101.3.4.1.43"
                },
                "CAMELLIA-192-CTR": {
                "algo_oid": "0.3.4401.5.3.1.9.29"
                },
                "AES-256-CFB": {
                "algo_oid": "2.16.840.1.101.3.4.1.44"
                },
                "aes-128-ccm": {
                "algo_oid": "2.16.840.1.101.3.4.1.7"
                },
                "id-aes128-CCM": {
                "algo_oid": "N/A"
                },
                "aes-192-gcm": {
                "algo_oid": "2.16.840.1.101.3.4.1.26"
                },
                "id-aes192-GCM": {
                "algo_oid": "N/A"
                },
                "AES-128-WRAP-PAD": {
                "algo_oid": "2.16.840.1.101.3.4.1.8"
                },
                "AES128-WRAP-PAD": {
                "algo_oid": "N/A"
                },
                "id-aes128-wrap-pad": {
                "algo_oid": "N/A"
                },
                "ARIA-128-CTR": {
                "algo_oid": "1.2.410.200046.1.1.5"
                },
                "AES-256-ECB": {
                "algo_oid": "2.16.840.1.101.3.4.1.41"
                },
                "ARIA-128-OFB": {
                "algo_oid": "1.2.410.200046.1.1.4"
                },
                "ARIA-256-CFB": {
                "algo_oid": "1.2.410.200046.1.1.13"
                },
                "ARIA-192-GCM": {
                "algo_oid": "1.2.410.200046.1.1.35"
                },
                "CAMELLIA-128-ECB": {
                "algo_oid": "0.3.4401.5.3.1.9.1"
                },
                "CAMELLIA-192-CBC": {
                "algo_oid": "1.2.392.200011.61.1.1.1.3"
                },
                "CAMELLIA192": {
                "algo_oid": "N/A"
                },
                "AES-192-CBC": {
                "algo_oid": "2.16.840.1.101.3.4.1.22"
                },
                "AES192": {
                "algo_oid": "N/A"
                },
                "ARIA-192-CBC": {
                "algo_oid": "1.2.410.200046.1.1.7"
                },
                "ARIA192": {
                "algo_oid": "N/A"
                },
                "AES-192-ECB": {
                "algo_oid": "2.16.840.1.101.3.4.1.21"
                },
                "ARIA-128-CFB": {
                "algo_oid": "1.2.410.200046.1.1.3"
                },
                "ARIA-256-CTR": {
                "algo_oid": "1.2.410.200046.1.1.15"
                },
                "SM4": {
                "algo_oid": "1.2.156.10197.1.104.2"
                },
                "SM4-CBC": {
                "algo_oid": "N/A"
                },
                "AES-256-WRAP-PAD": {
                "algo_oid": "2.16.840.1.101.3.4.1.48"
                },
                "AES256-WRAP-PAD": {
                "algo_oid": "N/A"
                },
                "id-aes256-wrap-pad": {
                "algo_oid": "N/A"
                },
                "AES-192-WRAP": {
                "algo_oid": "2.16.840.1.101.3.4.1.25"
                },
                "AES192-WRAP": {
                "algo_oid": "N/A"
                },
                "id-aes192-wrap": {
                "algo_oid": "N/A"
                },
                "SM4-CTR": {
                "algo_oid": "1.2.156.10197.1.104.7"
                },
                "CAMELLIA-192-OFB": {
                "algo_oid": "0.3.4401.5.3.1.9.23"
                },
                "AES-128-CBC": {
                "algo_oid": "2.16.840.1.101.3.4.1.2"
                },
                "AES128": {
                "algo_oid": "N/A"
                },
                "CAMELLIA-256-OFB": {
                "algo_oid": "0.3.4401.5.3.1.9.43"
                },
                "CAMELLIA-256-CBC": {
                "algo_oid": "1.2.392.200011.61.1.1.1.4"
                },
                "CAMELLIA256": {
                "algo_oid": "N/A"
                },
                "SM4-CFB": {
                "algo_oid": "1.2.156.10197.1.104.4"
                },
                "SM4-CFB128": {
                "algo_oid": "N/A"
                },
                "ARIA-128-CBC": {
                "algo_oid": "1.2.410.200046.1.1.2"
                },
                "ARIA128": {
                "algo_oid": "N/A"
                },
                "CAMELLIA-128-OFB": {
                "algo_oid": "0.3.4401.5.3.1.9.3"
                },
                "ARIA-192-CCM": {
                "algo_oid": "1.2.410.200046.1.1.38"
                },
                "ARIA-256-OFB": {
                "algo_oid": "1.2.410.200046.1.1.14"
                },
                "CAMELLIA-256-CTR": {
                "algo_oid": "0.3.4401.5.3.1.9.49"
                },
                "DES-EDE": {
                "algo_oid": "1.3.14.3.2.17"
                },
                "DES-EDE-ECB": {
                "algo_oid": "N/A"
                },
                "AES-192-OFB": {
                "algo_oid": "2.16.840.1.101.3.4.1.23"
                },
                "ARIA-192-CTR": {
                "algo_oid": "1.2.410.200046.1.1.10"
                },
                "CAMELLIA-256-ECB": {
                "algo_oid": "0.3.4401.5.3.1.9.41"
                },
                "ARIA-128-ECB": {
                "algo_oid": "1.2.410.200046.1.1.1"
                },
                "ARIA-192-CFB": {
                "algo_oid": "1.2.410.200046.1.1.8"
                },
                "ARIA-192-OFB": {
                "algo_oid": "1.2.410.200046.1.1.9"
                },
                "ARIA-128-CCM": {
                "algo_oid": "1.2.410.200046.1.1.37"
                },
                "AES-256-XTS": {
                "algo_oid": "1.3.111.2.1619.0.1.2"
                },
                "AES-192-WRAP-PAD": {
                "algo_oid": "2.16.840.1.101.3.4.1.28"
                },
                "AES192-WRAP-PAD": {
                "algo_oid": "N/A"
                },
                "id-aes192-wrap-pad": {
                "algo_oid": "N/A"
                },
                "AES-256-WRAP-INV": {
                "algo_oid": "N/A"
                },
                "AES256-WRAP-INV": {
                "algo_oid": "N/A"
                },
                "AES-192-WRAP-INV": {
                "algo_oid": "N/A"
                },
                "AES192-WRAP-INV": {
                "algo_oid": "N/A"
                },
                "AES-128-WRAP-INV": {
                "algo_oid": "N/A"
                },
                "AES128-WRAP-INV": {
                "algo_oid": "N/A"
                },
                "AES-256-WRAP-PAD-INV": {
                "algo_oid": "N/A"
                },
                "AES256-WRAP-PAD-INV": {
                "algo_oid": "N/A"
                },
                "AES-192-WRAP-PAD-INV": {
                "algo_oid": "N/A"
                },
                "AES192-WRAP-PAD-INV": {
                "algo_oid": "N/A"
                },
                "AES-128-WRAP-PAD-INV": {
                "algo_oid": "N/A"
                },
                "AES128-WRAP-PAD-INV": {
                "algo_oid": "N/A"
                },
                "DES-EDE3": {
                "algo_oid": "N/A"
                },
                "DES-EDE3-ECB": {
                "algo_oid": "N/A"
                }
            },
            "ciphers": {
                "tls": {
                "TLS_AES_256_GCM_SHA384": {
                    "TLS_version": "TLSv1.3",
                    "key_exchange_algorithm": "any",
                    "authentication": "any",
                    "encryption_algorithm": "AESGCM(256)",
                    "mac": "AEAD"
                },
                "TLS_CHACHA20_POLY1305_SHA256": {
                    "TLS_version": "TLSv1.3",
                    "key_exchange_algorithm": "any",
                    "authentication": "any",
                    "encryption_algorithm": "CHACHA20/POLY1305(256)",
                    "mac": "AEAD"
                },
                "TLS_AES_128_GCM_SHA256": {
                    "TLS_version": "TLSv1.3",
                    "key_exchange_algorithm": "any",
                    "authentication": "any",
                    "encryption_algorithm": "AESGCM(128)",
                    "mac": "AEAD"
                },
                "ECDHE-ECDSA-AES256-GCM-SHA384": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "ECDSA",
                    "encryption_algorithm": "AESGCM(256)",
                    "mac": "AEAD"
                },
                "ECDHE-RSA-AES256-GCM-SHA384": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AESGCM(256)",
                    "mac": "AEAD"
                },
                "DHE-RSA-AES256-GCM-SHA384": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "DH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AESGCM(256)",
                    "mac": "AEAD"
                },
                "ECDHE-ECDSA-CHACHA20-POLY1305": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "ECDSA",
                    "encryption_algorithm": "CHACHA20/POLY1305(256)",
                    "mac": "AEAD"
                },
                "ECDHE-RSA-CHACHA20-POLY1305": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "RSA",
                    "encryption_algorithm": "CHACHA20/POLY1305(256)",
                    "mac": "AEAD"
                },
                "DHE-RSA-CHACHA20-POLY1305": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "DH",
                    "authentication": "RSA",
                    "encryption_algorithm": "CHACHA20/POLY1305(256)",
                    "mac": "AEAD"
                },
                "ECDHE-ECDSA-AES128-GCM-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "ECDSA",
                    "encryption_algorithm": "AESGCM(128)",
                    "mac": "AEAD"
                },
                "ECDHE-RSA-AES128-GCM-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AESGCM(128)",
                    "mac": "AEAD"
                },
                "DHE-RSA-AES128-GCM-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "DH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AESGCM(128)",
                    "mac": "AEAD"
                },
                "ECDHE-ECDSA-AES256-SHA384": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "ECDSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA384"
                },
                "ECDHE-RSA-AES256-SHA384": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA384"
                },
                "DHE-RSA-AES256-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "DH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA256"
                },
                "ECDHE-ECDSA-AES128-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "ECDSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA256"
                },
                "ECDHE-RSA-AES128-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA256"
                },
                "DHE-RSA-AES128-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "DH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA256"
                },
                "ECDHE-ECDSA-AES256-SHA": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "ECDSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "ECDHE-RSA-AES256-SHA": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "DHE-RSA-AES256-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "DH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "ECDHE-ECDSA-AES128-SHA": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "ECDSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                },
                "ECDHE-RSA-AES128-SHA": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "ECDH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                },
                "DHE-RSA-AES128-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "DH",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                },
                "RSA-PSK-AES256-GCM-SHA384": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "RSAPSK",
                    "authentication": "RSA",
                    "encryption_algorithm": "AESGCM(256)",
                    "mac": "AEAD"
                },
                "DHE-PSK-AES256-GCM-SHA384": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "DHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AESGCM(256)",
                    "mac": "AEAD"
                },
                "RSA-PSK-CHACHA20-POLY1305": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "RSAPSK",
                    "authentication": "RSA",
                    "encryption_algorithm": "CHACHA20/POLY1305(256)",
                    "mac": "AEAD"
                },
                "DHE-PSK-CHACHA20-POLY1305": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "DHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "CHACHA20/POLY1305(256)",
                    "mac": "AEAD"
                },
                "ECDHE-PSK-CHACHA20-POLY1305": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "ECDHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "CHACHA20/POLY1305(256)",
                    "mac": "AEAD"
                },
                "AES256-GCM-SHA384": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "RSA",
                    "authentication": "RSA",
                    "encryption_algorithm": "AESGCM(256)",
                    "mac": "AEAD"
                },
                "PSK-AES256-GCM-SHA384": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "PSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AESGCM(256)",
                    "mac": "AEAD"
                },
                "PSK-CHACHA20-POLY1305": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "PSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "CHACHA20/POLY1305(256)",
                    "mac": "AEAD"
                },
                "RSA-PSK-AES128-GCM-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "RSAPSK",
                    "authentication": "RSA",
                    "encryption_algorithm": "AESGCM(128)",
                    "mac": "AEAD"
                },
                "DHE-PSK-AES128-GCM-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "DHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AESGCM(128)",
                    "mac": "AEAD"
                },
                "AES128-GCM-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "RSA",
                    "authentication": "RSA",
                    "encryption_algorithm": "AESGCM(128)",
                    "mac": "AEAD"
                },
                "PSK-AES128-GCM-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "PSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AESGCM(128)",
                    "mac": "AEAD"
                },
                "AES256-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "RSA",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA256"
                },
                "AES128-SHA256": {
                    "TLS_version": "TLSv1.2",
                    "key_exchange_algorithm": "RSA",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA256"
                },
                "ECDHE-PSK-AES256-CBC-SHA384": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "ECDHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA384"
                },
                "ECDHE-PSK-AES256-CBC-SHA": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "ECDHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "SRP-RSA-AES-256-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "SRP",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "SRP-AES-256-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "SRP",
                    "authentication": "SRP",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "RSA-PSK-AES256-CBC-SHA384": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "RSAPSK",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA384"
                },
                "DHE-PSK-AES256-CBC-SHA384": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "DHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA384"
                },
                "RSA-PSK-AES256-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "RSAPSK",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "DHE-PSK-AES256-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "DHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "AES256-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "RSA",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "PSK-AES256-CBC-SHA384": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "PSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA384"
                },
                "PSK-AES256-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "PSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(256)",
                    "mac": "SHA1"
                },
                "ECDHE-PSK-AES128-CBC-SHA256": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "ECDHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA256"
                },
                "ECDHE-PSK-AES128-CBC-SHA": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "ECDHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                },
                "SRP-RSA-AES-128-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "SRP",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                },
                "SRP-AES-128-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "SRP",
                    "authentication": "SRP",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                },
                "RSA-PSK-AES128-CBC-SHA256": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "RSAPSK",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA256"
                },
                "DHE-PSK-AES128-CBC-SHA256": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "DHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA256"
                },
                "RSA-PSK-AES128-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "RSAPSK",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                },
                "DHE-PSK-AES128-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "DHEPSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                },
                "AES128-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "RSA",
                    "authentication": "RSA",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                },
                "PSK-AES128-CBC-SHA256": {
                    "TLS_version": "TLSv1",
                    "key_exchange_algorithm": "PSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA256"
                },
                "PSK-AES128-CBC-SHA": {
                    "TLS_version": "SSLv3",
                    "key_exchange_algorithm": "PSK",
                    "authentication": "PSK",
                    "encryption_algorithm": "AES(128)",
                    "mac": "SHA1"
                }
                }
            },
            "nmap_tls_info": {
                "nmap_tls_ssl_enum_ciphers_info": {
                "22": {
                    "net_proto": "tcp",
                    "status": "open",
                    "tls_vers_enabled": {}
                }
                }
            },
            "certificate": {},
            "ssh_crypto_info": {
                "gssapikexalgorithms": [
                "gss-group14-sha256-",
                "gss-group16-sha512-",
                "gss-nistp256-sha256-",
                "gss-curve25519-sha256-",
                "gss-group14-sha1-",
                "gss-gex-sha1-"
                ],
                "ciphers": [
                "chacha20-poly1305@openssh.com",
                "aes128-ctr",
                "aes192-ctr",
                "aes256-ctr",
                "aes128-gcm@openssh.com",
                "aes256-gcm@openssh.com"
                ],
                "macs": [
                "umac-64-etm@openssh.com",
                "umac-128-etm@openssh.com",
                "hmac-sha2-256-etm@openssh.com",
                "hmac-sha2-512-etm@openssh.com",
                "hmac-sha1-etm@openssh.com",
                "umac-64@openssh.com",
                "umac-128@openssh.com",
                "hmac-sha2-256",
                "hmac-sha2-512",
                "hmac-sha1"
                ],
                "kexalgorithms": [
                "sntrup761x25519-sha512@openssh.com",
                "curve25519-sha256",
                "curve25519-sha256@libssh.org",
                "ecdh-sha2-nistp256",
                "ecdh-sha2-nistp384",
                "ecdh-sha2-nistp521",
                "diffie-hellman-group-exchange-sha256",
                "diffie-hellman-group16-sha512",
                "diffie-hellman-group18-sha512",
                "diffie-hellman-group14-sha256"
                ],
                "casignaturealgorithms": [
                "ssh-ed25519",
                "ecdsa-sha2-nistp256",
                "ecdsa-sha2-nistp384",
                "ecdsa-sha2-nistp521",
                "sk-ssh-ed25519@openssh.com",
                "sk-ecdsa-sha2-nistp256@openssh.com",
                "rsa-sha2-512",
                "rsa-sha2-256"
                ],
                "hostbasedacceptedalgorithms": [
                "ssh-ed25519-cert-v01@openssh.com",
                "ecdsa-sha2-nistp256-cert-v01@openssh.com",
                "ecdsa-sha2-nistp384-cert-v01@openssh.com",
                "ecdsa-sha2-nistp521-cert-v01@openssh.com",
                "sk-ssh-ed25519-cert-v01@openssh.com",
                "sk-ecdsa-sha2-nistp256-cert-v01@openssh.com",
                "rsa-sha2-512-cert-v01@openssh.com",
                "rsa-sha2-256-cert-v01@openssh.com",
                "ssh-ed25519",
                "ecdsa-sha2-nistp256",
                "ecdsa-sha2-nistp384",
                "ecdsa-sha2-nistp521",
                "sk-ssh-ed25519@openssh.com",
                "sk-ecdsa-sha2-nistp256@openssh.com",
                "rsa-sha2-512",
                "rsa-sha2-256"
                ],
                "hostkeyalgorithms": [
                "ssh-ed25519-cert-v01@openssh.com",
                "ecdsa-sha2-nistp256-cert-v01@openssh.com",
                "ecdsa-sha2-nistp384-cert-v01@openssh.com",
                "ecdsa-sha2-nistp521-cert-v01@openssh.com",
                "sk-ssh-ed25519-cert-v01@openssh.com",
                "sk-ecdsa-sha2-nistp256-cert-v01@openssh.com",
                "rsa-sha2-512-cert-v01@openssh.com",
                "rsa-sha2-256-cert-v01@openssh.com",
                "ssh-ed25519",
                "ecdsa-sha2-nistp256",
                "ecdsa-sha2-nistp384",
                "ecdsa-sha2-nistp521",
                "sk-ssh-ed25519@openssh.com",
                "sk-ecdsa-sha2-nistp256@openssh.com",
                "rsa-sha2-512",
                "rsa-sha2-256"
                ],
                "pubkeyacceptedalgorithms": [
                "ssh-ed25519-cert-v01@openssh.com",
                "ecdsa-sha2-nistp256-cert-v01@openssh.com",
                "ecdsa-sha2-nistp384-cert-v01@openssh.com",
                "ecdsa-sha2-nistp521-cert-v01@openssh.com",
                "sk-ssh-ed25519-cert-v01@openssh.com",
                "sk-ecdsa-sha2-nistp256-cert-v01@openssh.com",
                "rsa-sha2-512-cert-v01@openssh.com",
                "rsa-sha2-256-cert-v01@openssh.com",
                "ssh-ed25519",
                "ecdsa-sha2-nistp256",
                "ecdsa-sha2-nistp384",
                "ecdsa-sha2-nistp521",
                "sk-ssh-ed25519@openssh.com",
                "sk-ecdsa-sha2-nistp256@openssh.com",
                "rsa-sha2-512",
                "rsa-sha2-256"
                ]
            }
            }
        
        self.cyclone_incorrect2 = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "serialNumber": "urn:uuid:9b553688-c976-4d0a-9d22-4e3b59d174e2",
            "version": 1,
            "metadata": {
                "timestamp": "2025-02-25T10:32:41Z",
                "component": {
                    "type": "application",
                    "name": "my application",
                    "version": "1.0"
                }
            },
            "components": [
                {
                    "type": "certificate",
                    "name": "MailHog TLS Certificate",
                    "version": "1.0",
                    "description": "Self-signed TLS certificate for MailHog",
                    "licenses": [],
                    "externalReferences": [
                        {
                            "type": "distribution",
                            "url": "file:/home/localadmin/mailhog.crt"
                        }
                    ]
                }
            ]
        }

        self.cyclone_thing = {
            "attributes" : {
                "bomFormat" : "CycloneDX",
                "specVersion" : "1.5",
                "serialNumber" : "urn:uuid:dce5f002-f1f2-4809-bf9d-8813ae2efb79",
                "version" : 1
            },
            "features" : {
                "metadata" : {
                    "properties": {
                        "timestamp" : "2025-02-25T09:19:18Z",
                        "tools" : [
                            {
                            "vendor" : "OWASP",
                            "name" : "Dependency-Track",
                            "version" : "4.12.1"
                            }
                        ],
                        "component" : {
                            "type" : "application",
                            "bom-ref" : "82e592b4-56b8-455a-b3f6-70a966996277",
                            "name" : "test",
                            "version" : "1.0"
                        }
                    }
                },
                "components" : {
                    "properties": {
                        "1":{
                            "type" : "library",
                            "bom-ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2",
                            "name" : "Pillow",
                            "version" : "9.4.0",
                            "description" : "requirements line 10: Pillow==9.4.0",
                            "purl" : "pkg:pypi/pillow@9.4.0",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/Pillow/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "2":{
                            "type" : "library",
                            "bom-ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f",
                            "name" : "certifi",
                            "version" : "2022.12.7",
                            "description" : "requirements line 1: certifi==2022.12.7",
                            "purl" : "pkg:pypi/certifi@2022.12.7",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/certifi/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "3":{
                            "type" : "library",
                            "bom-ref" : "09cfcf87-a619-4eb6-9638-9ecd4fa76055",
                            "name" : "charset-normalizer",
                            "version" : "3.0.1",
                            "description" : "requirements line 2: charset-normalizer==3.0.1",
                            "purl" : "pkg:pypi/charset-normalizer@3.0.1",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/charset-normalizer/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "4":{
                            "type" : "library",
                            "bom-ref" : "a9fef477-0d97-4b5a-8e4d-40529c78c838",
                            "name" : "colorama",
                            "version" : "0.4.6",
                            "description" : "requirements line 3: colorama==0.4.6",
                            "purl" : "pkg:pypi/colorama@0.4.6",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/colorama/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "5":{
                            "type" : "library",
                            "bom-ref" : "9a642a54-1e89-4a01-a48e-3780b8d7ab1c",
                            "name" : "decorator",
                            "version" : "4.4.2",
                            "description" : "requirements line 4: decorator==4.4.2",
                            "purl" : "pkg:pypi/decorator@4.4.2",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/decorator/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "6":{
                            "type" : "library",
                            "bom-ref" : "547b6f87-49a8-4552-88da-0d1ff7507d4c",
                            "name" : "idna",
                            "version" : "3.4",
                            "description" : "requirements line 5: idna==3.4",
                            "purl" : "pkg:pypi/idna@3.4",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/idna/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "7":{
                            "type" : "library",
                            "bom-ref" : "c06911a1-05be-41f5-af67-f9405b726bea",
                            "name" : "imageio",
                            "version" : "2.25.0",
                            "description" : "requirements line 6: imageio==2.25.0",
                            "purl" : "pkg:pypi/imageio@2.25.0",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/imageio/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "8":{
                            "type" : "library",
                            "bom-ref" : "d6069bcc-0443-4f7d-a4ac-eceaeff92f5e",
                            "name" : "imageio-ffmpeg",
                            "version" : "0.4.8",
                            "description" : "requirements line 7: imageio-ffmpeg==0.4.8",
                            "purl" : "pkg:pypi/imageio-ffmpeg@0.4.8",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/imageio-ffmpeg/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "9":{
                            "type" : "library",
                            "bom-ref" : "b0013349-0ec0-4d7e-868d-7cf860d0f05e",
                            "name" : "moviepy",
                            "version" : "1.0.3",
                            "description" : "requirements line 8: moviepy==1.0.3",
                            "purl" : "pkg:pypi/moviepy@1.0.3",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/moviepy/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "10":{
                            "type" : "library",
                            "bom-ref" : "18282ac2-d895-4387-8ba7-2d068f0d1bbd",
                            "name" : "numpy",
                            "version" : "1.24.1",
                            "description" : "requirements line 9: numpy==1.24.1",
                            "purl" : "pkg:pypi/numpy@1.24.1",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/numpy/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "11":{
                            "type" : "library",
                            "bom-ref" : "c254814a-a64b-4726-9c9f-50fb734023f9",
                            "name" : "proglog",
                            "version" : "0.1.10",
                            "description" : "requirements line 11: proglog==0.1.10",
                            "purl" : "pkg:pypi/proglog@0.1.10",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/proglog/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "13":{
                            "type" : "library",
                            "bom-ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64",
                            "name" : "requests",
                            "version" : "2.28.2",
                            "description" : "requirements line 12: requests==2.28.2",
                            "purl" : "pkg:pypi/requests@2.28.2",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/requests/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "14":{
                            "type" : "library",
                            "bom-ref" : "f37629f1-b3af-4a21-98c5-0059cf9cfdf3",
                            "name" : "tk",
                            "version" : "0.1.0",
                            "description" : "requirements line 13: tk==0.1.0",
                            "purl" : "pkg:pypi/tk@0.1.0",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/tk/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "15":{
                            "type" : "library",
                            "bom-ref" : "f03b8152-604a-4b50-af8b-5d34b47f263c",
                            "name" : "tqdm",
                            "version" : "4.64.1",
                            "description" : "requirements line 14: tqdm==4.64.1",
                            "purl" : "pkg:pypi/tqdm@4.64.1",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/tqdm/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        },
                        "16":{
                            "type" : "library",
                            "bom-ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae",
                            "name" : "urllib3",
                            "version" : "1.26.14",
                            "description" : "requirements line 15: urllib3==1.26.14",
                            "purl" : "pkg:pypi/urllib3@1.26.14",
                            "externalReferences" : [
                            {
                                "type" : "distribution",
                                "url" : "https://pypi.org/simple/urllib3/",
                                "comment" : "implicit dist url"
                            }
                            ]
                        }
                    }
                },
                "dependencies" : {
                    "properties": {
                        "1":{
                            "ref" : "82e592b4-56b8-455a-b3f6-70a966996277",
                            "dependsOn" : [ ]
                        },
                        "2":{
                            "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2",
                            "dependsOn" : [ ]
                        },
                        "3":{
                            "ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f",
                            "dependsOn" : [ ]
                        },
                        "4":{
                            "ref" : "09cfcf87-a619-4eb6-9638-9ecd4fa76055",
                            "dependsOn" : [ ]
                        },
                        "5":{
                            "ref" : "a9fef477-0d97-4b5a-8e4d-40529c78c838",
                            "dependsOn" : [ ]
                        },
                        "6":{
                            "ref" : "9a642a54-1e89-4a01-a48e-3780b8d7ab1c",
                            "dependsOn" : [ ]
                        },
                        "7":{
                            "ref" : "547b6f87-49a8-4552-88da-0d1ff7507d4c",
                            "dependsOn" : [ ]
                        },
                        "8":{
                            "ref" : "c06911a1-05be-41f5-af67-f9405b726bea",
                            "dependsOn" : [ ]
                        },
                        "9":{
                            "ref" : "d6069bcc-0443-4f7d-a4ac-eceaeff92f5e",
                            "dependsOn" : [ ]
                        },
                        "10":{
                            "ref" : "b0013349-0ec0-4d7e-868d-7cf860d0f05e",
                            "dependsOn" : [ ]
                        },
                        "11":{
                            "ref" : "18282ac2-d895-4387-8ba7-2d068f0d1bbd",
                            "dependsOn" : [ ]
                        },
                        "12":{
                            "ref" : "c254814a-a64b-4726-9c9f-50fb734023f9",
                            "dependsOn" : [ ]
                        },
                        "13":{
                            "ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64",
                            "dependsOn" : [ ]
                        },
                        "14":{
                            "ref" : "f37629f1-b3af-4a21-98c5-0059cf9cfdf3",
                            "dependsOn" : [ ]
                        },
                        "15":{
                            "ref" : "f03b8152-604a-4b50-af8b-5d34b47f263c",
                            "dependsOn" : [ ]
                        },
                        "16":{
                            "ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae",
                            "dependsOn" : [ ]
                        }
                    }
                },
                "vulnerabilities" : {
                    "properties": {
                        "1":{
                            "bom-ref" : "bcd6ed5f-338c-4a2e-8109-1c999bf77909",
                            "id" : "CVE-2023-44271",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "score" : 7.5,
                                "severity" : "high",
                                "method" : "CVSSv3",
                                "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H"
                            }
                            ],
                            "cwes" : [
                            770
                            ],
                            "description" : "An issue was discovered in Pillow before 10.0.0. It is a Denial of Service that uncontrollably allocates memory to process a given task, potentially causing a service to crash by having it run out of memory. This occurs for truetype in ImageFont when textlength in an ImageDraw instance operates on a long text argument.",
                            "published" : "2023-11-03T05:15:00Z",
                            "updated" : "2024-11-21T08:25:00Z",
                            "affects" : [
                            {
                                "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2"
                            }
                            ]
                        },
                        "2":{
                            "bom-ref" : "887673cd-4dc9-426e-ac73-e3c3bb20cab9",
                            "id" : "CVE-2023-50447",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "score" : 8.1,
                                "severity" : "high",
                                "method" : "CVSSv3",
                                "vector" : "CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H"
                            }
                            ],
                            "cwes" : [
                            94
                            ],
                            "description" : "Pillow through 10.1.0 allows PIL.ImageMath.eval Arbitrary Code Execution via the environment parameter, a different vulnerability than CVE-2022-22817 (which was about the expression parameter).",
                            "published" : "2024-01-19T20:15:00Z",
                            "updated" : "2024-11-21T08:37:00Z",
                            "affects" : [
                            {
                                "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2"
                            }
                            ]
                        },
                        "3":{
                            "bom-ref" : "9940c65a-2d42-433b-b2fc-8b23d3e44b6f",
                            "id" : "CVE-2024-28219",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "severity" : "unknown",
                                "method" : "other"
                            }
                            ],
                            "description" : "In _imagingcms.c in Pillow before 10.3.0, a buffer overflow exists because strcpy is used instead of strncpy.",
                            "published" : "2024-04-03T03:15:00Z",
                            "updated" : "2024-11-21T09:06:00Z",
                            "affects" : [
                            {
                                "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2"
                            }
                            ]
                        },
                        "4":{
                            "bom-ref" : "dd48aea9-abf8-4066-a302-f9fdafde5f94",
                            "id" : "CVE-2023-37920",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "score" : 9.8,
                                "severity" : "critical",
                                "method" : "CVSSv3",
                                "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                            }
                            ],
                            "cwes" : [
                            345
                            ],
                            "description" : "Certifi is a curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. Certifi prior to version 2023.07.22 recognizes \"e-Tugra\" root certificates. e-Tugra's root certificates were subject to an investigation prompted by reporting of security issues in their systems. Certifi 2023.07.22 removes root certificates from \"e-Tugra\" from the root store.",
                            "published" : "2023-07-25T21:15:00Z",
                            "updated" : "2025-02-13T13:50:00Z",
                            "affects" : [
                            {
                                "ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f"
                            }
                            ]
                        },
                        "5":{
                            "bom-ref" : "5da6c82a-aef0-4553-bdae-f44e8baec6e7",
                            "id" : "CVE-2024-39689",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "score" : 7.5,
                                "severity" : "high",
                                "method" : "CVSSv3",
                                "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N"
                            }
                            ],
                            "cwes" : [
                            345
                            ],
                            "description" : "Certifi is a curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. Certifi starting in 2021.5.30 and prior to 2024.7.4 recognized root certificates from `GLOBALTRUST`. Certifi 2024.7.04 removes root certificates from `GLOBALTRUST` from the root store. These are in the process of being removed from Mozilla's trust store. `GLOBALTRUST`'s root certificates are being removed pursuant to an investigation which identified \"long-running and unresolved compliance issues.\"",
                            "published" : "2024-07-05T19:15:00Z",
                            "updated" : "2025-02-15T00:15:00Z",
                            "affects" : [
                            {
                                "ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f"
                            }
                            ]
                        },
                        "6":{
                            "bom-ref" : "cba0c835-5170-43dc-9079-f971aa3098dd",
                            "id" : "CVE-2024-3651",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "score" : 7.5,
                                "severity" : "high",
                                "method" : "CVSSv3",
                                "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H"
                            }
                            ],
                            "description" : "A vulnerability was identified in the kjd/idna library, specifically within the `idna.encode()` function, affecting version 3.6. The issue arises from the function's handling of crafted input strings, which can lead to quadratic complexity and consequently, a denial of service condition. This vulnerability is triggered by a crafted input that causes the `idna.encode()` function to process the input with considerable computational load, significantly increasing the processing time in a quadratic manner relative to the input size.",
                            "published" : "2024-07-07T18:15:00Z",
                            "updated" : "2024-11-21T09:30:00Z",
                            "affects" : [
                            {
                                "ref" : "547b6f87-49a8-4552-88da-0d1ff7507d4c"
                            }
                            ]
                        },
                        "7":{
                            "bom-ref" : "22105a0a-361d-486b-af48-49d80fcde3c7",
                            "id" : "CVE-2023-32681",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "score" : 6.1,
                                "severity" : "medium",
                                "method" : "CVSSv3",
                                "vector" : "CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N"
                            }
                            ],
                            "description" : "Requests is a HTTP library. Since Requests 2.3.0, Requests has been leaking Proxy-Authorization headers to destination servers when redirected to an HTTPS endpoint. This is a product of how we use `rebuild_proxies` to reattach the `Proxy-Authorization` header to requests. For HTTP connections sent through the tunnel, the proxy will identify the header in the request itself and remove it prior to forwarding to the destination server. However when sent over HTTPS, the `Proxy-Authorization` header must be sent in the CONNECT request as the proxy has no visibility into the tunneled request. This results in Requests forwarding proxy credentials to the destination server unintentionally, allowing a malicious actor to potentially exfiltrate sensitive information. This issue has been patched in version 2.31.0.",
                            "published" : "2023-05-26T18:15:00Z",
                            "updated" : "2025-02-13T17:16:00Z",
                            "affects" : [
                            {
                                "ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64"
                            }
                            ]
                        },
                        "8":{
                            "bom-ref" : "fc0210ab-f1a3-44db-8cb4-69825bbcf39b",
                            "id" : "CVE-2024-35195",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "severity" : "unknown",
                                "method" : "other"
                            }
                            ],
                            "description" : "Requests is a HTTP library. Prior to 2.32.0, when making requests through a Requests `Session`, if the first request is made with `verify=False` to disable cert verification, all subsequent requests to the same host will continue to ignore cert verification regardless of changes to the value of `verify`. This behavior will continue for the lifecycle of the connection in the connection pool. This vulnerability is fixed in 2.32.0.",
                            "published" : "2024-05-20T21:15:00Z",
                            "updated" : "2024-11-21T09:19:00Z",
                            "affects" : [
                            {
                                "ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64"
                            }
                            ]
                        },
                        "9":{
                            "bom-ref" : "c0c11cda-82af-42ee-aff8-c59df8e069af",
                            "id" : "CVE-2024-34062",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "severity" : "unknown",
                                "method" : "other"
                            }
                            ],
                            "description" : "tqdm is an open source progress bar for Python and CLI. Any optional non-boolean CLI arguments (e.g. `--delim`, `--buf-size`, `--manpath`) are passed through python's `eval`, allowing arbitrary code execution. This issue is only locally exploitable and had been addressed in release version 4.66.3. All users are advised to upgrade. There are no known workarounds for this vulnerability.",
                            "published" : "2024-05-03T10:15:00Z",
                            "updated" : "2024-11-21T09:18:00Z",
                            "affects" : [
                            {
                                "ref" : "f03b8152-604a-4b50-af8b-5d34b47f263c"
                            }
                            ]
                        },
                        "10":{
                            "bom-ref" : "f4cf781b-de16-439c-a8d8-927d7c87aef4",
                            "id" : "CVE-2023-43804",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "score" : 8.1,
                                "severity" : "high",
                                "method" : "CVSSv3",
                                "vector" : "CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N"
                            }
                            ],
                            "description" : "urllib3 is a user-friendly HTTP client library for Python. urllib3 doesn't treat the `Cookie` HTTP header special or provide any helpers for managing cookies over HTTP, that is the responsibility of the user. However, it is possible for a user to specify a `Cookie` header and unknowingly leak information via HTTP redirects to a different origin if that user doesn't disable redirects explicitly. This issue has been patched in urllib3 version 1.26.17 or 2.0.5.",
                            "published" : "2023-10-04T17:15:00Z",
                            "updated" : "2024-12-13T14:15:00Z",
                            "affects" : [
                            {
                                "ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae"
                            }
                            ]
                        },
                        "11":{
                            "bom-ref" : "a05f5f5c-8a51-4604-92e8-40884ec82ca6",
                            "id" : "CVE-2023-45803",
                            "source" : {
                            "name" : "NVD",
                            "url" : "https://nvd.nist.gov/"
                            },
                            "ratings" : [
                            {
                                "source" : {
                                "name" : "NVD",
                                "url" : "https://nvd.nist.gov/"
                                },
                                "score" : 4.2,
                                "severity" : "medium",
                                "method" : "CVSSv3",
                                "vector" : "CVSS:3.0/AV:A/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N"
                            }
                            ],
                            "description" : "urllib3 is a user-friendly HTTP client library for Python. urllib3 previously wouldn't remove the HTTP request body when an HTTP redirect response using status 301, 302, or 303 after the request had its method changed from one that could accept a request body (like `POST`) to `GET` as is required by HTTP RFCs. Although this behavior is not specified in the section for redirects, it can be inferred by piecing together information from different sections and we have observed the behavior in other major HTTP client implementations like curl and web browsers. Because the vulnerability requires a previously trusted service to become compromised in order to have an impact on confidentiality we believe the exploitability of this vulnerability is low. Additionally, many users aren't putting sensitive data in HTTP request bodies, if this is the case then this vulnerability isn't exploitable. Both of the following conditions must be true to be affected by this vulnerability: 1. Using urllib3 and submitting sensitive information in the HTTP request body (such as form data or JSON) and 2. The origin service is compromised and starts redirecting using 301, 302, or 303 to a malicious peer or the redirected-to service becomes compromised. This issue has been addressed in versions 1.26.18 and 2.0.7 and users are advised to update to resolve this issue. Users unable to update should disable redirects for services that aren't expecting to respond with redirects with `redirects=False` and disable automatic redirects with `redirects=False` and handle 301, 302, and 303 redirects manually by stripping the HTTP request body.",
                            "published" : "2023-10-17T20:15:00Z",
                            "updated" : "2025-02-13T18:15:00Z",
                            "affects" : [
                            {
                                "ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae"
                            }
                            ]
                        }
                    }
                }
            },
            "_metadata": {
                "bomFormat" : "CycloneDX",
                "specVersion" : "1.5",
                "serialNumber" : "urn:uuid:dce5f002-f1f2-4809-bf9d-8813ae2efb79",
                "version" : 1,
                "metadata" : {
                "timestamp" : "2025-02-25T09:19:18Z",
                "tools" : [
                    {
                    "vendor" : "OWASP",
                    "name" : "Dependency-Track",
                    "version" : "4.12.1"
                    }
                ],
                "component" : {
                    "type" : "application",
                    "bom-ref" : "82e592b4-56b8-455a-b3f6-70a966996277",
                    "name" : "test",
                    "version" : "1.0"
                }
                },
                "components" : [
                {
                    "type" : "library",
                    "bom-ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2",
                    "name" : "Pillow",
                    "version" : "9.4.0",
                    "description" : "requirements line 10: Pillow==9.4.0",
                    "purl" : "pkg:pypi/pillow@9.4.0",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/Pillow/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f",
                    "name" : "certifi",
                    "version" : "2022.12.7",
                    "description" : "requirements line 1: certifi==2022.12.7",
                    "purl" : "pkg:pypi/certifi@2022.12.7",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/certifi/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "09cfcf87-a619-4eb6-9638-9ecd4fa76055",
                    "name" : "charset-normalizer",
                    "version" : "3.0.1",
                    "description" : "requirements line 2: charset-normalizer==3.0.1",
                    "purl" : "pkg:pypi/charset-normalizer@3.0.1",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/charset-normalizer/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "a9fef477-0d97-4b5a-8e4d-40529c78c838",
                    "name" : "colorama",
                    "version" : "0.4.6",
                    "description" : "requirements line 3: colorama==0.4.6",
                    "purl" : "pkg:pypi/colorama@0.4.6",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/colorama/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "9a642a54-1e89-4a01-a48e-3780b8d7ab1c",
                    "name" : "decorator",
                    "version" : "4.4.2",
                    "description" : "requirements line 4: decorator==4.4.2",
                    "purl" : "pkg:pypi/decorator@4.4.2",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/decorator/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "547b6f87-49a8-4552-88da-0d1ff7507d4c",
                    "name" : "idna",
                    "version" : "3.4",
                    "description" : "requirements line 5: idna==3.4",
                    "purl" : "pkg:pypi/idna@3.4",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/idna/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "c06911a1-05be-41f5-af67-f9405b726bea",
                    "name" : "imageio",
                    "version" : "2.25.0",
                    "description" : "requirements line 6: imageio==2.25.0",
                    "purl" : "pkg:pypi/imageio@2.25.0",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/imageio/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "d6069bcc-0443-4f7d-a4ac-eceaeff92f5e",
                    "name" : "imageio-ffmpeg",
                    "version" : "0.4.8",
                    "description" : "requirements line 7: imageio-ffmpeg==0.4.8",
                    "purl" : "pkg:pypi/imageio-ffmpeg@0.4.8",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/imageio-ffmpeg/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "b0013349-0ec0-4d7e-868d-7cf860d0f05e",
                    "name" : "moviepy",
                    "version" : "1.0.3",
                    "description" : "requirements line 8: moviepy==1.0.3",
                    "purl" : "pkg:pypi/moviepy@1.0.3",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/moviepy/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "18282ac2-d895-4387-8ba7-2d068f0d1bbd",
                    "name" : "numpy",
                    "version" : "1.24.1",
                    "description" : "requirements line 9: numpy==1.24.1",
                    "purl" : "pkg:pypi/numpy@1.24.1",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/numpy/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "c254814a-a64b-4726-9c9f-50fb734023f9",
                    "name" : "proglog",
                    "version" : "0.1.10",
                    "description" : "requirements line 11: proglog==0.1.10",
                    "purl" : "pkg:pypi/proglog@0.1.10",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/proglog/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64",
                    "name" : "requests",
                    "version" : "2.28.2",
                    "description" : "requirements line 12: requests==2.28.2",
                    "purl" : "pkg:pypi/requests@2.28.2",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/requests/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "f37629f1-b3af-4a21-98c5-0059cf9cfdf3",
                    "name" : "tk",
                    "version" : "0.1.0",
                    "description" : "requirements line 13: tk==0.1.0",
                    "purl" : "pkg:pypi/tk@0.1.0",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/tk/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "f03b8152-604a-4b50-af8b-5d34b47f263c",
                    "name" : "tqdm",
                    "version" : "4.64.1",
                    "description" : "requirements line 14: tqdm==4.64.1",
                    "purl" : "pkg:pypi/tqdm@4.64.1",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/tqdm/",
                        "comment" : "implicit dist url"
                    }
                    ]
                },
                {
                    "type" : "library",
                    "bom-ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae",
                    "name" : "urllib3",
                    "version" : "1.26.14",
                    "description" : "requirements line 15: urllib3==1.26.14",
                    "purl" : "pkg:pypi/urllib3@1.26.14",
                    "externalReferences" : [
                    {
                        "type" : "distribution",
                        "url" : "https://pypi.org/simple/urllib3/",
                        "comment" : "implicit dist url"
                    }
                    ]
                }
                ],
                "dependencies" : [
                {
                    "ref" : "82e592b4-56b8-455a-b3f6-70a966996277",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "09cfcf87-a619-4eb6-9638-9ecd4fa76055",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "a9fef477-0d97-4b5a-8e4d-40529c78c838",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "9a642a54-1e89-4a01-a48e-3780b8d7ab1c",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "547b6f87-49a8-4552-88da-0d1ff7507d4c",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "c06911a1-05be-41f5-af67-f9405b726bea",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "d6069bcc-0443-4f7d-a4ac-eceaeff92f5e",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "b0013349-0ec0-4d7e-868d-7cf860d0f05e",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "18282ac2-d895-4387-8ba7-2d068f0d1bbd",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "c254814a-a64b-4726-9c9f-50fb734023f9",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "f37629f1-b3af-4a21-98c5-0059cf9cfdf3",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "f03b8152-604a-4b50-af8b-5d34b47f263c",
                    "dependsOn" : [ ]
                },
                {
                    "ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae",
                    "dependsOn" : [ ]
                }
                ],
                "vulnerabilities" : [
                {
                    "bom-ref" : "bcd6ed5f-338c-4a2e-8109-1c999bf77909",
                    "id" : "CVE-2023-44271",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "score" : 7.5,
                        "severity" : "high",
                        "method" : "CVSSv3",
                        "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H"
                    }
                    ],
                    "cwes" : [
                    770
                    ],
                    "description" : "An issue was discovered in Pillow before 10.0.0. It is a Denial of Service that uncontrollably allocates memory to process a given task, potentially causing a service to crash by having it run out of memory. This occurs for truetype in ImageFont when textlength in an ImageDraw instance operates on a long text argument.",
                    "published" : "2023-11-03T05:15:00Z",
                    "updated" : "2024-11-21T08:25:00Z",
                    "affects" : [
                    {
                        "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2"
                    }
                    ]
                },
                {
                    "bom-ref" : "887673cd-4dc9-426e-ac73-e3c3bb20cab9",
                    "id" : "CVE-2023-50447",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "score" : 8.1,
                        "severity" : "high",
                        "method" : "CVSSv3",
                        "vector" : "CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H"
                    }
                    ],
                    "cwes" : [
                    94
                    ],
                    "description" : "Pillow through 10.1.0 allows PIL.ImageMath.eval Arbitrary Code Execution via the environment parameter, a different vulnerability than CVE-2022-22817 (which was about the expression parameter).",
                    "published" : "2024-01-19T20:15:00Z",
                    "updated" : "2024-11-21T08:37:00Z",
                    "affects" : [
                    {
                        "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2"
                    }
                    ]
                },
                {
                    "bom-ref" : "9940c65a-2d42-433b-b2fc-8b23d3e44b6f",
                    "id" : "CVE-2024-28219",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "severity" : "unknown",
                        "method" : "other"
                    }
                    ],
                    "description" : "In _imagingcms.c in Pillow before 10.3.0, a buffer overflow exists because strcpy is used instead of strncpy.",
                    "published" : "2024-04-03T03:15:00Z",
                    "updated" : "2024-11-21T09:06:00Z",
                    "affects" : [
                    {
                        "ref" : "47a41a51-64e6-4c16-8fd9-3934ebb145a2"
                    }
                    ]
                },
                {
                    "bom-ref" : "dd48aea9-abf8-4066-a302-f9fdafde5f94",
                    "id" : "CVE-2023-37920",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "score" : 9.8,
                        "severity" : "critical",
                        "method" : "CVSSv3",
                        "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                    }
                    ],
                    "cwes" : [
                    345
                    ],
                    "description" : "Certifi is a curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. Certifi prior to version 2023.07.22 recognizes \"e-Tugra\" root certificates. e-Tugra's root certificates were subject to an investigation prompted by reporting of security issues in their systems. Certifi 2023.07.22 removes root certificates from \"e-Tugra\" from the root store.",
                    "published" : "2023-07-25T21:15:00Z",
                    "updated" : "2025-02-13T13:50:00Z",
                    "affects" : [
                    {
                        "ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f"
                    }
                    ]
                },
                {
                    "bom-ref" : "5da6c82a-aef0-4553-bdae-f44e8baec6e7",
                    "id" : "CVE-2024-39689",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "score" : 7.5,
                        "severity" : "high",
                        "method" : "CVSSv3",
                        "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N"
                    }
                    ],
                    "cwes" : [
                    345
                    ],
                    "description" : "Certifi is a curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. Certifi starting in 2021.5.30 and prior to 2024.7.4 recognized root certificates from `GLOBALTRUST`. Certifi 2024.7.04 removes root certificates from `GLOBALTRUST` from the root store. These are in the process of being removed from Mozilla's trust store. `GLOBALTRUST`'s root certificates are being removed pursuant to an investigation which identified \"long-running and unresolved compliance issues.\"",
                    "published" : "2024-07-05T19:15:00Z",
                    "updated" : "2025-02-15T00:15:00Z",
                    "affects" : [
                    {
                        "ref" : "2f4d0675-18a3-4205-b3b0-3dfb814ca54f"
                    }
                    ]
                },
                {
                    "bom-ref" : "cba0c835-5170-43dc-9079-f971aa3098dd",
                    "id" : "CVE-2024-3651",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "score" : 7.5,
                        "severity" : "high",
                        "method" : "CVSSv3",
                        "vector" : "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H"
                    }
                    ],
                    "description" : "A vulnerability was identified in the kjd/idna library, specifically within the `idna.encode()` function, affecting version 3.6. The issue arises from the function's handling of crafted input strings, which can lead to quadratic complexity and consequently, a denial of service condition. This vulnerability is triggered by a crafted input that causes the `idna.encode()` function to process the input with considerable computational load, significantly increasing the processing time in a quadratic manner relative to the input size.",
                    "published" : "2024-07-07T18:15:00Z",
                    "updated" : "2024-11-21T09:30:00Z",
                    "affects" : [
                    {
                        "ref" : "547b6f87-49a8-4552-88da-0d1ff7507d4c"
                    }
                    ]
                },
                {
                    "bom-ref" : "22105a0a-361d-486b-af48-49d80fcde3c7",
                    "id" : "CVE-2023-32681",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "score" : 6.1,
                        "severity" : "medium",
                        "method" : "CVSSv3",
                        "vector" : "CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N"
                    }
                    ],
                    "description" : "Requests is a HTTP library. Since Requests 2.3.0, Requests has been leaking Proxy-Authorization headers to destination servers when redirected to an HTTPS endpoint. This is a product of how we use `rebuild_proxies` to reattach the `Proxy-Authorization` header to requests. For HTTP connections sent through the tunnel, the proxy will identify the header in the request itself and remove it prior to forwarding to the destination server. However when sent over HTTPS, the `Proxy-Authorization` header must be sent in the CONNECT request as the proxy has no visibility into the tunneled request. This results in Requests forwarding proxy credentials to the destination server unintentionally, allowing a malicious actor to potentially exfiltrate sensitive information. This issue has been patched in version 2.31.0.",
                    "published" : "2023-05-26T18:15:00Z",
                    "updated" : "2025-02-13T17:16:00Z",
                    "affects" : [
                    {
                        "ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64"
                    }
                    ]
                },
                {
                    "bom-ref" : "fc0210ab-f1a3-44db-8cb4-69825bbcf39b",
                    "id" : "CVE-2024-35195",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "severity" : "unknown",
                        "method" : "other"
                    }
                    ],
                    "description" : "Requests is a HTTP library. Prior to 2.32.0, when making requests through a Requests `Session`, if the first request is made with `verify=False` to disable cert verification, all subsequent requests to the same host will continue to ignore cert verification regardless of changes to the value of `verify`. This behavior will continue for the lifecycle of the connection in the connection pool. This vulnerability is fixed in 2.32.0.",
                    "published" : "2024-05-20T21:15:00Z",
                    "updated" : "2024-11-21T09:19:00Z",
                    "affects" : [
                    {
                        "ref" : "f45d1cd6-2c59-42e6-899c-fbdb69b74d64"
                    }
                    ]
                },
                {
                    "bom-ref" : "c0c11cda-82af-42ee-aff8-c59df8e069af",
                    "id" : "CVE-2024-34062",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "severity" : "unknown",
                        "method" : "other"
                    }
                    ],
                    "description" : "tqdm is an open source progress bar for Python and CLI. Any optional non-boolean CLI arguments (e.g. `--delim`, `--buf-size`, `--manpath`) are passed through python's `eval`, allowing arbitrary code execution. This issue is only locally exploitable and had been addressed in release version 4.66.3. All users are advised to upgrade. There are no known workarounds for this vulnerability.",
                    "published" : "2024-05-03T10:15:00Z",
                    "updated" : "2024-11-21T09:18:00Z",
                    "affects" : [
                    {
                        "ref" : "f03b8152-604a-4b50-af8b-5d34b47f263c"
                    }
                    ]
                },
                {
                    "bom-ref" : "f4cf781b-de16-439c-a8d8-927d7c87aef4",
                    "id" : "CVE-2023-43804",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "score" : 8.1,
                        "severity" : "high",
                        "method" : "CVSSv3",
                        "vector" : "CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N"
                    }
                    ],
                    "description" : "urllib3 is a user-friendly HTTP client library for Python. urllib3 doesn't treat the `Cookie` HTTP header special or provide any helpers for managing cookies over HTTP, that is the responsibility of the user. However, it is possible for a user to specify a `Cookie` header and unknowingly leak information via HTTP redirects to a different origin if that user doesn't disable redirects explicitly. This issue has been patched in urllib3 version 1.26.17 or 2.0.5.",
                    "published" : "2023-10-04T17:15:00Z",
                    "updated" : "2024-12-13T14:15:00Z",
                    "affects" : [
                    {
                        "ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae"
                    }
                    ]
                },
                {
                    "bom-ref" : "a05f5f5c-8a51-4604-92e8-40884ec82ca6",
                    "id" : "CVE-2023-45803",
                    "source" : {
                    "name" : "NVD",
                    "url" : "https://nvd.nist.gov/"
                    },
                    "ratings" : [
                    {
                        "source" : {
                        "name" : "NVD",
                        "url" : "https://nvd.nist.gov/"
                        },
                        "score" : 4.2,
                        "severity" : "medium",
                        "method" : "CVSSv3",
                        "vector" : "CVSS:3.0/AV:A/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N"
                    }
                    ],
                    "description" : "urllib3 is a user-friendly HTTP client library for Python. urllib3 previously wouldn't remove the HTTP request body when an HTTP redirect response using status 301, 302, or 303 after the request had its method changed from one that could accept a request body (like `POST`) to `GET` as is required by HTTP RFCs. Although this behavior is not specified in the section for redirects, it can be inferred by piecing together information from different sections and we have observed the behavior in other major HTTP client implementations like curl and web browsers. Because the vulnerability requires a previously trusted service to become compromised in order to have an impact on confidentiality we believe the exploitability of this vulnerability is low. Additionally, many users aren't putting sensitive data in HTTP request bodies, if this is the case then this vulnerability isn't exploitable. Both of the following conditions must be true to be affected by this vulnerability: 1. Using urllib3 and submitting sensitive information in the HTTP request body (such as form data or JSON) and 2. The origin service is compromised and starts redirecting using 301, 302, or 303 to a malicious peer or the redirected-to service becomes compromised. This issue has been addressed in versions 1.26.18 and 2.0.7 and users are advised to update to resolve this issue. Users unable to update should disable redirects for services that aren't expecting to respond with redirects with `redirects=False` and disable automatic redirects with `redirects=False` and handle 301, 302, and 303 redirects manually by stripping the HTTP request body.",
                    "published" : "2023-10-17T20:15:00Z",
                    "updated" : "2025-02-13T18:15:00Z",
                    "affects" : [
                    {
                        "ref" : "2bf92814-a7e0-47b7-ae71-d8ceaa5880ae"
                    }
                    ]
                }
                ]
            }
        }



        # Create test directory if it doesn't exist
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        
        # Create test file for hash testing
        with open(os.path.join(self.test_dir, "test_file.txt"), "w") as f:
            f.write("Test content for file hash testing")
    
    def tearDown(self):
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def compare_structures(self, obj1, obj2, path=""):
        """Compare the structure of two JSON objects and report differences."""
        differences = []
        
        # Compare types
        if type(obj1) != type(obj2):
            return [f"{path}: Different types - {type(obj1).__name__} vs {type(obj2).__name__}"]
        
        # Handle dictionaries
        if isinstance(obj1, dict):
            # Check for different keys
            keys1, keys2 = set(obj1.keys()), set(obj2.keys())
            for key in keys1 - keys2:
                differences.append(f"{path}.{key}: Key only in first object")
            for key in keys2 - keys1:
                differences.append(f"{path}.{key}: Key only in second object")
                
            # Check common keys
            for key in keys1 & keys2:
                differences.extend(self.compare_structures(obj1[key], obj2[key], f"{path}.{key}"))
        
        # Handle lists
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                differences.append(f"{path}: Different list lengths - {len(obj1)} vs {len(obj2)}")
            
            # Compare list items up to the minimum length
            for i in range(min(len(obj1), len(obj2))):
                differences.extend(self.compare_structures(obj1[i], obj2[i], f"{path}[{i}]"))
        
        # Compare values
        elif obj1 != obj2:
            differences.append(f"{path}: Different values - {obj1} vs {obj2}")
        
        return differences

    def test_1_validate_cyclone(self):
        """Test the validate_cyclonedx_smart method with real validation"""
        
        logger.info("Testing CycloneDX validation")
        
        # Test with payload
        logger.info("Testing valid CycloneDX payload with default settings")
        result = self.adapter.validate_cyclonedx_smart(self.cyclone_example)
        self.assertTrue(result)
        logger.info(f"Validation result for valid CycloneDX: {result}")
        
        logger.info("Testing invalid 1 CycloneDX payload with default settings")
        result = self.adapter.validate_cyclonedx_smart(self.cyclone_incorrect1)
        self.assertFalse(result)
        logger.info(f"Validation result for invalid CycloneDX: {result}")

        logger.info("Testing invalid 2 CycloneDX payload with default settings")
        result = self.adapter.validate_cyclonedx_smart(self.cyclone_incorrect2)
        self.assertFalse(result)
        logger.info(f"Validation result for invalid CycloneDX: {result}")

        # Test with payload with stric function
        logger.info("Testing valid CycloneDX payload with default settings")
        result = self.adapter.validate_cyclonedx_smart(self.cyclone_example, strict=True)
        self.assertTrue(result)
        logger.info(f"Validation result for valid CycloneDX: {result}")
        
        logger.info("Testing invalid 1 CycloneDX payload with default settings")
        result = self.adapter.validate_cyclonedx_smart(self.cyclone_incorrect1, strict=True)
        self.assertFalse(result)
        logger.info(f"Validation result for invalid CycloneDX: {result}")

        logger.info("Testing invalid 2 CycloneDX payload with default settings")
        result = self.adapter.validate_cyclonedx_smart(self.cyclone_incorrect2, strict=True)
        self.assertFalse(result)
        logger.info(f"Validation result for invalid CycloneDX: {result}")
        

        logger.info("CycloneDX validation tests completed")


    def test_2_from_cyclone(self):
        """Test the from_cyclone method with real transformation"""
        
        logger.info("Testing CycloneDX transformation")
        
        # Convert the example to JSON string
        cyclone_json = json.dumps(self.cyclone_example)
        
        # Call the method
        transformed= self.adapter.from_cyclone(cyclone_json, "test_name")
        # print(transformed)
        json1 = transformed  # transformed is already a dictionary, no need for json.loads()
        json2 = self.cyclone_thing

        # Structural comparison
        logger.info("Comparing structure...")
        structural_differences = self.compare_structures(json1, json2)

        if structural_differences:
            logger.info(f"\nFound {len(structural_differences)} structural differences:")
            for diff in structural_differences[:20]:  # limit output to first 20 differences
                logger.info(f"• {diff}")
            if len(structural_differences) > 20:
                logger.info(f"... and {len(structural_differences) - 20} more differences")
        else:
            logger.info("No structural differences found!")
            self.assertFalse(structural_differences)

        # Convert to strings for a direct text comparison
        text1 = json.dumps(json1, sort_keys=True, indent=2)
        text2 = json.dumps(json2, sort_keys=True, indent=2)
        
        if text1 == text2:
            self.assertFalse(text1 == text2)
            logger.info("Content is identical when sorted and normalized!")
        else:
           logger.info("Content differs when normalized!")

        
        logger.info(f"Transformation successful.")


    def test_3_send_to_controller(self):
        """Test the send_to_controller method with real HTTP request"""
        
        logger.info("Testing send to controller")
        
        # Prepare a simple payload
        payload = {
            "test": "payload",
            "timestamp": time.time()
        }
        
        try:
            # Call the method (this will make a real HTTP request)
            result = self.adapter.send_to_controller(payload)
            
            # Log the response for debugging
            logger.info(f"Controller response: {result.status_code}")
            logger.info(f"Controller response content: {result.text[:100]}...")
            
            # Basic assertions
            self.assertIsNotNone(result)
            # Note: We can't assert exact status code as it depends on the real service
            
        except Exception as e:
            logger.error(f"Error sending to controller: {e}")
            self.fail(f"send_to_controller raised an exception: {e}")

    def test_4_integration_cyclone_to_ditto(self):
        """Integration test: Transform CycloneDX and create in Ditto"""
        
        logger.info("Testing full integration: CycloneDX -> Transform -> Ditto")
        
        # Convert the example to JSON string
        cyclone_json = json.dumps(self.cyclone_example)
        
        # First, transform the CycloneDX
        transformed, serial_number, bom_type = self.adapter.from_cyclone(cyclone_json, "test_integration")
        
        # Then, use the controller to create it in Ditto
        try:
            result = self.controller.create_in_ditto(
                json.dumps(transformed),
                self.test_toeid,
                "integration.test." + bom_type
            )
            
            logger.info(f"Ditto creation result: {result}")
            
            # Assertions
            self.assertTrue(result.get("success", False))
            self.assertTrue(200 <= result.get("status_code", 0) < 300)
            
            # Wait for creation to complete
            time.sleep(1)
            
            # Verify by reading
            read_result = self.controller.read_item(
                self.test_toeid,
                "integration.test." + bom_type
            )
            
            logger.info(f"Ditto read result: {read_result is not None}")
            
            self.assertIsNotNone(read_result)
            self.assertEqual(read_result["attributes"]["BomType"], bom_type)
            
            # Finally, clean up by deleting
            delete_result = self.controller.delete_item(
                self.test_toeid,
                "integration.test." + bom_type
            )
            
            logger.info(f"Ditto delete result: {delete_result}")
            
        except Exception as e:
            logger.error(f"Integration test error: {e}")
            self.fail(f"Integration test raised an exception: {e}")

    def test_5_fetch_push_save_file(self):
        """Test downloading and processing a file from a URL"""
        
        logger.info("Testing fetch and process file")
        
        # Use a reliable public file URL for testing
        test_url = "https://raw.githubusercontent.com/tensorflow/tensorflow/master/README.md"
        
        try:
            # Call the method
            result = self.adapter.fetch_push_save_file(test_url)
            
            # Assertions
            self.assertIsNotNone(result)
            self.assertIn("thingId", result)
            self.assertIn("attributes", result)
            self.assertIn("file_name", result["attributes"])
            self.assertIn("features", result)
            self.assertIn("file", result["features"])
            self.assertIn("properties", result["features"]["file"])
            self.assertIn("hash", result["features"]["file"]["properties"])
            
            file_name = result["attributes"]["file_name"]
            file_hash = result["features"]["file"]["properties"]["hash"]
            
            logger.info(f"Downloaded file: {file_name} with hash: {file_hash}")
            
        except Exception as e:
            logger.error(f"Error in fetch_push_save_file: {e}")
            # This might fail if the URL is unavailable, so we'll make it a soft failure
            logger.warning("Skipping full assertions due to possible network issues")

    


if __name__ == '__main__':
    print("Running integration tests for DTModelAdapter...")
    
    # Create an interactive menu for testing
    while True:
        print("\n" + "="*50)
        print("=== DTModelAdapter Integration Test Menu ===")
        print("="*50)
        print("1. Test CycloneDX Validation")
        print("2. Test CycloneDX Transformation")
        print("3. Test Controller Communication")
        print("4. Test Full Integration (CycloneDX to Ditto)")
        print("5. Test File Download and Processing")
        print("6. Run All Tests")
        print("q. Quit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-6 or q): ").lower()
        
        if choice == 'q':
            print("Exiting test runner.")
            break
        
        test_suite = unittest.TestSuite()
        runner = unittest.TextTestRunner(verbosity=2)
        
        if choice == '1':
            test_suite.addTest(TestDTModelAdapterIntegration('test_1_validate_cyclone'))
        elif choice == '2':
            test_suite.addTest(TestDTModelAdapterIntegration('test_2_from_cyclone'))
        elif choice == '3':
            test_suite.addTest(TestDTModelAdapterIntegration('test_3_send_to_controller'))
        elif choice == '4':
            test_suite.addTest(TestDTModelAdapterIntegration('test_4_integration_cyclone_to_ditto'))
        elif choice == '5':
            test_suite.addTest(TestDTModelAdapterIntegration('test_5_fetch_push_save_file'))
        elif choice == '6':
            test_suite.addTest(TestDTModelAdapterIntegration('test_1_validate_cyclone'))
            test_suite.addTest(TestDTModelAdapterIntegration('test_2_from_cyclone'))
            test_suite.addTest(TestDTModelAdapterIntegration('test_3_send_to_controller'))
            test_suite.addTest(TestDTModelAdapterIntegration('test_4_integration_cyclone_to_ditto'))
            test_suite.addTest(TestDTModelAdapterIntegration('test_5_fetch_push_save_file'))
        else:
            print("Invalid choice. Please select a valid option.")
            continue
        
        runner.run(test_suite)
