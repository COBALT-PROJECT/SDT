import os
import tempfile
import shutil
import logging
from datetime import datetime
from fastapi.responses import FileResponse

# Setup logging
logger = logging.getLogger(__name__)

class FileUtils:
    """
    Utility class for file operations, particularly creating and handling zip files.
    """

    @staticmethod
    def zip_file(evidence_dir, toe_id):
        """
        Creates a zip file from the evidence directory.

        Args:
            evidence_dir (str): Path to the evidence directory to zip.
            toe_id (str): Target of Evaluation ID.

        Returns:
            tuple: (zip_path, zip_filename) - Path to the created zip file and its filename.
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dir_name = os.path.basename(evidence_dir)  # 'testevidence'
        zip_filename = f'evidence_{dir_name}_{toe_id}_{timestamp}.zip'
        zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
        logger.info(f"Creating zip file: {zip_path}")
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', evidence_dir)
        logger.info(f"Successfully created evidence zip file: {zip_filename}")
        return zip_path, zip_filename

    @staticmethod
    def zip_response(evidence_dir, toe_id):
        """
        Creates a FastAPI FileResponse containing a zip file of the evidence directory.

        Args:
            evidence_dir (str): Path to the evidence directory to zip.
            toe_id (str): Target of Evaluation ID.

        Returns:
            FileResponse: FastAPI response object containing the zip file.
        """
        zip_path, zip_filename = FileUtils.zip_file(evidence_dir, toe_id)
        logger.info(f"Returning zip file: {zip_filename}")
        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type="application/zip"
        )

    @staticmethod
    def file_response(file_path, filename=None, media_type=None):
        """
        Creates a FastAPI FileResponse for a given file.

        Args:
            file_path (str): Path to the file to serve.
            filename (str, optional): Name for the file in the response. Defaults to the basename of file_path.
            media_type (str, optional): Media type (MIME type) for the file. Defaults to None (auto-detection).

        Returns:
            FileResponse: FastAPI response object containing the file.
        """
        if not filename:
            filename = os.path.basename(file_path)

        logger.info(f"Returning file: {filename}")
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type
        )
