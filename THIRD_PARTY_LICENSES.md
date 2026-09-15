# Third-Party Licenses

This file lists all third-party Python packages used by the SDT Service, along with their
respective licenses. All packages are installed via `requirements.txt` at build time.

A runtime dependency (Mosquitto MQTT broker) is also included — it is installed directly
inside the Docker image by the `Dockerfile`.

---

## Python Packages

| Package | Version constraint | License | Source |
|---|---|---|---|
| fastapi | unpinned | MIT | https://github.com/tiangolo/fastapi |
| pydantic | unpinned | MIT | https://github.com/pydantic/pydantic |
| flask | unpinned | BSD-3-Clause | https://github.com/pallets/flask |
| requests | unpinned | Apache-2.0 | https://github.com/psf/requests |
| uvicorn | unpinned | BSD-3-Clause | https://github.com/encode/uvicorn |
| cyclonedx-python-lib | unpinned | Apache-2.0 | https://github.com/CycloneDX/cyclonedx-python-lib |
| gitpython | unpinned | BSD-3-Clause | https://github.com/gitpython-developers/GitPython |
| rdflib | unpinned | BSD-3-Clause | https://github.com/RDFLib/rdflib |
| sseclient-py | unpinned | Apache-2.0 | https://github.com/mpetazzoni/sseclient |
| python-multipart | unpinned | Apache-2.0 | https://github.com/Kludex/python-multipart |
| paho-mqtt | unpinned | EPL-2.0 OR BSD-3-Clause | https://github.com/eclipse/paho.mqtt.python |
| pytest | unpinned | MIT | https://github.com/pytest-dev/pytest |
| cryptography | unpinned | Apache-2.0 OR BSD-3-Clause | https://github.com/pyca/cryptography |
| PyJWT | unpinned | MIT | https://github.com/jpadilla/pyjwt |
| python-dotenv | unpinned | BSD-3-Clause | https://github.com/theskumar/python-dotenv |
| tenacity | unpinned | Apache-2.0 | https://github.com/jd/tenacity |

---

## Runtime Dependency (Docker image only)

| Package | License | Source |
|---|---|---|
| mosquitto | EPL-2.0 | https://github.com/eclipse/mosquitto |

---

## License Summaries

### MIT License
Applies to: **fastapi**, **pydantic**, **pytest**, **PyJWT**

A short, permissive license. Allows use, copy, modify, merge, publish, distribute, sublicense,
and sell copies. The only requirement is that the original copyright notice and license text
are included in all copies or substantial portions of the software.

### BSD-3-Clause License
Applies to: **flask**, **uvicorn**, **gitpython**, **rdflib**, **python-dotenv**,
and optionally **paho-mqtt** and **cryptography**

A permissive license similar to MIT. Requires preservation of the copyright notice, the list
of conditions, and the disclaimer in source and binary forms. The name of the copyright holder
may not be used to endorse derived products without permission.

### Apache-2.0 License
Applies to: **requests**, **cyclonedx-python-lib**, **sseclient-py**, **python-multipart**,
**tenacity**, and optionally **cryptography**

A permissive license that allows use, modification, and distribution. Requires preservation of
copyright and license notices, a NOTICE file where applicable, and a statement of changes made
to modified files. Does not grant trademark rights.

### EPL-2.0 (Eclipse Public License 2.0)
Applies to: **paho-mqtt** (one of its dual-license options), **mosquitto**

A weak copyleft license. Source code of EPL-licensed components and their modifications must be
made available under EPL-2.0 when distributed. EPL-2.0 is compatible with Apache-2.0 when the
EPL component is used as a library (not modified and redistributed).

### Dual-licensed packages

- **paho-mqtt**: distributed under EPL-2.0 OR BSD-3-Clause — consumers may choose either.
- **cryptography**: distributed under Apache-2.0 OR BSD-3-Clause — consumers may choose either.
