"""delivery_check.py — Phase 5 Buzz Check service.

Runs deterministic delivery checks against brief requirements and returns
a structured result.  All scoring is computed server-side; creators cannot
influence the result.

Rules:
- If the brief does NOT specify a requirement, that check is skipped entirely
  (does not penalise the score).
- If file metadata is unavailable (extraction failed), the check is marked
  "not_verified" — never auto-passed.
- Score is 0–100 based only on applicable checks.
- overall_status:  ready (>=90) | needs_attention (60-89) | blocked (<60)
"""

import re
import logging
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)

# ── Weight table (percentage points) ─────────────────────────────────────────
WEIGHTS = {
    "format": 20,
    "aspect_ratio": 25,
    "dimensions": 20,
    "duration": 20,
    "deliverable_type": 15,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_aspect_ratio(raw: Optional[str]) -> Optional[tuple[int, int]]:
    """Convert '9:16' -> (9, 16). Returns None if unparseable."""
    if not raw:
        return None
    m = re.match(r"^\s*(\d+)\s*[:/]\s*(\d+)\s*$", raw.strip())
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def _parse_duration_seconds(raw: Optional[str]) -> Optional[float]:
    """Convert '30 seconds', '15s', '2 min', '1:30' -> float seconds."""
    if not raw:
        return None
    s = raw.strip().lower()
    # mm:ss
    m = re.match(r"^(\d+):(\d{2})$", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    # Xm Ys  or  X min Y sec
    m = re.match(r"(\d+)\s*m(?:in(?:utes?)?)?\s*(?:(\d+)\s*s(?:ec(?:onds?)?)?)?", s)
    if m:
        return int(m.group(1)) * 60 + (int(m.group(2)) if m.group(2) else 0)
    # plain seconds
    m = re.match(r"(\d+(?:\.\d+)?)\s*s(?:ec(?:onds?)?)?", s)
    if m:
        return float(m.group(1))
    # bare number
    m = re.match(r"^(\d+(?:\.\d+)?)$", s)
    if m:
        return float(m.group(1))
    return None


def _ratio_from_dimensions(width: Optional[int], height: Optional[int]) -> Optional[tuple[int, int]]:
    """Reduce pixel dimensions to a simplified aspect ratio."""
    if not width or not height:
        return None
    from math import gcd
    g = gcd(width, height)
    return width // g, height // g


def _ratio_matches(expected: tuple[int, int], actual: tuple[int, int], tolerance: float = 0.03) -> bool:
    """Compare two aspect ratios with a small float tolerance."""
    e_val = expected[0] / expected[1]
    a_val = actual[0] / actual[1]
    return abs(e_val - a_val) / e_val <= tolerance


# ── Metadata extraction ───────────────────────────────────────────────────────

def extract_file_metadata(stored_path: str, file_type: Optional[str]) -> dict:
    """
    Attempt to read width, height, duration_seconds from file on disk.
    Returns a dict with only the keys that were successfully extracted.
    Never raises — failures are silently skipped.
    """
    result: dict = {}
    if not stored_path:
        return result

    try:
        from pathlib import Path as _Path
        path = _Path(stored_path)
        if not path.exists():
            return result

        ftype = (file_type or "").lower()

        # ── Images ────────────────────────────────────────────────────────────
        if ftype == "image" or path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            try:
                from PIL import Image
                with Image.open(path) as img:
                    result["width"], result["height"] = img.size
            except Exception as exc:
                log.debug("PIL extraction failed for %s: %s", stored_path, exc)

        # ── Video / Audio via mutagen ─────────────────────────────────────────
        # mutagen reads container headers for duration; works for mp4/mov/mp3/m4a
        if ftype in {"video", "audio"} or path.suffix.lower() in {".mp4", ".mov", ".mp3", ".m4a", ".ogg"}:
            try:
                from mutagen import File as MutagenFile
                mf = MutagenFile(str(path))
                if mf and mf.info and hasattr(mf.info, "length"):
                    result["duration_seconds"] = float(mf.info.length)
            except Exception as exc:
                log.debug("mutagen extraction failed for %s: %s", stored_path, exc)

    except Exception as exc:
        log.debug("Metadata extraction outer error for %s: %s", stored_path, exc)

    return result


# ── Main check function ───────────────────────────────────────────────────────

def run_delivery_check(
    *,
    file_id: int,
    workspace_id: int,
    version: int,
    filename: str,
    mime_type: Optional[str],
    file_type: Optional[str],
    width: Optional[int],
    height: Optional[int],
    duration_seconds: Optional[float],
    deliverable_type: Optional[str],
    # Brief requirements (all optional — None means "not specified")
    brief_aspect_ratio: Optional[str] = None,
    brief_duration: Optional[str] = None,
    brief_content_type: Optional[str] = None,
    brief_deliverables: Optional[list] = None,
) -> dict:
    """
    Run all applicable delivery checks and return a structured result dict.
    This is pure business logic — no DB access.
    """
    checks = []
    warnings = []
    suggested_fixes = []
    score_earned = 0
    score_possible = 0

    def _add_check(name: str, label: str, status: str, detail: str, fix: Optional[str] = None):
        """Helper to append a check item and update running score."""
        nonlocal score_earned, score_possible
        weight = WEIGHTS.get(name, 0)
        if status == "passed":
            score_possible += weight
            score_earned += weight
        elif status == "failed":
            score_possible += weight
        elif status == "not_verified":
            # Not counted in score — we don't penalise for unknown metadata
            pass
        checks.append({"name": name, "label": label, "status": status, "detail": detail})
        if fix:
            suggested_fixes.append(fix)

    # ── 1. FORMAT CHECK ───────────────────────────────────────────────────────
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    expected_format: Optional[str] = None
    if brief_content_type:
        ct = brief_content_type.lower()
        if ct == "video":
            expected_format = "video"
        elif ct == "image":
            expected_format = "image"

    if expected_format:
        if expected_format == "video" and ext in {"mp4", "mov"}:
            _add_check("format", "File Format", "passed", f"Format '{ext.upper()}' is accepted for video deliverables.")
        elif expected_format == "image" and ext in {"jpg", "jpeg", "png", "webp"}:
            _add_check("format", "File Format", "passed", f"Format '{ext.upper()}' is accepted for image deliverables.")
        elif expected_format == "video" and ext not in {"mp4", "mov"}:
            _add_check(
                "format", "File Format", "failed",
                f"Uploaded '{ext.upper()}' but brief requires a video deliverable (MP4 or MOV).",
                f"Re-export your deliverable as MP4 or MOV before resubmitting.",
            )
        elif expected_format == "image" and ext not in {"jpg", "jpeg", "png", "webp"}:
            _add_check(
                "format", "File Format", "failed",
                f"Uploaded '{ext.upper()}' but brief requires an image deliverable (JPG, PNG, or WEBP).",
                f"Re-export your deliverable as JPG, PNG, or WEBP before resubmitting.",
            )

    # ── 2. ASPECT RATIO CHECK ────────────────────────────────────────────────
    req_ratio = _parse_aspect_ratio(brief_aspect_ratio)
    if req_ratio:
        if width and height:
            actual_ratio = _ratio_from_dimensions(width, height)
            if actual_ratio and _ratio_matches(req_ratio, actual_ratio):
                _add_check(
                    "aspect_ratio", "Aspect Ratio", "passed",
                    f"Aspect ratio {req_ratio[0]}:{req_ratio[1]} confirmed ({width}×{height}px).",
                )
            else:
                actual_label = f"{actual_ratio[0]}:{actual_ratio[1]}" if actual_ratio else f"{width}×{height}px"
                _add_check(
                    "aspect_ratio", "Aspect Ratio", "failed",
                    f"Brief requires {req_ratio[0]}:{req_ratio[1]} but file appears to be {actual_label}.",
                    f"Resize or re-crop to {req_ratio[0]}:{req_ratio[1]} before resubmitting.",
                )
        else:
            _add_check(
                "aspect_ratio", "Aspect Ratio", "not_verified",
                f"Brief requires {req_ratio[0]}:{req_ratio[1]}. Dimensions could not be read from this file — verify manually.",
            )
            warnings.append(
                f"Aspect ratio could not be verified automatically. Please confirm the file is {req_ratio[0]}:{req_ratio[1]}."
            )

    # ── 3. DIMENSIONS CHECK ───────────────────────────────────────────────────
    # Only check if we have pixel info AND the ratio requirement is already flagged
    # Here we surface raw dimensions as info — not a scored gate unless explicitly set in brief
    if width and height and req_ratio:
        # Brief-level dimension enforcement is not currently a separate field;
        # we treat this as an informational supplementary detail, not a scored gate.
        pass

    # ── 4. DURATION CHECK ────────────────────────────────────────────────────
    req_dur = _parse_duration_seconds(brief_duration)
    if req_dur is not None:
        if duration_seconds is not None:
            # Allow up to 3-second over-run before flagging
            TOLERANCE_SEC = 3.0
            if duration_seconds <= req_dur + TOLERANCE_SEC:
                _add_check(
                    "duration", "Duration", "passed",
                    f"Duration {duration_seconds:.1f}s is within the required {req_dur:.0f}s limit.",
                )
            else:
                over = duration_seconds - req_dur
                _add_check(
                    "duration", "Duration", "failed",
                    f"Duration is {duration_seconds:.1f}s — {over:.1f}s over the required maximum of {req_dur:.0f}s.",
                    f"Trim approximately {over:.1f} seconds before resubmitting for final review.",
                )
        else:
            _add_check(
                "duration", "Duration", "not_verified",
                f"Brief requires a maximum of {req_dur:.0f}s. Duration could not be read automatically — verify manually.",
            )
            warnings.append(
                f"Duration could not be verified automatically. Please confirm the file is within {req_dur:.0f}s."
            )

    # ── 5. DELIVERABLE TYPE CHECK ────────────────────────────────────────────
    if brief_deliverables and isinstance(brief_deliverables, list) and len(brief_deliverables) > 0:
        # We only verify presence of expected deliverable count, not semantic labelling
        # (deliverable_type is a free-form creator label, not a brief requirement field)
        # This check is informational — brief_deliverables is a list of expected output descriptions.
        # We confirm the upload is a recognisable media type consistent with the brief.
        if file_type in {"video", "image", "document"}:
            _add_check(
                "deliverable_type", "Deliverable Type", "passed",
                f"File type '{file_type}' aligns with project deliverable expectations.",
            )
        elif file_type == "zip":
            _add_check(
                "deliverable_type", "Deliverable Type", "passed",
                "Archive package (ZIP) received — ensure all brief deliverables are included inside.",
            )
            warnings.append("ZIP package detected. Please verify all required deliverables are included before the recruiter reviews.")
        else:
            _add_check(
                "deliverable_type", "Deliverable Type", "not_verified",
                "File type could not be confirmed against brief deliverable requirements.",
            )

    # ── COMPUTE FINAL SCORE ───────────────────────────────────────────────────
    if score_possible > 0:
        readiness_score = round(score_earned / score_possible * 100)
    else:
        # No scoreable checks ran → treat as fully compliant (nothing to check)
        readiness_score = 100

    if readiness_score >= 90:
        overall_status = "ready"
    elif readiness_score >= 60:
        overall_status = "needs_attention"
    else:
        overall_status = "blocked"

    return {
        "file_id": file_id,
        "workspace_id": workspace_id,
        "version": version,
        "overall_status": overall_status,
        "readiness_score": readiness_score,
        "check_details": checks,
        "warnings": warnings,
        "suggested_fixes": suggested_fixes,
        "generated_at": datetime.utcnow().isoformat(),
    }
