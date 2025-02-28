import logging
import subprocess
import time
import uuid
from sdt_pod_deploy import SDTDeployer
from delete_sdt_deployment import SdtDeploymentCleaner

class SDTManager:
    def __init__(self):
        """Initialize SDTManager with instances of SDTDeployer and SdtDeploymentCleaner."""
        self.deployer = SDTDeployer()
        self.cleaner = SdtDeploymentCleaner()

    def deploy(self):
        """Deploys the SDT pod and service."""
        pod_id = uuid.uuid4().hex[:8]
        self.deployer.deploy_pod()
        pod_name = self.deployer.get_pod_name()
        if pod_name:
            self.deployer.pod_map[pod_name] = pod_id  # Store the pod name and ID mapping
            logging.info(f"Mapped Pod Name: {pod_name} to ID: {pod_id}")
            logging.info(f"Current Pod Map: {self.deployer.pod_map}")

        if self.deployer.check_pod_running():
            self.deployer.deploy_service()
        else:
            logging.error("Service deployment skipped because the pod is not running.")

    def delete_sdt_deployment(self, identifier):
        """Deletes the SDT deployment corresponding to the chosen identifier."""
        for pod_name, pod_id in self.deployer.pod_map.items():
            if pod_id == identifier:
                deployment_name = f"sdt-deployment-{pod_id}"
                logging.info(f"Attempting to delete deployment: {deployment_name}")
                self.cleaner.delete_deployment(deployment_name)
                del self.deployer.pod_map[pod_name]
                logging.info(f"Deployment {deployment_name} removed from pod map.")
                return
        logging.info("Identifier not found in the pod map.")

if __name__ == "__main__":
    manager = SDTManager()
    manager.deploy()
    
    if manager.deployer.pod_map:
        print("Available Identifiers:")
        for pod_name, pod_id in manager.deployer.pod_map.items():
            print(f"Pod Name: {pod_name}, Identifier: {pod_id}")
        
        user_input = input("Enter the identifier of the deployment you want to delete (or press Enter to skip): ").strip()
        if user_input:
            manager.delete_sdt_deployment(user_input)
        else:
            logging.info("Exiting without deleting any deployment.")
    else:
        logging.info("No deployments available to delete.")
