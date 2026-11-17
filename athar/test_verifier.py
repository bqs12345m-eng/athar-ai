
import unittest

from athar.verifier import verify_task, sha256_text


class VerifierTests(unittest.TestCase):

    def test_all_requirements_pass(self):
        task = {
            "task_id": "T1",
            "requirements": [
                {
                    "requirement_id": "R1",
                    "evidence_id": "E1",
                    "expected_contains": "hello"
                }
            ],
            "evidence": [
                {"evidence_id": "E1", "content": "hello world"}
            ]
        }
        self.assertEqual(verify_task(task)["status"], "VERIFIED")

    def test_missing_evidence(self):
        task = {
            "task_id": "T2",
            "requirements": [
                {
                    "requirement_id": "R1",
                    "evidence_id": "E1",
                    "expected_contains": "hello"
                }
            ],
            "evidence": []
        }
        self.assertEqual(
            verify_task(task)["status"],
            "INSUFFICIENT_EVIDENCE"
        )

    def test_mismatch_fails(self):
        task = {
            "task_id": "T3",
            "requirements": [
                {
                    "requirement_id": "R1",
                    "evidence_id": "E1",
                    "expected_contains": "hello"
                }
            ],
            "evidence": [
                {"evidence_id": "E1", "content": "goodbye"}
            ]
        }
        self.assertEqual(verify_task(task)["status"], "FAILED")

    def test_partial_result(self):
        task = {
            "task_id": "T4",
            "requirements": [
                {
                    "requirement_id": "R1",
                    "evidence_id": "E1",
                    "expected_contains": "hello"
                },
                {
                    "requirement_id": "R2",
                    "evidence_id": "E2",
                    "expected_contains": "world"
                }
            ],
            "evidence": [
                {"evidence_id": "E1", "content": "hello"}
            ]
        }
        self.assertEqual(verify_task(task)["status"], "PARTIAL")

    def test_sha256_check(self):
        content = "athar"
        task = {
            "requirements": [
                {
                    "requirement_id": "R1",
                    "evidence_id": "E1",
                    "expected_sha256": sha256_text(content)
                }
            ],
            "evidence": [
                {"evidence_id": "E1", "content": content}
            ]
        }
        self.assertEqual(verify_task(task)["status"], "VERIFIED")


if __name__ == "__main__":
    unittest.main()
