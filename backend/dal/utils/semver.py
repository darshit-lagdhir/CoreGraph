import re
from typing import Tuple, Optional, List
from sqlalchemy import select, and_, text
from dal.models.graph import PackageVersion

# Regex: Semantic Versioning 2.0.0 compliance with 'v' prefix support
SEMVER_REGEX = re.compile(
    r"^v?(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def calculate_semver_components(
    version_str: str,
) -> Tuple[int, int, int, Optional[str], Optional[str], str]:
    """Decomposes a version string into B-Tree indexable sort keys (Task 009 Engine)."""
    match = SEMVER_REGEX.match(version_str)
    if not match:
        # Fallback to lexical sorting for non-compliant strings (CoreGraph Protocol)
        parts = version_str.split(".")
        ma = int(parts[0]) if parts and parts[0].isdigit() else 0
        mi = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        pa = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        sort_key = f"{ma:05d}.{mi:05d}.{pa:05d}"
        return (ma, mi, pa, None, None, sort_key)

    ma = int(match.group("major"))
    mi = int(match.group("minor"))
    pa = int(match.group("patch"))
    pre = match.group("prerelease")
    build = match.group("buildmetadata")
    sort_key = f"{ma:05d}.{mi:05d}.{pa:05d}"
    return (ma, mi, pa, pre, build, sort_key)


async def resolve_best_candidate(
    session, package_id: str, range_specifier: str
) -> Optional[PackageVersion]:
    """
    The High-Velocity Resolution Kernel (Task 009).
    Translates ranges (^1.2.0, ~0.5.1) into the highest compliant B-Tree candidate.
    """
    # Simple Caret/Tilde logic for competition MVP:
    # ^1.2.0 -> [1.2.0, 2.0.0)
    # ~1.2.0 -> [1.2.0, 1.3.0)

    clean_range = range_specifier.lstrip("^~")
    ma, mi, pa, _, _, _ = calculate_semver_components(clean_range)

    query = select(PackageVersion).where(
        and_(PackageVersion.package_id == package_id, PackageVersion.is_stable == True)
    )

    if range_specifier.startswith("^"):
        # Major must match if > 0, otherwise major match 0 and minor match
        if ma > 0:
            query = query.where(PackageVersion.version_major == ma)
        else:
            query = query.where(
                and_(PackageVersion.version_major == 0, PackageVersion.version_minor == mi)
            )
    elif range_specifier.startswith("~"):
        query = query.where(
            and_(PackageVersion.version_major == ma, PackageVersion.version_minor == mi)
        )

    # Sort by sort_key DESC to find the HIGHEST resolution (Task 009 Protocol)
    query = query.order_by(PackageVersion.sort_key.desc()).limit(1)

    result = await session.execute(query)
    return result.scalars().first()
