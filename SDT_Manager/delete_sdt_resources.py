import os
import subprocess
import logging
import time
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

# Constants
WORK_DIR = "/home/allen/ditto"  # Ensure this is the correct working directory
KUBECTL_PATH = "/usr/local/bin/kubectl"  # Ensure this matches your system
KUBECONFIG_PATH = "/etc/rancher/k3s/k3s.yaml"  # K3s kubeconfig path

# Set Kubernetes config explicitly for K3s
os.environ["KUBECONFIG"] = KUBECONFIG_PATH

# Configure Logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def run_shell_command(command: str):
    """Executes a shell command and logs output."""
    try:
        if command.startswith("kubectl "):
            command = command.replace("kubectl ", f"{KUBECTL_PATH} ", 1)
        
        logger.info(f"Executing: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(result.stdout)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(e.stderr)
        return None

def delete_configmaps():
    """Deletes all Ditto-related ConfigMaps."""
    logger.info("Deleting ConfigMaps...")
    configmaps = ["nginx-conf", "nginx-cors", "nginx-htpasswd", "nginx-index", "swagger-ui-api"]
    run_shell_command(f"kubectl delete configmap {' '.join(configmaps)} --ignore-not-found")

def delete_ditto_resources():
    """Deletes all Ditto-related resources."""
    logger.info("Deleting MongoDB resources...")
    run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/mongodb/mongodb.yaml --ignore-not-found")
    
    logger.info("Deleting Ditto log files pod...")
    run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/ditto/ditto-log-files.yaml --ignore-not-found")
    
    logger.info("Deleting Ditto core services...")
    run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/ditto/ --ignore-not-found")
    
    logger.info("Deleting Swagger UI resources...")
    run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/swagger/swagger.yaml --ignore-not-found")
    
    logger.info("Deleting Nginx resources...")
    run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/nginx/nginx.yaml --ignore-not-found")

def wait_for_pods_termination(label="app=sdt", timeout=60):
    """Waits until all pods matching a label are terminated."""
    logger.info(f"Waiting for pods with label {label} to be deleted...")
    for _ in range(timeout // 5):
        pods = run_shell_command(f"kubectl get pods -l {label} -n default --no-headers")
        if not pods:
            logger.info(f"All pods with label {label} are deleted.")
            return
        time.sleep(5)
    logger.warning(f"Pods with label {label} were not deleted within {timeout} seconds.")

def delete_all_remaining_resources():
    """Deletes only SDT-related resources in the 'default' namespace instead of everything."""
    logger.info("Deleting SDT-specific resources in the default namespace...")
    run_shell_command("kubectl delete all -l app=sdt -n default --ignore-not-found")
    wait_for_pods_termination("app=sdt")

def confirm_deletion():
    """Lists remaining resources in the 'default' namespace."""
    logger.info("Checking for remaining resources in the default namespace...")
    run_shell_command("kubectl get all -n default")

def main():
    """Main function to delete all Ditto resources in the default namespace."""
    logger.info("Starting Ditto Cluster Deletion Process...")
    delete_configmaps()
    delete_ditto_resources()
    delete_all_remaining_resources()
    confirm_deletion()
    logger.info("Ditto Cluster Cleanup Completed.")

if __name__ == "__main__":
    main()


import os
import subprocess
import logging
import time

class DittoResourceCleaner:
    WORK_DIR = "/home/allen/ditto"  # Ensure this is the correct working directory
    KUBECTL_PATH = "/usr/local/bin/kubectl"  # Ensure this matches your system
    KUBECONFIG_PATH = "/etc/rancher/k3s/k3s.yaml"  # K3s kubeconfig path

    def __init__(self):
        os.environ["KUBECONFIG"] = self.KUBECONFIG_PATH
        logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run_shell_command(self, command: str):
        """Executes a shell command and logs output."""
        try:
            if command.startswith("kubectl "):
                command = command.replace("kubectl ", f"{self.KUBECTL_PATH} ", 1)
            
            self.logger.info(f"Executing: {command}")
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            self.logger.info(result.stdout)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {command}")
            self.logger.error(e.stderr)
            return None

    def delete_configmaps(self):
        """Deletes all Ditto-related ConfigMaps."""
        self.logger.info("Deleting ConfigMaps...")
        configmaps = ["nginx-conf", "nginx-cors", "nginx-htpasswd", "nginx-index", "swagger-ui-api"]
        self.run_shell_command(f"kubectl delete configmap {' '.join(configmaps)} --ignore-not-found")

    def delete_ditto_resources(self):
        """Deletes all Ditto-related resources."""
        self.logger.info("Deleting MongoDB resources...")
        self.run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/mongodb/mongodb.yaml --ignore-not-found")
        
        self.logger.info("Deleting Ditto log files pod...")
        self.run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/ditto/ditto-log-files.yaml --ignore-not-found")
        
        self.logger.info("Deleting Ditto core services...")
        self.run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/ditto/ --ignore-not-found")
        
        self.logger.info("Deleting Swagger UI resources...")
        self.run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/swagger/swagger.yaml --ignore-not-found")
        
        self.logger.info("Deleting Nginx resources...")
        self.run_shell_command("kubectl delete -f deployment/kubernetes/deploymentFiles/nginx/nginx.yaml --ignore-not-found")

    def wait_for_pods_termination(self, label="app=sdt", timeout=60):
        """Waits until all pods matching a label are terminated."""
        self.logger.info(f"Waiting for pods with label {label} to be deleted...")
        for _ in range(timeout // 5):
            pods = self.run_shell_command(f"kubectl get pods -l {label} -n default --no-headers")
            if not pods:
                self.logger.info(f"All pods with label {label} are deleted.")
                return
            time.sleep(5)
        self.logger.warning(f"Pods with label {label} were not deleted within {timeout} seconds.")

    def delete_all_remaining_resources(self):
        """Deletes only SDT-related resources in the 'default' namespace instead of everything."""
        self.logger.info("Deleting SDT-specific resources in the default namespace...")
        self.run_shell_command("kubectl delete all -l app=sdt -n default --ignore-not-found")
        self.wait_for_pods_termination("app=sdt")

    def confirm_deletion(self):
        """Lists remaining resources in the 'default' namespace."""
        self.logger.info("Checking for remaining resources in the default namespace...")
        self.run_shell_command("kubectl get all -n default")

    def cleanup(self):
        """Main function to delete all Ditto resources in the default namespace."""
        self.logger.info("Starting Ditto Cluster Deletion Process...")
        self.delete_configmaps()
        self.delete_ditto_resources()
        self.delete_all_remaining_resources()
        self.confirm_deletion()
        self.logger.info("Ditto Cluster Cleanup Completed.")

if __name__ == "__main__":
    cleaner = DittoResourceCleaner()
    cleaner.cleanup()
