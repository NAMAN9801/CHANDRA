from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class UploadResponse:
    request_id: str
    original_path: str
    display_url: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "original_path": self.original_path,
            "display_url": self.display_url,
        }


@dataclass
class AnalysisRequest:
    display_url: str

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "AnalysisRequest":
        display_url = payload.get("display_url")
        if not display_url or not isinstance(display_url, str):
            raise ValueError("Display URL is required")
        return cls(display_url=display_url)


@dataclass
class AnalysisResponse:
    success: bool
    request_id: str
    analysis_result: str
    artifact_path: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "request_id": self.request_id,
            "analysis_result": self.analysis_result,
            "artifact_path": self.artifact_path,
        }
