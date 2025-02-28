import logging
import subprocess

class SdtDeploymentCleaner:
    """
    A simple class to delete an SDT (Smart Digital Transport) deployment by name.
    """

    def __init__(self, kubectl_path="/usr/local/bin/kubectl"):
        """
        :param kubectl_path: The path to the kubectl binary on your system.
        """
        self.kubectl_path = kubectl_path
        # Configure logging once in the constructor (optional)
        logging.basicConfig(level=logging.INFO, 
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def run_command(self, command: str) -> str:
        """
        Runs a shell command using subprocess and logs the results.
        :param command: The command to be executed.
        :return: The standard output of the command or an empty string if failed.
        """
        self.logger.info(f"Executing command: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            self.logger.info(result.stdout)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed with error: {e.stderr}")
            return ""

    def delete_deployment(self, deployment_name: str) -> None:
        """
        Deletes the specified SDT deployment in the default namespace.
        :param deployment_name: The exact name of the Kubernetes deployment.
        """
        self.logger.info(f"Attempting to delete deployment: {deployment_name}")
        command = f"{self.kubectl_path} delete deployment {deployment_name} --ignore-not-found"
        output = self.run_command(command)
        if "deleted" in output:
            self.logger.info(f"Deployment '{deployment_name}' was successfully deleted.")
        else:
            self.logger.info(f"Deployment '{deployment_name}' not found or already deleted.")

def main():
    # Example usage:
    # You could get the deployment name from command-line args or hardcode it.
    sdt_deployment_name = "sdt-deployment-example"

    cleaner = SdtDeploymentCleaner()
    cleaner.delete_deployment(sdt_deployment_name)

if __name__ == "__main__":
    main()
