
"""ATHAR AI evidence verifier."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_task(task: dict[str, Any]) -> dict[str, Any]:
    """Check supplied evidence against declared requirements."""
    task_id = str(task.get("task_id", "UNSPECIFIED"))
    requirements = task.get("requirements", [])
    evidence_items = task.get("evidence", [])

    if not isinstance(requirements, list) or not isinstance(evidence_items, list):
        raise ValueError("'requirements' and 'evidence' must be lists")

    evidence_by_id = {
        str(item["evidence_id"]): item
        for item in evidence_items
        if isinstance(item, dict) and item.get("evidence_id") is not None
    }

    checks = []
    passed = 0
    missing = 0
    failed = 0

    for index, requirement in enumerate(requirements, start=1):
        if not isinstance(requirement, dict):
            raise ValueError(f"Requirement #{index} must be an object")

        req_id = str(requirement.get("requirement_id", f"REQ-{index}"))
        evidence_id = str(requirement.get("evidence_id", ""))
        evidence = evidence_by_id.get(evidence_id)

        result = {
            "requirement_id": req_id,
            "evidence_id": evidence_id,
            "checks": [],
        }

        if not evidence or not isinstance(evidence.get("content"), str):
            result["status"] = "MISSING"
            result["reason"] = "Required evidence is missing."
            missing += 1
            checks.append(result)
            continue

        content = evidence["content"]
        content_hash = sha256_text(content)
        criteria = 0
        mismatch = False

        expected = requirement.get("expected_contains")
        if expected is not None:
            criteria += 1
            ok = str(expected) in content
            result["checks"].append({
                "type": "expected_contains",
                "expected": str(expected),
                "passed": ok,
            })
            mismatch = mismatch or not ok

        expected_hash = requirement.get("expected_sha256")
        if expected_hash is not None:
            criteria += 1
            ok = str(expected_hash).lower() == content_hash
            result["checks"].append({
                "type": "expected_sha256",
                "expected": str(expected_hash).lower(),
                "actual": content_hash,
                "passed": ok,
            })
            mismatch = mismatch or not ok

        if criteria == 0:
            result["status"] = "UNVERIFIABLE"
            missing += 1
        elif mismatch:
            result["status"] = "FAILED"
            result["actual_sha256"] = content_hash
            failed += 1
        else:
            result["status"] = "PASSED"
            result["actual_sha256"] = content_hash
            passed += 1

        checks.append(result)

    total = len(requirements)

    if total == 0 or (passed == 0 and failed == 0):
        status = "INSUFFICIENT_EVIDENCE"
    elif failed:
        status = "FAILED"
    elif passed == total:
        status = "VERIFIED"
    else:
        status = "PARTIAL"

    return {
        "schema_version": "1.0",
        "product": "ATHAR AI",
        "task_id": task_id,
        "claim": task.get("claim", ""),
        "status": status,
        "summary": {
            "total_requirements": total,
            "passed": passed,
            "missing_or_unverifiable": missing,
            "failed": failed,
        },
        "checks": checks,
        "limitations": [
            "Only supplied evidence was checked.",
            "Evidence origin and authenticity are not independently proven.",
            "No external agent execution was observed.",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
