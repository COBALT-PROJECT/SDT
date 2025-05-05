import json
import requests
import os
import git
import hashlib
import shutil

from core.util import FileUtils

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
                import shutil
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
            #         "component_type": "Repository",
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
                "component_type": "Repository",
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
                from datetime import datetime
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
        from datetime import datetime


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
                    "component_type": component
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
 