import logging
import subprocess
from sdt_pod_deploy import SDTDeployer
from delete_sdt_deployment import SdtDeploymentCleaner

class SDTManager:
    def __init__(self):
        """Initialize SDTManager with an instance of SDTDeployer."""
        self.deployer = SDTDeployer()
    
    def deploy(self):
        """Deploys the SDT pod and service."""
        self.deployer.deploy_pod()
        if self.deployer.check_pod_running():
            self.deployer.deploy_service()
        else:
            print("Service deployment skipped because the pod is not running.")

    #def delete_sdt_deployment(self):
        #get the deployment name from the identifier's key-value pair (key is pod name, value is identifier)

if __name__ == "__main__":
    manager = SDTManager()
    manager.deploy()
    #the code block to delete the sdt deployment
