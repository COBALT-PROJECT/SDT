# File: sdt_manager.py
import logging
import subprocess
from sdt_pod_deploy import SDTDeployer
from delete_sdt_deployment import SDTDeploymentCleaner

class SDTManager:
    def __init__(self):
        """Initialize SDTManager with instances of SDTDeployer and SDTDeploymentCleaner."""
        self.deployer = SDTDeployer()
        self.cleaner = SDTDeploymentCleaner()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def deploy(self):
        """Deploys the SDT pod and service."""
        self.deployer.deploy_pod()
        if self.deployer.check_pod_running():
            self.deployer.deploy_service()
        else:
            self.logger.error("Service deployment skipped because the pod is not running.")

    def delete_sdt_deployment(self):
        """
        Shows available deployments and lets user choose which to delete based on identifiers.
        
        Returns:
            Dict[str, bool]: Dictionary mapping identifier to deletion success status
        """
        pod_map = self.deployer.pod_map #import the variable from deployer which has the identifier and corresponding pod name
        
        if not pod_map:
            self.logger.warning("No deployments found in pod map to delete.")
            return {}
        
        deletion_results = self.cleaner.cleanup_deployment_by_identifier(pod_map)
        
        # Remove deleted deployments from pod_map
        for identifier, success in deletion_results.items():
            if success:
                pods_to_remove = [pod_name for pod_name, pod_id in self.deployer.pod_map.items() 
                                if pod_id == identifier]
                for pod_name in pods_to_remove:
                    del self.deployer.pod_map[pod_name]
                    self.logger.info(f"Removed {pod_name} from pod map.")
        
        return deletion_results

if __name__ == "__main__":
    manager = SDTManager()
    
    # Deploy
    manager.deploy()
    
    # Delete deployments
    deletion_results = manager.delete_sdt_deployment()
    for identifier, success in deletion_results.items():
        print(f"Deployment deletion for identifier {identifier}: {'Successful' if success else 'Failed'}")
