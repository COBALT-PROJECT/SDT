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
    def fetch_push_save_repo(self,toeid: str, category:str,  repo_url, local_dir='evidence'):
        """
        Clones a GitHub repository and saves it in the local directory.
        Generates a file tree with hashes for each file.
        Overwrites repository if it already exists.
        Includes Git modification times for each file.

        Args:
            repo_url (str): The URL of the GitHub repository.
            local_dir (str): The local directory to save the repo. Default is 'evidence'.

        Returns:
            dict: Transformed thing object with repository metadata and file tree
        """
        try:
            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]

            # Use current working directory for local storage
            current_dir = os.getcwd()
            save_dir = os.path.join(current_dir, local_dir)
            repo_path = os.path.join(save_dir, repo_name)

            # Create directory if it doesn't exist
            os.makedirs(save_dir, exist_ok=True)

            # Remove existing repository if it exists
            if os.path.exists(repo_path):
                print(f"Repository already exists at {repo_path}. Removing...")
                shutil.rmtree(repo_path)

            # Clone the repository
            print(f"Cloning repository {repo_url} to {repo_path}...")
            # Check if repo already exists and is a git repository
            if os.path.exists(os.path.join(repo_path, '.git')):
                print(f"Repository already exists at {repo_path}. Syncing...")
                repository = git.Repo(repo_path)
                origin = repository.remotes.origin
                origin.pull()
            else:
                # If path exists but is not a git repo, remove it
                if os.path.exists(repo_path):
                    print(f"Path exists but is not a git repository. Removing...")
                    shutil.rmtree(repo_path)

                # Clone the repository
                print(f"Cloning repository {repo_url} to {repo_path}...")
                repository = git.Repo.clone_from(repo_url, repo_path)

            # Generate file tree with hashes and modification times
            thing =self.generate_things_for_repo(toeid, category, repo_path, repository)

            file_tree = self._generate_file_tree_with_hashes_and_times(repo_path, repository)

            # # Create transformed thing object
            # payload = {
            #     "thingId": "toe.ai.repo:b10359fb-7d9e-4bf2-b83b-8b0244a0dd4e",
            #     "policyId": "cobalt:policy",
            #     "attributes": {
            #         "TOE": "cobalt:TOE",
            #         "repo_name": repo_name,
            #         "github": repo_url,
            #         "source": "Repository",
            #         "clone_timestamp": self._get_current_timestamp()
            #     },
            #     "features": {
            #         "repository": {
            #             "properties": {
            #                 "github": repo_url,
            #                 "local_path": repo_path,
            #                 "last_commit": self._get_last_commit_info(repository)
            #             }
            #         },
            #         "Repository_file_tree": {
            #             "properties": file_tree
            #         }
            #     }
            # }
            # payload = json.dumps(payload)
            # ctrl.create_in_ditto(payload)
            return thing

        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")

    def generate_things_for_repo(self, toeid, category, repo_path, repository):
        """
        Generates a file tree with hashes and modification times for each file in the repository.

        Args:
            repo_path (str): Path to the local repository.
            repository (git.Repo): Git repository object.

        Returns:
            dict: A dictionary representing the file tree with hashes and modification times.
        """
        file_info = []

        # Generate file tree with hashes and modification times
        file_tree = self._generate_file_tree_with_hashes_and_times(repo_path, repository)
        file_tree_object = {}
        for index, file_item in enumerate(file_tree):
            file_tree_object[str(index)] = file_item
        print("**************************************************************")
        # Create transformed thing object
        payload = {
            "attributes": {
                "toe_id": toeid,
                "category": category,
                "repo_name": os.path.basename(repo_path),
                "github": repo_path,
                "sourceType": "Repository",
                "clone_timestamp": self._get_current_timestamp()
            },
            "features": {
                "repository": {
                    "properties": {
                        "github": repo_path,
                        "local_path": repo_path,
                        "last_commit": self._get_last_commit_info(repository)
                    }
                },
                "Repository_file_tree": {
                    "properties": file_tree_object
                }
            }
        }

        return json.dumps(payload)




    def generate_things_for_repo_files(self, repo_path, repository):
        """
        Generates a file tree with hashes and modification times for each file in the repository.

        Args:
            repo_path (str): Path to the local repository.
            repository (git.Repo): Git repository object.

        Returns:
            dict: A dictionary representing the file tree with hashes and modification times.
        """
        file_info = []

        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')

            for file in files:
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1]

                try:
                    # Get file hash
                    file_hash = self.get_file_hash(file_path)

                    # Get last modification time from git
                    mod_time = self._get_git_modification_time(repository, os.path.relpath(file_path, repo_path))

                    # Store file info as dictionary with extension, path, hash, and modification time
                    file_info = {
                        "extension": file_extension,
                        "path": file_path,
                        "hash": file_hash,
                        "last_modified": mod_time
                    }
                except Exception as e:
                    file_info = {
                        "extension": file_extension,
                        "path": file_path,
                        "error": f"Error processing file: {str(e)}"
                    }

                # Create transformed thing object
                payload = {
                    # "thingId": "toe.ai" + file_extension + ":b10359fb-7d9e-4bf2-b83b-8b0244a0dd4e",
                    # "policyId": "cobalt:policy",
                    "attributes": {
                        "repo_name": os.path.basename(repo_path),
                        "repo_path": repo_path
                    },
                    "features": {
                        "file_info": {
                            "properties": file_info
                        }
                    }
                }
                print("3333333333333333333333333")
                print(payload)
                # Send payload to Ditto
                # ctrl.create_in_ditto(json.dumps(payload))
                print("File info sent to Controller.")

        return json.dumps(payload)

    def _generate_file_tree_with_hashes_and_times(self, repo_path, repository):
        """
        Generates a file list with hashes, modification times, and paths for each file in the repository.

        Args:
            repo_path (str): Path to the local repository.
            repository (git.Repo): Git repository object.

        Returns:
            list: A list of dictionaries containing file information (name, path, hash, and modification time).
        """
        file_list = []

        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')

            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, repo_path)

                try:
                    # Get file hash
                    file_hash = self.get_file_hash(file_path)

                    # Get last modification time from git
                    mod_time = self._get_git_modification_time(repository, rel_file_path)

                    # Add file info to the list with the full path
                    file_list.append({
                        "name": file,  # Add the name of the file
                        "path": file_path,  # Use full path instead of relative path
                        "hash": file_hash,
                        "last_modified": mod_time
                    })
                except Exception as e:
                    file_list.append({
                        "name": file,  # Add the name of the file
                        "path": file_path,  # Use full path instead of relative path
                        "error": f"Error processing file: {str(e)}"
                    })

        return file_list

    def _get_git_modification_time(self, repository, file_path):
        """
        Gets the last modification time of a file from git history.

        Args:
            repository (git.Repo): Git repository object.
            file_path (str): Relative path to the file from repository root.

        Returns:
            str: ISO formatted timestamp of last modification.
        """
        try:
            # Get the last commit that modified the file
            logs = repository.git.log('-1', '--format=%aI', '--', file_path)
            if logs:
                return logs.strip()
            else:
                # If no git history for the file, return current time
                return datetime.now().isoformat()
        except Exception as e:
            return f"Error getting modification time: {str(e)}"

    def _get_last_commit_info(self, repository):
        """
        Gets information about the last commit in the repository.

        Args:
            repository (git.Repo): Git repository object.

        Returns:
            dict: Information about the last commit.
        """
        try:
            commit = repository.head.commit
            return {
                "hash": commit.hexsha,
                "author": f"{commit.author.name} <{commit.author.email}>",
                "date": commit.committed_datetime.isoformat(),
                "message": commit.message.strip()
            }
        except Exception as e:
            return {"error": f"Error getting commit info: {str(e)}"}

    def _get_current_timestamp(self):
        """
        Gets the current timestamp in ISO format.

        Returns:
            str: Current timestamp in ISO format.
        """
        return datetime.now().isoformat()

    def fetch_push_save_file(self, github_url, local_dir='evidence'):
        """
        Fetches a file from GitHub and saves it in the local directory.

        Args:
            github_url (str): The URL of the file on GitHub.
            local_dir (str): The local directory to save the file. Default is 'evidence'.

        Returns:
            dict: Transformed thing object with file metadata
        """
        try:
            # Use a directory within the current working directory that you have permissions to
            current_dir = os.getcwd()
            file_name = github_url.split('/')[-1]
            file_extension = os.path.splitext(file_name)[1]

            # Create directory if it doesn't exist
            save_dir = os.path.join(current_dir, local_dir)
            os.makedirs(save_dir, exist_ok=True)

            # Set full file path
            local_path = os.path.join(save_dir, file_name)

            # Convert GitHub blob URL to raw content URL
            if "github.com" in github_url and "/blob/" in github_url:
                raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            else:
                raw_url = github_url

            # Download file
            response = requests.get(raw_url)
            response.raise_for_status()  # Raises error for bad status codes

            # Save file
            with open(local_path, 'wb') as file:
                file.write(response.content)

            # Get file hash
            downloaded_file_hash = self.get_file_hash(local_path)

            # Determine file type and component
            file_types = {
                '.h5': ("toe.ai.h5", "AI Model"),
                '.ipynb': ("toe.ai.ipynb", "AI Notebook"),
                '.json': ("toe.cloud.json", "Cloud")
            }
            ftype, component = file_types.get(file_extension, ("toe.unknown", "Unknown"))

            # Create transformed thing object
            return {
                "thingId": ftype,
                "policyId": "cobalt:policy",
                "attributes": {
                    "TOE": "cobalt:TOE",
                    "file_name": file_name,
                    "github": github_url,
                    "source": component
                },
                "features": {
                    "file": {
                        "properties": {
                            "github": github_url,
                            "hash": downloaded_file_hash,
                            "link": local_path
                        }
                    }
                }
            }

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch file: {str(e)}")
        except IOError as e:
            raise Exception(f"Failed to save file: {str(e)}")

    def get_file_hash(self, file_path, hash_algorithm='sha256'):
        """
        Computes the hash of a file.

        Args:
            file_path (str): The path to the file.
            hash_algorithm (str): The hash algorithm to use. Default is 'sha256'.

        Returns:
            str: The computed hash of the file.
        """
        hash_func = hashlib.new('sha256')
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

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
    
    def process_ids_response(self, ids_response: dict, toe_id: str):
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
