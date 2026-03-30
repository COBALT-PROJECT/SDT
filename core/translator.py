import json
import requests
import os
import git
import hashlib
import shutil
import sys
import time
import logging
import traceback
from datetime import datetime

from .util import FileUtils
from .adapter_all import DTModelAdapter
from .unified_file_extractor import file_extractor

class Translator():
    """
    A class to handle translation between connector and SDT


    Methods:

        fetch_push_save_repo(repo_url: str, local_dir: str = 'evidence') -> dict:
            Clones a GitHub repository and saves it in the local directory.

        fetch_push_save_file(github_url: str, local_dir: str = 'evidence') -> dict:
            Fetches a file from GitHub and saves it in the local directory.

        get_file_hash(file_path: str, hash_algorithm: str = 'sha256') -> str:
            Computes the hash of a file.


    """
    def __init__(self):
        print("SDT-translator instance created.")

    # def from_clouditor(self, s):
    #     r = self.__from_clouditor(s)
    #     return r

    # def to_clouditor(self, s):
    #     r = self.__to_clouditor(s)
    #     return r

    # def from_cloud(self, s):
    #     r = self.__from_cloud(s)
    #     return r

    # def __from_clouditor(self, s):
    #     translated=[]
    #     resource = "resource"
    #     attributes = [] #["id", "timestamp"]
    #     resource_attributes = ["@type", "id", "name", "creationTime", "labels", "internetAccessibleEndpoint", "raw"] #["@type", "creationTime", "internetAccessibleEndpoint", "labels", "name", "publicAccess","raw"]
    #     resource_excluded = []
    #     try:

    #         s_data = s
    #         '''
    #         with open(s, 'r') as json_data:
    #             s_data = json.loads(json_data.read())
    #             json_data.close()
    #         '''

    #         entry = {}
    #         #entry["thingId"] = "cobalt:" + s_data["id"]
    #         entry["policyId"] = "cobalt:policy"
    #         entry["definition"] = "cobalt:clouditor-resource:0.0.1"
    #         entry["attributes"] = {}
    #         for i in attributes:
    #             try:
    #                 entry["attributes"][i] = s_data[i]
    #             except Exception as e:
    #                 pass

    #         s_data = s_data[resource]
    #         for i in resource_attributes:
    #             try:
    #                 entry["attributes"][i] = s_data[i]
    #             except Exception as e:
    #                 pass

    #         entry["features"] = {}

    #         for i in s_data:
    #             if i not in resource_attributes:
    #                 if i not in resource_excluded:
    #                     try:
    #                         entry["features"][i] = {}
    #                         entry["features"][i]["properties"] = {}
    #                         if isinstance(s_data[i], dict):
    #                             entry["features"][i]["properties"] = {}
    #                             entry["features"][i]["properties"] = s_data[i]
    #                         else:
    #                             entry["features"][i]["properties"][i] = {}
    #                             entry["features"][i]["properties"][i] = s_data[i]
    #                     except Exception as e:
    #                         pass

    #         # t_json = json.dumps(entry)
    #         # with open('test.json', 'w', encoding='utf-8') as f:
    #         #    json.dump(entry,f,ensure_ascii=False, indent=4)

    #         # print(t_json)
    #         print(entry)
    #         translated.append(entry)
    #         return translated
    #     except Exception as e:
    #         print(e)

    #     # t_json = json.dumps(s_data["resource"])

    #     return None

    # def __to_clouditor(self, s):
    #     resource = "resource"
    #     attributes = [] #["id", "timestamp"]
    #     resource_attributes = ["@type", "id", "name", "creationTime", "labels", "internetAccessibleEndpoint", "raw"] #["@type", "creationTime", "internetAccessibleEndpoint", "labels", "name", "publicAccess","raw"]
    #     resource_excluded = []
    #     try:

    #         s_data = s
    #         '''
    #         with open(s, 'r') as json_data:
    #             s_data = json.loads(json_data.read())
    #             json_data.close()
    #         '''

    #         entry = {}
    #         entry[s_data["definition"]] = []
    #         #entry[s_data["definition"]].append(s_data["attributes"])

    #         tmp = s_data["attributes"]

    #         tmp["properties"] = {}
    #         for i in s_data["features"]:
    #             tmp["properties"][i] = {}
    #             if i in s_data["features"][i]["properties"]:
    #                 tmp["properties"][i] = s_data["features"][i]["properties"][i]
    #             else:
    #                 tmp["properties"][i] = s_data["features"][i]["properties"]

    #         entry[s_data["definition"]].append(tmp)

    #         '''
    #         entry["definition"] = "cobalt:clouditor-resource:0.0.1"
    #         entry["attributes"] = {}
    #         for i in attributes:
    #             try:
    #                 entry["attributes"][i] = s_data[i]
    #             except Exception as e:
    #                 pass

    #         s_data = s_data[resource]
    #         for i in resource_attributes:
    #             try:
    #                 entry["attributes"][i] = s_data[i]
    #             except Exception as e:
    #                 pass

    #         entry["features"] = {}

    #         for i in s_data:
    #             if i not in resource_attributes:
    #                 if i not in resource_excluded:
    #                     try:
    #                         entry["features"][i] = {}
    #                         entry["features"][i]["properties"] = {}
    #                         if isinstance(s_data[i], dict):
    #                             entry["features"][i]["properties"] = {}
    #                             entry["features"][i]["properties"] = s_data[i]
    #                         else:
    #                             entry["features"][i]["properties"][i] = {}
    #                             entry["features"][i]["properties"][i] = s_data[i]
    #                     except Exception as e:
    #                         pass

    #         # t_json = json.dumps(entry)
    #         # with open('test.json', 'w', encoding='utf-8') as f:
    #         #    json.dump(entry,f,ensure_ascii=False, indent=4)
    #         '''
    #         # print(t_json)
    #         print(json.dumps(entry))
    #         #return json.dumps(entry)

    #     except Exception as e:
    #         print(e)

    #     # t_json = json.dumps(s_data["resource"])

    #     return None

    # def __from_cloud(self, s):

    #     translated = []
    #     try:
    #         s_data = s
    #         for i in s_data:
    #             try:

    #                 n = -1
    #                 for j in s_data[i]:
    #                     n += 1

    #                     entry = {}
    #                     # entry["thingId"] = "cobalt:test"
    #                     entry["policyId"] = "cobalt:policy"
    #                     entry["definition"] = "cobalt:clouditor-resource:0.0.1"
    #                     entry["attributes"] = {}
    #                     entry["features"] = {}


    #                     #entry["features"][i]["properties"] = {}

    #                     for k in j:
    #                         if k != "properties":
    #                             entry["attributes"][k] = {}
    #                             entry["attributes"][k] = s_data[i][n][k]
    #                         else:
    #                             for l in s_data[i][n][k]:
    #                                 entry["features"][l] = {}
    #                                 entry["features"][l]["properties"] = {}
    #                                 if isinstance(s_data[i][n][k][l], dict):

    #                                     entry["features"][l]["properties"] = s_data[i][n][k][l]
    #                                 else:
    #                                     entry["features"][l]["properties"][l] = {}
    #                                     entry["features"][l]["properties"][l] = s_data[i][n][k][l]

    #                 '''
    #                 print(entry)
    #                 session = requests.Session()
    #                 session.auth = ("ditto", "ditto")
    #                 r = session.post("http://10.0.1.174:8080/api/2/things/", json=entry, headers={'Content-Type': 'application/json'})
    #                 print(r.json())
    #                 '''

    #                 translated.append(json.dumps(entry))

    #             except Exception as e:
    #                 print(e)

    #         return translated

    #     except Exception as e:
    #         print(e)

    #     # t_json = json.dumps(s_data["resource"])

    #     return None


#===================DEMO METHODS======================
    # def fetch_push_save_repo(self,toeid: str, category:str,  repo_url, local_dir='evidence'):
    #     """
    #     Clones a GitHub repository and saves it in the local directory.
    #     Generates a file tree with hashes for each file.
    #     Overwrites repository if it already exists.
    #     Includes Git modification times for each file.

    #     Args:
    #         repo_url (str): The URL of the GitHub repository.
    #         local_dir (str): The local directory to save the repo. Default is 'evidence'.

    #     Returns:
    #         dict: Transformed thing object with repository metadata and file tree
    #     """
    #     try:
    #         # Extract repo name from URL
    #         repo_name = repo_url.split('/')[-1]
    #         if repo_name.endswith('.git'):
    #             repo_name = repo_name[:-4]

    #         # Use current working directory for local storage
    #         current_dir = os.getcwd()
    #         save_dir = os.path.join(current_dir, local_dir)
    #         repo_path = os.path.join(save_dir, repo_name)

    #         # Create directory if it doesn't exist
    #         os.makedirs(save_dir, exist_ok=True)

    #         # Remove existing repository if it exists
    #         if os.path.exists(repo_path):
    #             print(f"Repository already exists at {repo_path}. Removing...")
    #             shutil.rmtree(repo_path)

    #         # Clone the repository
    #         print(f"Cloning repository {repo_url} to {repo_path}...")
    #         # Check if repo already exists and is a git repository
    #         if os.path.exists(os.path.join(repo_path, '.git')):
    #             print(f"Repository already exists at {repo_path}. Syncing...")
    #             repository = git.Repo(repo_path)
    #             origin = repository.remotes.origin
    #             origin.pull()
    #         else:
    #             # If path exists but is not a git repo, remove it
    #             if os.path.exists(repo_path):
    #                 print(f"Path exists but is not a git repository. Removing...")
    #                 shutil.rmtree(repo_path)

    #             # Clone the repository
    #             print(f"Cloning repository {repo_url} to {repo_path}...")
    #             repository = git.Repo.clone_from(repo_url, repo_path)

    #         # Generate file tree with hashes and modification times
    #         thing =self.generate_things_for_repo(toeid, category, repo_path, repository)

    #         file_tree = self._generate_file_tree_with_hashes_and_times(repo_path, repository)

    #         # # Create transformed thing object
    #         # payload = {
    #         #     "thingId": "toe.ai.repo:b10359fb-7d9e-4bf2-b83b-8b0244a0dd4e",
    #         #     "policyId": "cobalt:policy",
    #         #     "attributes": {
    #         #         "TOE": "cobalt:TOE",
    #         #         "repo_name": repo_name,
    #         #         "github": repo_url,
    #         #         "source": "Repository",
    #         #         "clone_timestamp": self._get_current_timestamp()
    #         #     },
    #         #     "features": {
    #         #         "repository": {
    #         #             "properties": {
    #         #                 "github": repo_url,
    #         #                 "local_path": repo_path,
    #         #                 "last_commit": self._get_last_commit_info(repository)
    #         #             }
    #         #         },
    #         #         "Repository_file_tree": {
    #         #             "properties": file_tree
    #         #         }
    #         #     }
    #         # }
    #         # payload = json.dumps(payload)
    #         # ctrl.create_in_ditto(payload)
    #         return thing

    #     except Exception as e:
    #         raise Exception(f"Failed to clone repository: {str(e)}")

    # def generate_things_for_repo(self, toeid, category, repo_path, repository):
    #     """
    #     Generates a file tree with hashes and modification times for each file in the repository.

    #     Args:
    #         repo_path (str): Path to the local repository.
    #         repository (git.Repo): Git repository object.

    #     Returns:
    #         dict: A dictionary representing the file tree with hashes and modification times.
    #     """
    #     file_info = []

    #     # Generate file tree with hashes and modification times
    #     file_tree = self._generate_file_tree_with_hashes_and_times(repo_path, repository)
    #     file_tree_object = {}
    #     for index, file_item in enumerate(file_tree):
    #         file_tree_object[str(index)] = file_item
    #     print("**************************************************************")
    #     # Create transformed thing object
    #     payload = {
    #         "attributes": {
    #             "toe_id": toeid,
    #             "category": category,
    #             "repo_name": os.path.basename(repo_path),
    #             "github": repo_path,
    #             "sourceType": "Repository",
    #             "clone_timestamp": self._get_current_timestamp()
    #         },
    #         "features": {
    #             "repository": {
    #                 "properties": {
    #                     "github": repo_path,
    #                     "local_path": repo_path,
    #                     "last_commit": self._get_last_commit_info(repository)
    #                 }
    #             },
    #             "Repository_file_tree": {
    #                 "properties": file_tree_object
    #             }
    #         }
    #     }

    #     return json.dumps(payload)




    # def generate_things_for_repo_files(self, repo_path, repository):
    #     """
    #     Generates a file tree with hashes and modification times for each file in the repository.

    #     Args:
    #         repo_path (str): Path to the local repository.
    #         repository (git.Repo): Git repository object.

    #     Returns:
    #         dict: A dictionary representing the file tree with hashes and modification times.
    #     """
    #     file_info = []

    #     for root, dirs, files in os.walk(repo_path):
    #         # Skip .git directory
    #         if '.git' in dirs:
    #             dirs.remove('.git')

    #         for file in files:
    #             file_path = os.path.join(root, file)
    #             file_extension = os.path.splitext(file)[1]

    #             try:
    #                 # Get file hash
    #                 file_hash = self.get_file_hash(file_path)

    #                 # Get last modification time from git
    #                 mod_time = self._get_git_modification_time(repository, os.path.relpath(file_path, repo_path))

    #                 # Store file info as dictionary with extension, path, hash, and modification time
    #                 file_info = {
    #                     "extension": file_extension,
    #                     "path": file_path,
    #                     "hash": file_hash,
    #                     "last_modified": mod_time
    #                 }
    #             except Exception as e:
    #                 file_info = {
    #                     "extension": file_extension,
    #                     "path": file_path,
    #                     "error": f"Error processing file: {str(e)}"
    #                 }

    #             # Create transformed thing object
    #             payload = {
    #                 # "thingId": "toe.ai" + file_extension + ":b10359fb-7d9e-4bf2-b83b-8b0244a0dd4e",
    #                 # "policyId": "cobalt:policy",
    #                 "attributes": {
    #                     "repo_name": os.path.basename(repo_path),
    #                     "repo_path": repo_path
    #                 },
    #                 "features": {
    #                     "file_info": {
    #                         "properties": file_info
    #                     }
    #                 }
    #             }
    #             print("3333333333333333333333333")
    #             print(payload)
    #             # Send payload to Ditto
    #             # ctrl.create_in_ditto(json.dumps(payload))
    #             print("File info sent to Controller.")

    #     return json.dumps(payload)

    # def _generate_file_tree_with_hashes_and_times(self, repo_path, repository):
    #     """
    #     Generates a file list with hashes, modification times, and paths for each file in the repository.

    #     Args:
    #         repo_path (str): Path to the local repository.
    #         repository (git.Repo): Git repository object.

    #     Returns:
    #         list: A list of dictionaries containing file information (name, path, hash, and modification time).
    #     """
    #     file_list = []

    #     for root, dirs, files in os.walk(repo_path):
    #         # Skip .git directory
    #         if '.git' in dirs:
    #             dirs.remove('.git')

    #         for file in files:
    #             file_path = os.path.join(root, file)
    #             rel_file_path = os.path.relpath(file_path, repo_path)

    #             try:
    #                 # Get file hash
    #                 file_hash = self.get_file_hash(file_path)

    #                 # Get last modification time from git
    #                 mod_time = self._get_git_modification_time(repository, rel_file_path)

    #                 # Add file info to the list with the full path
    #                 file_list.append({
    #                     "name": file,  # Add the name of the file
    #                     "path": file_path,  # Use full path instead of relative path
    #                     "hash": file_hash,
    #                     "last_modified": mod_time
    #                 })
    #             except Exception as e:
    #                 file_list.append({
    #                     "name": file,  # Add the name of the file
    #                     "path": file_path,  # Use full path instead of relative path
    #                     "error": f"Error processing file: {str(e)}"
    #                 })

    #     return file_list

    # def _get_git_modification_time(self, repository, file_path):
    #     """
    #     Gets the last modification time of a file from git history.

    #     Args:
    #         repository (git.Repo): Git repository object.
    #         file_path (str): Relative path to the file from repository root.

    #     Returns:
    #         str: ISO formatted timestamp of last modification.
    #     """
    #     try:
    #         # Get the last commit that modified the file
    #         logs = repository.git.log('-1', '--format=%aI', '--', file_path)
    #         if logs:
    #             return logs.strip()
    #         else:
    #             # If no git history for the file, return current time
    #             return datetime.now().isoformat()
    #     except Exception as e:
    #         return f"Error getting modification time: {str(e)}"

    # def _get_last_commit_info(self, repository):
    #     """
    #     Gets information about the last commit in the repository.

    #     Args:
    #         repository (git.Repo): Git repository object.

    #     Returns:
    #         dict: Information about the last commit.
    #     """
    #     try:
    #         commit = repository.head.commit
    #         return {
    #             "hash": commit.hexsha,
    #             "author": f"{commit.author.name} <{commit.author.email}>",
    #             "date": commit.committed_datetime.isoformat(),
    #             "message": commit.message.strip()
    #         }
    #     except Exception as e:
    #         return {"error": f"Error getting commit info: {str(e)}"}

    # def _get_current_timestamp(self):
    #     """
    #     Gets the current timestamp in ISO format.

    #     Returns:
    #         str: Current timestamp in ISO format.
    #     """
    #     return datetime.now().isoformat()

    # def fetch_push_save_file(self, github_url, local_dir='evidence'):
    #     """
    #     Fetches a file from GitHub and saves it in the local directory.

    #     Args:
    #         github_url (str): The URL of the file on GitHub.
    #         local_dir (str): The local directory to save the file. Default is 'evidence'.

    #     Returns:
    #         dict: Transformed thing object with file metadata
    #     """
    #     try:
    #         # Use a directory within the current working directory that you have permissions to
    #         current_dir = os.getcwd()
    #         file_name = github_url.split('/')[-1]
    #         file_extension = os.path.splitext(file_name)[1]

    #         # Create directory if it doesn't exist
    #         save_dir = os.path.join(current_dir, local_dir)
    #         os.makedirs(save_dir, exist_ok=True)

    #         # Set full file path
    #         local_path = os.path.join(save_dir, file_name)

    #         # Convert GitHub blob URL to raw content URL
    #         if "github.com" in github_url and "/blob/" in github_url:
    #             raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    #         else:
    #             raw_url = github_url

    #         # Download file
    #         response = requests.get(raw_url)
    #         response.raise_for_status()  # Raises error for bad status codes

    #         # Save file
    #         with open(local_path, 'wb') as file:
    #             file.write(response.content)

    #         # Get file hash
    #         downloaded_file_hash = self.get_file_hash(local_path)

    #         # Determine file type and component
    #         file_types = {
    #             '.h5': ("toe.ai.h5", "AI Model"),
    #             '.ipynb': ("toe.ai.ipynb", "AI Notebook"),
    #             '.json': ("toe.cloud.json", "Cloud")
    #         }
    #         ftype, component = file_types.get(file_extension, ("toe.unknown", "Unknown"))

    #         # Create transformed thing object
    #         return {
    #             "thingId": ftype,
    #             "policyId": "cobalt:policy",
    #             "attributes": {
    #                 "TOE": "cobalt:TOE",
    #                 "file_name": file_name,
    #                 "github": github_url,
    #                 "source": component
    #             },
    #             "features": {
    #                 "file": {
    #                     "properties": {
    #                         "github": github_url,
    #                         "hash": downloaded_file_hash,
    #                         "link": local_path
    #                     }
    #                 }
    #             }
    #         }

    #     except requests.RequestException as e:
    #         raise Exception(f"Failed to fetch file: {str(e)}")
    #     except IOError as e:
    #         raise Exception(f"Failed to save file: {str(e)}")

    # def get_file_hash(self, file_path, hash_algorithm='sha256'):
    #     """
    #     Computes the hash of a file.

    #     Args:
    #         file_path (str): The path to the file.
    #         hash_algorithm (str): The hash algorithm to use. Default is 'sha256'.

    #     Returns:
    #         str: The computed hash of the file.
    #     """
    #     hash_func = hashlib.new('sha256')
    #     with open(file_path, 'rb') as f:
    #         for chunk in iter(lambda: f.read(4096), b""):
    #             hash_func.update(chunk)
    #     return hash_func.hexdigest()

#==========================IDS Connector File Processing Methods==========================

    def process_received_file(self, file_path: str, filename: str, toe_id: str, category: str, metadata: str = "{}"):
        """
        Processes received files based on their type and returns thing format for Ditto
        """
        print(f"Translator: Processing received file {filename} at {file_path}")

        try:
            file_ext = filename.split('.')[-1].lower()

            # Route to appropriate processor based on file extension
            processors = {
                'h5': self._process_h5_file,
                'py': self._process_python_file,
                'ipynb': self._process_notebook_file,
                'txt': self._process_text_file
            }

            processor = processors.get(file_ext, self._process_generic_file)
            result = processor(file_path, toe_id, category, metadata)

            print(f"Translator: File processing completed for {filename}")
            return result

        except Exception as e:
            print(f"Error in translator processing file: {e}")
            raise Exception(f"File processing failed: {str(e)}")

    def download_and_process_file(self, file_url: str, toe_id: str, category: str):
        """
        Downloads file from URL and processes it, returning thing format
        """
        print(f"Translator: Downloading file from {file_url}")

        try:
            response = requests.get(file_url, timeout=30)
            response.raise_for_status()

            # Extract filename from URL
            filename = file_url.split('/')[-1]
            if not filename:
                filename = f"downloaded_file_{int(time.time())}"

            # Create evidence directory if it doesn't exist
            os.makedirs("evidence", exist_ok=True)

            # Save file
            file_path = f"evidence/{toe_id}_{category}_{filename}"
            with open(file_path, 'wb') as f:
                f.write(response.content)

            # Process the file
            thing_data = self.process_received_file(file_path, filename, toe_id, category)

            print(f"Translator: File downloaded and processed successfully")
            return {
                "thing_data": thing_data,
                "file_path": file_path,
                "message": "File downloaded and processed"
            }

        except Exception as e:
            print(f"Error downloading and processing file: {e}")
            raise Exception(f"Download and processing failed: {str(e)}")

    def _process_h5_file(self, file_path: str, toe_id: str, category: str, metadata: str = "{}"):
        """Process .h5 AI model files - returns thing format"""
        return json.dumps({
            "attributes": {
                "toe_id": toe_id,
                "category": category,
                "file_path": file_path,
                "file_type": "h5",
                "model_framework": "tensorflow",
                "file_hash": self.get_file_hash(file_path),
                "processing_timestamp": time.time(),
                "metadata": metadata
            },
            "features": {
                "ai_model": {
                    "properties": {
                        "model_type": "neural_network",
                        "file_size": os.path.getsize(file_path),
                        "framework": "tensorflow"
                    }
                }
            }
        })

    def _process_python_file(self, file_path: str, toe_id: str, category: str, metadata: str = "{}"):
        """Process .py Python files - returns thing format"""
        return json.dumps({
            "attributes": {
                "toe_id": toe_id,
                "category": category,
                "file_path": file_path,
                "file_type": "py",
                "language": "python",
                "file_hash": self.get_file_hash(file_path),
                "processing_timestamp": time.time(),
                "metadata": metadata
            },
            "features": {
                "source_code": {
                    "properties": {
                        "file_size": os.path.getsize(file_path),
                        "line_count": self._count_lines(file_path),
                        "language": "python"
                    }
                }
            }
        })

    def _process_notebook_file(self, file_path: str, toe_id: str, category: str, metadata: str = "{}"):
        """Process .ipynb Jupyter notebook files - returns thing format"""
        return json.dumps({
            "attributes": {
                "toe_id": toe_id,
                "category": category,
                "file_path": file_path,
                "file_type": "ipynb",
                "notebook_type": "jupyter",
                "file_hash": self.get_file_hash(file_path),
                "processing_timestamp": time.time(),
                "metadata": metadata
            },
            "features": {
                "notebook": {
                    "properties": {
                        "file_size": os.path.getsize(file_path),
                        "notebook_type": "jupyter"
                    }
                }
            }
        })

    def _process_text_file(self, file_path: str, toe_id: str, category: str, metadata: str = "{}"):
        """Process .txt text files - returns thing format"""
        return json.dumps({
            "attributes": {
                "toe_id": toe_id,
                "category": category,
                "file_path": file_path,
                "file_type": "txt",
                "content_type": "text",
                "file_hash": self.get_file_hash(file_path),
                "processing_timestamp": time.time(),
                "metadata": metadata
            },
            "features": {
                "document": {
                    "properties": {
                        "file_size": os.path.getsize(file_path),
                        "line_count": self._count_lines(file_path),
                        "content_type": "text"
                    }
                }
            }
        })

    def _process_generic_file(self, file_path: str, toe_id: str, category: str, metadata: str = "{}"):
        """Process generic files - returns thing format"""
        return json.dumps({
            "attributes": {
                "toe_id": toe_id,
                "category": category,
                "file_path": file_path,
                "file_type": "unknown",
                "file_hash": self.get_file_hash(file_path),
                "processing_timestamp": time.time(),
                "metadata": metadata
            },
            "features": {
                "generic_file": {
                    "properties": {
                        "file_size": os.path.getsize(file_path)
                    }
                }
            }
        })

    def _count_lines(self, file_path: str) -> int:
        """Count lines in a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    #===================IDS CONNECTOR METHODS======================

    # def process_ids_response(self, ids_response: dict, toe_id: str):
    #     """
    #     Process IDS connector response and route to appropriate handler

    #     Args:
    #         ids_response: Response from IDS connector GET /api/IDSconnector/get_data_request
    #         toe_id: Target of Evaluation ID

    #     Returns:
    #         list: List of processed things
    #     """
    #     logger = logging.getLogger(__name__)

    #     logger.info(f"Processing IDS response for TOE: {toe_id}")

    #     processed_things = []

    #     try:
    #         # Parse the IDS response
    #         data_type = ids_response.get("data_type")
    #         data_str = ids_response.get("data")

    #         if data_type != "json":
    #             logger.error(f"Unsupported data type: {data_type}")
    #             return processed_things

    #         # Parse the data string
    #         data = json.loads(data_str)

    #         # Check if it's a list of resources or single resource
    #         resources = data.get("resources", [data]) if isinstance(data, dict) else [data]

    #         for resource in resources:
    #             # Extract resource metadata
    #             resource_id = resource.get("@id", "")
    #             resource_type = resource.get("@type", "")
    #             title = resource.get("ids:title", [{}])[0].get("@value", "Unknown")
    #             description = resource.get("ids:description", [{}])[0].get("@value", "")

    #             logger.info(f"Processing resource: {title} (Type: {resource_type})")

    #             # Detect artifact type from description or content
    #             artifact_type = self._detect_artifact_type_from_ids(resource, description)

    #             if artifact_type:
    #                 logger.info(f"Detected artifact type: {artifact_type}")
    #                 thing = self._process_ids_artifact(resource, toe_id, artifact_type)
    #                 if thing:
    #                     processed_things.append(thing)
    #             else:
    #                 # Store as generic file
    #                 logger.info(f"Storing as generic evidence file")
    #                 thing = self._store_ids_evidence_file(resource, toe_id)
    #                 if thing:
    #                     processed_things.append(thing)

    #         return processed_things

    #     except Exception as e:
    #         logger.error(f"Error processing IDS response: {e}")
    #         logger.error(traceback.format_exc())
    #         return processed_things

    def process_ids_response(self, ids_response: dict, toe_id: str):
        """
        Process IDS connector response and extract all files with metadata.
        Route each file to appropriate processing based on type:
        - OSCAL, ARM, BOMs: Transform and create structured things
        - Other files: Create file-based things

        Args:
            ids_response: Response from IDS connector GET /api/IDSconnector/get_data_request
            toe_id: Target of Evaluation ID

        Returns:
            list: List of processed things
        """
        logger = logging.getLogger(__name__)

        logger.info(f"Processing IDS response for TOE: {toe_id}")

        processed_things = []

        try:
            # Ensure evidence directory exists
            evidence_dir = "/home/sdtm/SDTM/SDT/evidence"
            os.makedirs(evidence_dir, exist_ok=True)

            # Extract data from IDS response
            data_type = ids_response.get("data_type")
            data_str = ids_response.get("data")

            logger.info(f"Processing IDS response with data_type: {data_type}")
            logger.info(f"Data string length: {len(data_str) if data_str else 0}")

            if not data_str:
                logger.error("No data in IDS response")
                return processed_things

            # Check if data is JSON
            if data_type == "json":
                try:
                    data = json.loads(data_str)
                    logger.info(f"Parsed JSON data type: {type(data)}")
                    logger.info(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")

                    # Handle consumer response format with resource and extracted_file
                    if isinstance(data, dict) and "resource" in data and "extracted_file" in data:
                        # Extract from the resource directly, not the consumer's extracted_file
                        resource = data["resource"]
                        processed_things.extend(self._process_resource_directly(resource, toe_id))

                    # Handle consumer response with multiple files
                    elif isinstance(data, dict) and "files" in data:
                        logger.info("Detected consumer response format with multiple files")
                        files_data = data["files"]

                        for file_item in files_data:
                            if "resource" in file_item:
                                resource = file_item["resource"]
                                processed_things.extend(self._process_resource_directly(resource, toe_id))
                            else:
                                logger.warning("File item missing resource, skipping")

                    # Check if it's a list of resources or single resource (original logic)
                    elif isinstance(data, dict) and "resources" in data:
                        resources = data["resources"]
                        logger.info(f"Found {len(resources)} resources in IDS response")

                        for resource in resources:
                            logger.info(f"Processing resource: {resource.get('@id', 'unknown')}")
                            processed_things.extend(self._process_resource_directly(resource, toe_id))

                    else:
                        # Single resource or unknown format
                        resources = [data] if isinstance(data, dict) else [data]

                        for resource in resources:
                            processed_things.extend(self._process_resource_directly(resource, toe_id))

                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON data, treating as base64 encoded file")
                    # Fall through to file extraction

            # For non-JSON data types or failed JSON parsing, use unified extractor
            if data_type != "json" or (data_type == "json" and not processed_things):
                logger.info("Using unified file extractor for data processing")

                # Use the unified file extractor
                extractor = file_extractor()
                file_data, metadata, data_type_result = extractor.extract_file_from_json(ids_response)
                if file_data:
                    # Save the extracted file to /evidence directory
                    filename = metadata.get("filename", f"extracted_file_{toe_id}")
                    # Add appropriate extension based on data_type_result
                    if not os.path.splitext(filename)[1]:
                        if "zip" in data_type_result.lower():
                            filename += ".zip"
                        elif "ipynb" in data_type_result.lower():
                            filename += ".ipynb"
                        elif "py" in data_type_result.lower():
                            filename += ".py"
                        elif "json" in data_type_result.lower():
                            filename += ".json"

                    file_path = os.path.join(evidence_dir, filename)
                    saved_path = extractor.save_file(file_data, metadata, data_type_result, file_path)
                    logger.info(f"Saved extracted file to: {saved_path}")

                    file_info = {
                        "resource_id": f"{toe_id}_extracted_{hashlib.md5(str(metadata).encode()).hexdigest()[:8]}",
                        "title": metadata.get("filename", "Extracted File"),
                        "format": data_type_result,
                        "data_size": len(file_data),
                        "permission": "read",
                        "created": metadata.get("upload_timestamp", datetime.utcnow().isoformat() + "Z"),
                        "updated": metadata.get("upload_timestamp", datetime.utcnow().isoformat() + "Z"),
                        "file_path": saved_path,
                        "filename": filename
                    }
                    # Create Ditto thing from extracted file metadata
                    thing = self._create_thing_from_metadata(file_info, toe_id)
                    if thing:
                        processed_things.append(thing)

            return processed_things

        except Exception as e:
            logger.error(f"Error processing IDS response: {e}")
            logger.error(traceback.format_exc())
            return processed_things

    def _process_resource_directly(self, resource: dict, toe_id: str):
        """
        Process a single IDS resource directly by extracting embedded file from ids:description.

        Args:
            resource: IDS resource dictionary
            toe_id: Target of Evaluation ID

        Returns:
            list: List of processed things
        """
        logger = logging.getLogger(__name__)
        processed_things = []

        logger.info(f"Processing resource directly: {resource.get('@id', 'unknown')}")

        try:
            # Extract embedded file data from ids:description
            descriptions = resource.get("ids:description", [])
            if not descriptions:
                logger.warning("No description found in resource")
                return processed_things

            description_value = descriptions[0].get("@value", "{}")
            logger.info(f"Raw description value: {description_value[:200]}...")

            # Parse the description as JSON to get embedded file data
            try:
                # Handle multiple-encoded JSON (escaped quotes)
                description_to_parse = description_value
                if description_value.startswith('{') and '\\\\"' in description_value:
                    logger.info("Detected multiple-encoded JSON, unescaping")
                    # Unescape twice for double-encoded JSON
                    description_to_parse = description_value.replace('\\\\"', '"')
                    logger.info(f"Unescaped once: {description_to_parse[:200]}...")
                    description_to_parse = description_to_parse.replace('\\"', '"')
                    logger.info(f"Unescaped twice: {description_to_parse[:200]}...")

                embedded_data = json.loads(description_to_parse)
                logger.info(f"Successfully parsed embedded data, type: {embedded_data.get('type', 'unknown')}")
            except json.JSONDecodeError as e:
                logger.warning(f"Description is not valid JSON after unescaping: {e}")
                logger.warning(f"Description content: {description_value[:500]}")
                return processed_things

            # Check if this contains embedded file data
            if ("data" in embedded_data or "content" in embedded_data) and "metadata" in embedded_data:
                logger.info("Found embedded file data in resource description")

                # Use unified extractor on the embedded data
                extractor = file_extractor()
                file_data, metadata, data_type_result = extractor.extract_file_from_json(embedded_data)

                logger.info(f"Extractor returned: file_data={type(file_data)}, len={len(file_data) if file_data else 0}, metadata={metadata}, data_type={data_type_result}")

                if file_data:
                    # Determine filename with correct extension
                    filename = metadata.get("filename", f"resource_file_{toe_id}")
                    mime_type = metadata.get("mime_type", "")

                    # Add extension if missing based on type
                    if not os.path.splitext(filename)[1]:
                        if "python" in mime_type or "py" in filename:
                            filename += ".py"
                        elif "ipynb" in mime_type or "jupyter" in mime_type:
                            filename += ".ipynb"
                        elif "zip" in mime_type:
                            filename += ".zip"
                        elif "json" in mime_type:
                            filename += ".json"

                    evidence_dir = "/home/sdtm/SDTM/SDT/evidence"
                    file_path = os.path.join(evidence_dir, filename)
                    saved_path = extractor.save_file(file_data, metadata, data_type_result, file_path)
                    logger.info(f"Saved embedded file to: {saved_path}")

                    file_info = {
                        "resource_id": resource.get("@id", f"{toe_id}_resource_{hashlib.md5(str(resource).encode()).hexdigest()[:8]}"),
                        "title": resource.get("ids:title", [{}])[0].get("@value", filename),
                        "format": data_type_result,
                        "data_size": len(file_data) if isinstance(file_data, (str, bytes)) else 0,
                        "permission": "read",
                        "created": resource.get("ids:created", {}).get("@value", datetime.utcnow().isoformat() + "Z"),
                        "updated": resource.get("ids:modified", {}).get("@value", datetime.utcnow().isoformat() + "Z"),
                        "file_path": saved_path,
                        "filename": filename,
                        "sourceType": "ids_embedded_file"
                    }

                    # Create Ditto thing from file metadata
                    thing = self._create_thing_from_metadata(file_info, toe_id)
                    if thing:
                        processed_things.append(thing)
                else:
                    logger.warning("Failed to extract file data from resource")
            else:
                logger.info("No embedded file data found, storing as generic IDS evidence")
                # Store the resource itself as evidence
                thing = self._store_ids_evidence_file(resource, toe_id)
                if thing:
                    processed_things.append(thing)

        except Exception as e:
            logger.error(f"Error processing resource directly: {e}")
            logger.error(traceback.format_exc())

        return processed_things
        """
        Process a single extracted file from consumer response.
        Determines file type and routes to appropriate processing.

        Args:
            extracted_file: The extracted_file object from consumer response
            resource: The resource metadata from consumer response
            toe_id: Target of Evaluation ID

        Returns:
            list: List of processed things (usually one thing per file)
        """
        logger = logging.getLogger(__name__)
        processed_things = []

        try:
            if not extracted_file.get("success"):
                logger.warning("Extracted file indicates failure, skipping")
                return processed_things

            file_data = extracted_file.get("data")
            metadata = extracted_file.get("metadata", {})

            if not file_data:
                logger.warning("No file data in extracted_file")
                return processed_things

            # Get resource metadata
            resource_id = resource.get("@id", "")
            resource_type = resource.get("@type", "")
            title = resource.get("ids:title", [{}])[0].get("@value", "Unknown")
            description = resource.get("ids:description", [{}])[0].get("@value", "")

            logger.info(f"Processing extracted file: {title}")

            # Determine file type and content
            file_type = metadata.get("type", "unknown")
            mime_type = metadata.get("mime_type", "")

            # Check if this is a structured data format that needs transformation
            if self._is_structured_data_format(file_data, metadata, description):
                logger.info("Detected structured data format, attempting transformation")

                # Try to parse the file data as JSON for transformation
                try:
                    if isinstance(file_data, str):
                        # If it's a string, try to parse as JSON
                        structured_data = json.loads(file_data)
                    else:
                        # If it's bytes, decode and parse
                        structured_data = json.loads(file_data.decode('utf-8'))

                    # Detect artifact type from the structured data
                    artifact_type = self._detect_artifact_type_from_content(structured_data, metadata, description)

                    if artifact_type:
                        logger.info(f"Detected artifact type: {artifact_type} for transformation")

                        # Create a synthetic IDS resource for transformation
                        synthetic_resource = self._create_synthetic_resource(resource, metadata, structured_data)

                        # Process through appropriate transformer
                        thing = self._process_ids_artifact(synthetic_resource, toe_id, artifact_type)
                        if thing:
                            processed_things.append(thing)
                            logger.info(f"Created transformed thing for {artifact_type}")
                        else:
                            logger.warning(f"Failed to transform {artifact_type}, falling back to file storage")
                            # Fall through to file storage
                    else:
                        logger.info("No specific artifact type detected, storing as file")

                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.info(f"File is not JSON-structured, storing as regular file: {e}")

            # Store as regular file if not structured or transformation failed
            if not processed_things:
                logger.info("Storing extracted file to disk and creating file thing")

                # Save the file directly
                filename = metadata.get("filename", f"extracted_file_{toe_id}")
                # Add appropriate extension if missing
                if not os.path.splitext(filename)[1]:
                    if file_type == "text":
                        filename += ".txt"
                    elif "zip" in mime_type:
                        filename += ".zip"
                    elif "ipynb" in mime_type or "jupyter" in mime_type:
                        filename += ".ipynb"
                    elif "python" in mime_type:
                        filename += ".py"
                    elif "json" in mime_type:
                        filename += ".json"

                evidence_dir = "/home/sdtm/SDTM/SDT/evidence"
                file_path = os.path.join(evidence_dir, filename)

                try:
                    # Write the file
                    mode = 'wb' if isinstance(file_data, bytes) else 'w'
                    with open(file_path, mode) as f:
                        f.write(file_data)
                    logger.info(f"Saved extracted file to: {file_path}")

                    file_info = {
                        "resource_id": f"{toe_id}_extracted_{hashlib.md5(str(metadata).encode()).hexdigest()[:8]}",
                        "title": metadata.get("filename", title),
                        "format": file_type,
                        "data_size": len(file_data) if isinstance(file_data, (str, bytes)) else 0,
                        "permission": "read",
                        "created": metadata.get("extraction_timestamp", datetime.utcnow().isoformat() + "Z"),
                        "updated": metadata.get("extraction_timestamp", datetime.utcnow().isoformat() + "Z"),
                        "file_path": file_path,
                        "filename": filename,
                        "sourceType": "extracted_file"
                    }

                    # Create Ditto thing from extracted file metadata
                    thing = self._create_thing_from_metadata(file_info, toe_id)
                    if thing:
                        processed_things.append(thing)
                        logger.info(f"Created file thing for extracted file: {filename}")

                except Exception as e:
                    logger.error(f"Failed to save extracted file: {e}")

        except Exception as e:
            logger.error(f"Error processing extracted file: {e}")
            logger.error(traceback.format_exc())

        return processed_things

    def _is_structured_data_format(self, file_data, metadata: dict, description: str):
        """
        Determine if the file contains structured data that should be transformed.

        Args:
            file_data: The raw file data
            metadata: File metadata
            description: Resource description

        Returns:
            bool: True if this appears to be structured data for transformation
        """
        # Check metadata indicators
        mime_type = metadata.get("mime_type", "").lower()
        file_type = metadata.get("type", "").lower()

        # JSON-based formats are candidates for transformation
        if "json" in mime_type or file_type in ["json", "cyclonedx", "oscal", "arm"]:
            return True

        # Check if description contains structured data hints
        if description:
            try:
                desc_data = json.loads(description)
                if any(key in desc_data for key in ["bomFormat", "component-definition", "$schema", "cloudServiceId"]):
                    return True
            except:
                pass

        # Check file content for JSON structure
        try:
            if isinstance(file_data, str):
                test_data = json.loads(file_data)
            elif isinstance(file_data, bytes):
                test_data = json.loads(file_data.decode('utf-8'))
            else:
                return False

            # If it's valid JSON, check for known structured formats
            if isinstance(test_data, dict):
                if any(key in test_data for key in ["bomFormat", "specVersion", "component-definition", "component", "$schema"]):
                    return True
        except:
            pass

        return False

    def _detect_artifact_type_from_content(self, content: dict, metadata: dict, description: str):
        """
        Detect artifact type from actual content data.

        Args:
            content: Parsed content data
            metadata: File metadata
            description: Resource description

        Returns:
            str: Artifact type ('cyclonedx', 'oscal', 'arm', 'clouditor') or None
        """
        # Check content for CycloneDX identifiers
        if "bomFormat" in content or "specVersion" in content:
            return "cyclonedx"

        # Check for OSCAL identifiers
        if "component-definition" in content or "component" in content:
            return "oscal"

        # Check for ARM template identifiers
        if "$schema" in content and "microsoft.com/schemas" in str(content.get("$schema", "")).lower():
            return "arm"

        # Check for Clouditor evidence
        if "cloudServiceId" in content or "toolId" in content:
            return "clouditor"

        # Check description for type hints
        if description:
            try:
                desc_data = json.loads(description)
                return self._detect_artifact_type_from_content(desc_data, metadata, "")
            except:
                pass

        return None

    def _create_synthetic_resource(self, original_resource: dict, metadata: dict, content: dict):
        """
        Create a synthetic IDS resource for transformation purposes.

        Args:
            original_resource: Original resource from consumer
            metadata: File metadata
            content: Parsed content data

        Returns:
            dict: Synthetic IDS resource
        """
        synthetic = dict(original_resource)  # Copy original

        # Update description with the actual content
        synthetic["ids:description"] = [{"@value": json.dumps(content)}]

        # Update title if not present
        if not synthetic.get("ids:title"):
            filename = metadata.get("filename", "Structured Data")
            synthetic["ids:title"] = [{"@value": filename}]

        return synthetic
        """
        Process IDS connector response and route to appropriate handler

        Args:
            ids_response: Response from IDS connector GET /api/IDSconnector/get_data_request
            toe_id: Target of Evaluation ID

        Returns:
            list: List of processed things
        """
        logger = logging.getLogger(__name__)

        logger.info(f"Processing IDS response for TOE: {toe_id}")

        processed_things = []

        try:
            # Parse the IDS response
            data_type = ids_response.get("data_type")
            data_str = ids_response.get("data")

            if data_type != "json":
                logger.error(f"Unsupported data type: {data_type}")
                return processed_things

            # Parse the data string
            data = json.loads(data_str)

            # Check if it's a list of resources or single resource
            resources = data.get("resources", [data]) if isinstance(data, dict) else [data]

            for resource in resources:
                # Extract resource metadata
                resource_id = resource.get("@id", "")
                resource_type = resource.get("@type", "")
                title = resource.get("ids:title", [{}])[0].get("@value", "Unknown")
                description = resource.get("ids:description", [{}])[0].get("@value", "")

                logger.info(f"Processing resource: {title} (Type: {resource_type})")

                # Detect artifact type from description or content
                artifact_type = self._detect_artifact_type_from_ids(resource, description)

                if artifact_type:
                    logger.info(f"Detected artifact type: {artifact_type}")
                    thing = self._process_ids_artifact(resource, toe_id, artifact_type)
                    if thing:
                        processed_things.append(thing)
                else:
                    # Store as generic file
                    logger.info(f"Storing as generic evidence file")
                    thing = self._store_ids_evidence_file(resource, toe_id)
                    if thing:
                        processed_things.append(thing)

            return processed_things

        except Exception as e:
            logger.error(f"Error processing IDS response: {e}")
            logger.error(traceback.format_exc())
            return processed_things

    def _create_thing_from_metadata(self, file_info: dict, toe_id: str):
        """
        Create a Ditto thing from file metadata extracted by unified extractor

        Args:
            file_info: Dictionary containing file metadata from extractor
            toe_id: Target of Evaluation ID

        Returns:
            str: JSON string of Ditto thing
        """
        logger = logging.getLogger(__name__)

        try:
            # Extract metadata fields
            resource_id = file_info.get("resource_id") or f"{toe_id}_{hashlib.md5(file_info.get('filename', '').encode()).hexdigest()[:8]}"
            title = file_info.get("title", "Unknown")
            file_format = file_info.get("format", "")
            data_size = file_info.get("data_size", 0)
            permission = file_info.get("permission", "")
            created = file_info.get("created") or datetime.utcnow().isoformat() + "Z"
            updated = file_info.get("updated") or datetime.utcnow().isoformat() + "Z"
            file_path = file_info.get("file_path", "")
            filename = file_info.get("filename", "")

            # Determine category based on file extension or format
            category = "AI" # Default category for extracted files
            if file_format:
                if "zip" in file_format.lower():
                    category = "AI"
                elif "ipynb" in file_format.lower():
                    category = "AI"
                elif "py" in file_format.lower():
                    category = "AI"

            # Create Ditto thing
            thing = {
                "thingId": f"cobalt:{toe_id}:{resource_id or filename}",
                "policyId": "cobalt:policy",
                "definition": "cobalt:evidence-file:1.0.0",
                "attributes": {
                    "toe_id": toe_id,
                    "category": category,
                    "source": "ids_connector",
                    "resource_id": resource_id,
                    "title": title,
                    "format": file_format,
                    "data_size": data_size,
                    "permission": permission,
                    "created": created,
                    "updated": updated,
                    "file_path": file_path,
                    "filename": filename,
                    "sourceType": "extracted_file",
                    "transformedAt": datetime.utcnow().isoformat() + "Z"
                },
                "features": {
                    "file_metadata": {
                        "properties": {
                            "size": data_size,
                            "type": file_format,
                            "path": file_path,
                            "permissions": permission
                        }
                    },
                    "timestamps": {
                        "properties": {
                            "created": created,
                            "updated": updated,
                            "transformed": datetime.utcnow().isoformat() + "Z"
                        }
                    }
                }
            }

            logger.info(f"Created thing for extracted file: {filename}")
            return json.dumps(thing)

        except Exception as e:
            logger.error(f"Error creating thing from metadata: {e}")
            return None

    def _detect_artifact_type_from_ids(self, resource: dict, description: str):
        """
        Detect artifact type from IDS resource

        Returns:
            str: 'cyclonedx', 'oscal', 'arm', or None
        """
        # Try to parse description as JSON to detect type
        try:
            desc_json = json.loads(description)

            # Check for CycloneDX identifiers
            if "bomFormat" in desc_json or "specVersion" in desc_json:
                return "cyclonedx"

            # Check for OSCAL identifiers
            if "component-definition" in desc_json or "component" in desc_json:
                return "oscal"

            # Check for ARM template identifiers
            if "$schema" in desc_json and "microsoft.com/schemas" in str(desc_json.get("$schema", "")).lower():
                return "arm"

            # Check for Clouditor evidence (your use case)
            if "cloudServiceId" in desc_json or "toolId" in desc_json:
                return "clouditor"

        except:
            pass

        # Check resource title/keywords
        keywords = resource.get("ids:keyword", [])
        for keyword in keywords:
            keyword_value = keyword.get("@value", "").lower()
            if "bom" in keyword_value or "sbom" in keyword_value:
                return "cyclonedx"
            if "oscal" in keyword_value:
                return "oscal"
            if "arm" in keyword_value or "azure" in keyword_value:
                return "arm"

        return None

    def _process_ids_artifact(self, resource: dict, toe_id: str, artifact_type: str):
        """
        Process IDS artifact based on type

        Returns:
            str: JSON string of Thing
        """
        logger = logging.getLogger(__name__)

        try:
            # Extract description which contains the actual data
            description = resource.get("ids:description", [{}])[0].get("@value", "{}")
            artifact_data = json.loads(description)

            # Route to appropriate processor
            if artifact_type == "cyclonedx":
                return self.from_cyclonedx_ids(artifact_data, resource, toe_id)
            elif artifact_type == "oscal":
                return self.from_oscal_ids(artifact_data, resource, toe_id)
            elif artifact_type == "arm":
                return self.from_arm_ids(artifact_data, resource, toe_id)
            elif artifact_type == "clouditor":
                return self.from_clouditor_ids(artifact_data, resource, toe_id)
            else:
                return None

        except Exception as e:
            logger.error(f"Error processing IDS artifact: {e}")
            return None

    def from_cyclonedx_ids(self, cyclone_data: dict, ids_resource: dict, toe_id: str):
        """
        Transform CycloneDX from IDS connector to Thing format
        """
        logger = logging.getLogger(__name__)

        logger.info("Transforming CycloneDX from IDS connector")

        # Use existing from_cyclone logic but add IDS metadata
        cyclone_json = json.dumps(cyclone_data)

        adapter = DTModelAdapter()
        thing = adapter.from_cyclone(cyclone_json)

        # Add IDS metadata
        thing["attributes"]["source"] = "ids_connector"
        thing["attributes"]["ids_resource_id"] = ids_resource.get("@id")
        thing["attributes"]["ids_title"] = ids_resource.get("ids:title", [{}])[0].get("@value")
        thing["attributes"]["toe_id"] = toe_id
        thing["attributes"]["category"] = "BOMS"

        return json.dumps(thing)

    def from_oscal_ids(self, oscal_data: dict, ids_resource: dict, toe_id: str):
        """
        Transform OSCAL from IDS connector to Thing format
        """
        logger = logging.getLogger(__name__)

        logger.info("Transforming OSCAL from IDS connector")

        # Use existing adapter logic
        adapter = DTModelAdapter()
        oscal_json = json.dumps(oscal_data)
        thing = adapter.from_oscal_component(oscal_json)

        # Add IDS metadata
        thing["attributes"]["source"] = "ids_connector"
        thing["attributes"]["ids_resource_id"] = ids_resource.get("@id")
        thing["attributes"]["ids_title"] = ids_resource.get("ids:title", [{}])[0].get("@value")
        thing["attributes"]["toe_id"] = toe_id
        thing["attributes"]["category"] = "OSCAL"

        return json.dumps(thing)

    def from_arm_ids(self, arm_data: dict, ids_resource: dict, toe_id: str):
        """
        Transform ARM template from IDS connector to Thing format
        """
        logger = logging.getLogger(__name__)

        logger.info("Transforming ARM template from IDS connector")

        # Use existing adapter logic
        adapter = DTModelAdapter()
        arm_json = json.dumps(arm_data)
        thing = adapter.from_arm_template(arm_json)

        # Add IDS metadata
        thing["attributes"]["source"] = "ids_connector"
        thing["attributes"]["ids_resource_id"] = ids_resource.get("@id")
        thing["attributes"]["ids_title"] = ids_resource.get("ids:title", [{}])[0].get("@value")
        thing["attributes"]["toe_id"] = toe_id
        thing["attributes"]["category"] = "ARM"

        return json.dumps(thing)

    def from_clouditor_ids(self, clouditor_data: dict, ids_resource: dict, toe_id: str):
        """
        Transform Clouditor evidence from IDS connector to Thing format
        """
        logger = logging.getLogger(__name__)

        logger.info("Transforming Clouditor evidence from IDS connector")

        # Extract resource information
        resource_info = clouditor_data.get("resource", {})

        thing = {
            "attributes": {
                "toe_id": toe_id,
                "category": "CLOUD",
                "source": "ids_connector",
                "ids_resource_id": ids_resource.get("@id"),
                "ids_title": ids_resource.get("ids:title", [{}])[0].get("@value"),
                "evidence_id": clouditor_data.get("id"),
                "timestamp": clouditor_data.get("timestamp"),
                "cloud_service_id": clouditor_data.get("cloudServiceId"),
                "tool_id": clouditor_data.get("toolId"),
                "sourceType": "clouditor",
                "transformedAt": datetime.utcnow().isoformat() + "Z"
            },
            "features": {
                "resource": {
                    "properties": resource_info
                },
                "raw_data": {
                    "properties": {
                        "raw": clouditor_data.get("raw", "")
                    }
                }
            }
        }

        return json.dumps(thing)

    def _store_ids_evidence_file(self, resource: dict, toe_id: str):
        """
        Store IDS resource as generic evidence file

        Returns:
            str: JSON string of Thing with file metadata
        """
        logger = logging.getLogger(__name__)

        try:
            # Extract metadata
            resource_id = resource.get("@id", "unknown")
            title = resource.get("ids:title", [{}])[0].get("@value", "Unknown")
            description = resource.get("ids:description", [{}])[0].get("@value", "")
            created = resource.get("ids:created", {}).get("@value", datetime.now().isoformat())

            # Create evidence directory
            evidence_dir = "evidence"
            os.makedirs(evidence_dir, exist_ok=True)

            # Generate filename from resource ID

            filename = f"{toe_id}_{hashlib.md5(resource_id.encode()).hexdigest()[:8]}.json"
            file_path = os.path.join(evidence_dir, filename)

            # Save resource to file
            with open(file_path, 'w') as f:
                json.dump(resource, f, indent=2)

            logger.info(f"Stored IDS evidence file: {file_path}")

            # Create Thing for file metadata
            thing = {
                "attributes": {
                    "toe_id": toe_id,
                    "category": "IDS_EVIDENCE",
                    "source": "ids_connector",
                    "ids_resource_id": resource_id,
                    "title": title,
                    "file_path": file_path,
                    "filename": filename,
                    "created": created,
                    "sourceType": "ids_evidence",
                    "transformedAt": datetime.utcnow().isoformat() + "Z"
                },
                "features": {
                    "metadata": {
                        "properties": {
                            "description": description,
                            "file_size": os.path.getsize(file_path),
                            "keywords": [kw.get("@value") for kw in resource.get("ids:keyword", [])]
                        }
                    },
                    "ids_resource": {
                        "properties": resource
                    }
                }
            }

            return json.dumps(thing)

        except Exception as e:
            logger.error(f"Error storing IDS evidence file: {e}")
            return None
