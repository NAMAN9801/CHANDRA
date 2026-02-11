from pathlib import Path
from urllib.parse import urlparse
import uuid

from OptimizedPSRAnalyzer import OptimizedPSRAnalyzer
from services.models import AnalysisRequest, AnalysisResponse, UploadResponse
from services.storage import ImageNotFoundError, StorageRepository


class AnalysisServiceError(Exception):
    """Base service exception."""


class RequestValidationError(AnalysisServiceError):
    """Raised on bad request payloads."""


class AnalysisExecutionError(AnalysisServiceError):
    """Raised when analysis execution fails."""


class AnalysisService:
    def __init__(self, storage: StorageRepository) -> None:
        self.storage = storage

    def handle_upload(self, file_obj, host_url: str) -> UploadResponse:
        request_id = str(uuid.uuid4())
        self.storage.validate_image(file_obj)
        image_path = self.storage.save_upload(file_obj=file_obj, request_id=request_id)
        display_url = f"{host_url}/display/{request_id}"
        return UploadResponse(
            request_id=request_id,
            original_path=str(image_path),
            display_url=display_url,
        )

    def _request_id_from_display_url(self, display_url: str) -> str:
        parsed = urlparse(display_url)
        request_id = Path(parsed.path).name.strip()
        if not request_id:
            raise RequestValidationError("Display URL is required")
        return request_id

    def analyze(self, payload: dict) -> AnalysisResponse:
        try:
            analysis_request = AnalysisRequest.from_dict(payload)
        except ValueError as exc:
            raise RequestValidationError(str(exc)) from exc

        request_id = self._request_id_from_display_url(analysis_request.display_url)

        try:
            image_path = self.storage.get_uploaded_image(request_id)
        except ImageNotFoundError:
            raise

        analysis_dir = self.storage.create_analysis_dir(request_id)

        analyzer = OptimizedPSRAnalyzer(output_dir=str(analysis_dir))
        output_path = analyzer.analyze_and_visualize(str(image_path))

        if not output_path:
            raise AnalysisExecutionError("Analysis failed")

        return AnalysisResponse(
            success=True,
            request_id=request_id,
            analysis_result="Analysis complete",
            artifact_path=str(output_path),
        )
