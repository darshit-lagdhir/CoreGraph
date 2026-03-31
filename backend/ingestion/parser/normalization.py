import re
from datetime import datetime, timezone
from typing import Dict, Optional, Set, Any, Union, List
import ujson  # type: ignore[import-untyped]


class VersionRecord:
    __slots__ = ("major", "minor", "patch", "pre_release", "v_idx")

    def __init__(self, major: int, minor: int, patch: int, pre_release: str, v_idx: int):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre_release = pre_release
        self.v_idx = v_idx


class PackageMetadata:
    __slots__ = (
        "name",
        "ecosystem",
        "version_string",
        "v_idx",
        "license_spdx",
        "timestamp",
        "is_anomaly",
    )

    def __init__(
        self,
        name: str,
        ecosystem: str,
        version_string: str,
        v_idx: int,
        license_spdx: str,
        timestamp: str,
        is_anomaly: bool,
    ):
        self.name = name
        self.ecosystem = ecosystem
        self.version_string = version_string
        self.v_idx = v_idx
        self.license_spdx = license_spdx
        self.timestamp = timestamp
        self.is_anomaly = is_anomaly


class NormalizationKernel:
    __slots__ = ("seen_versions", "flush_counter", "_license_map", "_prerelease_map", "_semver_rgx")

    def __init__(self):
        self.seen_versions: Set[int] = set()
        self.flush_counter: int = 0

        self._license_map: Dict[str, str] = {
            "apache 2": "Apache-2.0",
            "apache-2.0": "Apache-2.0",
            "asl 2.0": "Apache-2.0",
            "mit/x11": "MIT",
            "mit": "MIT",
            "gplv2+": "GPL-2.0-or-later",
            "gplv3": "GPL-3.0-only",
            "bsd-3-clause": "BSD-3-Clause",
            "bsd-2-clause": "BSD-2-Clause",
            "mpl-2.0": "MPL-2.0",
            "lgpl-3.0": "LGPL-3.0-only",
            "isc": "ISC",
        }

        self._prerelease_map: Dict[str, int] = {
            "alpha": 1,
            "a": 1,
            "beta": 2,
            "b": 2,
            "rc": 3,
            "pre": 4,
            "next": 5,
            "stable": 100,
        }

        self._semver_rgx = re.compile(
            r"^v?(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?(?:[.\-](?P<prerelease>[a-zA-Z0-9]+)\.?\d*)?(?:\+.*)?$"
        )

    def normalize(self, raw_payload: Dict[str, Any], ecosystem: str) -> Optional[PackageMetadata]:
        self._clean_payload(raw_payload)

        if ecosystem == "npm":
            record = self._normalize_npm(raw_payload)
        elif ecosystem == "pypi":
            record = self._normalize_pypi(raw_payload)
        elif ecosystem == "github":
            record = self._normalize_github(raw_payload)
        else:
            return None

        if not record:
            return None

        fp = hash((record.name, record.version_string))
        if fp in self.seen_versions:
            return record

        self.seen_versions.add(fp)
        self.flush_counter += 1

        if self.flush_counter >= 5000:
            self.seen_versions.clear()
            self.flush_counter = 0

        return record

    def _calculate_vidx(self, version_string: str) -> int:
        clean_v = version_string.strip()
        match = self._semver_rgx.match(clean_v)
        if not match:
            return 0

        major = min(int(match.group("major") or 0), 65535)
        minor = min(int(match.group("minor") or 0), 65535)
        patch = min(int(match.group("patch") or 0), 65535)

        pre = match.group("prerelease")
        if pre:
            pre_lower = pre.lower()
            prerelease_quantized = self._prerelease_map.get(pre_lower, 50)
        else:
            prerelease_quantized = 100

        return (major << 48) | (minor << 32) | (patch << 16) | prerelease_quantized

    def _sanitize_license(self, raw_license: str) -> str:
        if not raw_license:
            return "Unrecognized"

        normalized = raw_license.strip().lower()
        if "see " in normalized or "proprietary" in normalized:
            return "Unrecognized"

        for key, spdx in self._license_map.items():
            if key in normalized:
                return spdx

        return "Unrecognized"

    def _normalize_timestamp(self, raw_ts: str) -> str:
        if not raw_ts:
            return datetime.now(timezone.utc).isoformat()

        try:
            if raw_ts.endswith("Z"):
                raw_ts = raw_ts[:-1] + "+00:00"
            dt = datetime.fromisoformat(raw_ts)
            dt = dt.astimezone(timezone.utc)
            return dt.isoformat()
        except (ValueError, TypeError):
            return datetime.now(timezone.utc).isoformat()

    def _normalize_npm(self, payload: Dict[str, Any]) -> Optional[PackageMetadata]:
        name = payload.get("name")
        version = payload.get("version")
        if not name or not version:
            return None

        lic_field = payload.get("license", "")
        raw_lic = lic_field.get("type", "") if isinstance(lic_field, dict) else str(lic_field)
        spdx = self._sanitize_license(raw_lic)

        ts = self._normalize_timestamp(payload.get("time", {}).get(version, ""))
        v_idx = self._calculate_vidx(version)

        return PackageMetadata(
            name=name,
            ecosystem="npm",
            version_string=version,
            v_idx=v_idx,
            license_spdx=spdx,
            timestamp=ts,
            is_anomaly=False,
        )

    def _normalize_pypi(self, payload: Dict[str, Any]) -> Optional[PackageMetadata]:
        info = payload.get("info", {})
        name = info.get("name")
        version = info.get("version")
        if not name or not version:
            return None

        spdx = self._sanitize_license(str(info.get("license", "")))

        urls = payload.get("urls", [])
        raw_ts = urls[0].get("upload_time_iso_8601", "") if urls and isinstance(urls, list) else ""
        ts = self._normalize_timestamp(raw_ts)

        v_idx = self._calculate_vidx(version)

        return PackageMetadata(
            name=name,
            ecosystem="pypi",
            version_string=version,
            v_idx=v_idx,
            license_spdx=spdx,
            timestamp=ts,
            is_anomaly=False,
        )

    def _normalize_github(self, payload: Dict[str, Any]) -> Optional[PackageMetadata]:
        name = payload.get("name") or payload.get("full_name")
        version = payload.get("tag_name")
        if not name or not version:
            return None

        spdx = self._sanitize_license(str(payload.get("license", {}).get("spdx_id", "")))
        ts = self._normalize_timestamp(payload.get("published_at", ""))

        v_idx = self._calculate_vidx(version)

        return PackageMetadata(
            name=name,
            ecosystem="github",
            version_string=version,
            v_idx=v_idx,
            license_spdx=spdx,
            timestamp=ts,
            is_anomaly=False,
        )

    def _clean_payload(self) -> Dict[str, Any]:  # noqa: C901self, data: Dict[str, Any]) -> None:
        stack: List[Union[Dict, List]] = [data]

        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                for k, v in list(current.items()):
                    if isinstance(v, str):
                        current[k] = v.replace("\x00", "")
                    elif isinstance(v, int):
                        if not (-9223372036854775808 <= v <= 9223372036854775807):
                            current[k] = 0
                    elif isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(current, list):
                for i in range(len(current)):
                    if isinstance(current[i], str):
                        current[i] = current[i].replace("\x00", "")
                    elif isinstance(current[i], int):
                        if not (-9223372036854775808 <= current[i] <= 9223372036854775807):
                            current[i] = 0
                    elif isinstance(current[i], (dict, list)):
                        stack.append(current[i])
