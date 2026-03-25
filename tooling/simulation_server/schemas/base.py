from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime

class SyntheticDependency(BaseModel):
    purl: str
    requirement: str
    is_direct: bool = True
    ecosystem: str

    @field_validator('purl')
    @classmethod
    def validate_purl_format(cls, v: str) -> str:
        if not v.startswith("pkg:"):
            raise ValueError("Synthetic PURL must strictly adhere to the pkg-scheme format (e.g., pkg:npm/lodash@4.17.21).")
        return v

class SyntheticPackageVersion(BaseModel):
    version: str
    published_at: datetime
    dependencies: List[SyntheticDependency] = []
    metadata: Dict[str, str] = {
        "license": "Apache-2.0",
        "size_bytes": "1048576",
        "hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }

class SyntheticPackage(BaseModel):
    name: str
    ecosystem: str
    versions: List[SyntheticPackageVersion]
