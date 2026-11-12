"""Agent 3: Remediation Agent.

Takes findings from Code Analysis and Security Vulnerability agents and generates
actionable, prioritized remediation plans with side-by-side corrected code examples.
Leverages secure coding guidelines from the RAG knowledge base to explain
why the original code is problematic and why the proposed fix is safer.
Never modifies original files directly.
"""
from typing import List, Dict, Any, Optional
from rag.rag_pipeline import RAGPipeline


class RemediationAgent:
    """Agent 3: Generates targeted remediation strategies and corrected code."""

    def __init__(self, rag_pipeline: Optional[RAGPipeline] = None):
        self.agent_name = "Remediation Agent"
        self.rag_pipeline = rag_pipeline or RAGPipeline()

    def generate_remediation_plan(
        self,
        findings: List[Dict[str, Any]],
        detected_language: str = "python"
    ) -> Dict[str, Any]:
        """Produce prioritized remediation roadmap and code corrections.

        Args:
            findings: Consolidated findings from Code Analysis and Security agents.
            detected_language: 'python' or 'java'.

        Returns:
            Dictionary containing:
            - prioritized_roadmap: List of remediations sorted by severity
            - critical_actions: Immediate steps for critical issues
            - total_remediations: int
            - summary: Overview text
        """
        if not findings:
            return {
                "total_remediations": 0,
                "summary": "No security vulnerabilities or code smells detected. No remediation required.",
                "critical_actions": [],
                "prioritized_roadmap": [],
            }

        # Severity ranking for sorting
        severity_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_findings = sorted(
            findings,
            key=lambda x: (severity_rank.get(str(x.get("severity", "LOW")).upper(), 4), -x.get("heuristic_score", 0))
        )

        roadmap = []
        critical_actions = []

        for idx, finding in enumerate(sorted_findings, start=1):
            title = finding.get("title", "Unknown Finding")
            severity = str(finding.get("severity", "LOW")).upper()
            line_no = finding.get("line_number", 1)
            evidence = finding.get("evidence_snippet", "")
            corrected = finding.get("corrected_code", "")
            rec = finding.get("remediation_recommendation", "")
            desc = finding.get("description", "")
            risk = finding.get("risk_explanation", "")

            # Query knowledge base for additional grounded context
            kb_chunks = self.rag_pipeline.retrieve_context(f"{title} secure remediation {detected_language}", top_k=1)
            kb_citation = ""
            if kb_chunks:
                first_chunk = kb_chunks[0]
                kb_citation = f"{first_chunk.get('title')} § {first_chunk.get('section')}"

            # Elaborate problem explanation and safety rationale
            problem_explanation = (
                f"{desc} At line {line_no}, the construct '{evidence}' exhibits an unmitigated vulnerability pattern. {risk}"
            )

            safety_rationale = (
                f"The corrected implementation resolves the issue by enforcing defensive coding practices: {rec}. "
                "By decoupling user input from direct execution or state mutation, exploit vectors are eliminated."
            )

            item = {
                "step_number": idx,
                "title": title,
                "severity": severity,
                "line_number": line_no,
                "category": finding.get("category", "General"),
                "problem_explanation": problem_explanation,
                "original_code_snippet": evidence,
                "remediation_code": corrected or "# Review logic and follow secure coding standard.",
                "safety_rationale": safety_rationale,
                "knowledge_base_reference": kb_citation or "OWASP Secure Coding Practice",
            }
            roadmap.append(item)

            if severity in ("CRITICAL", "HIGH"):
                critical_actions.append(f"Line {line_no}: Fix {title} - {rec}")

        summary = (
            f"Generated {len(roadmap)} remediation steps. "
            f"{len(critical_actions)} require immediate prioritization before merge."
        )

        return {
            "total_remediations": len(roadmap),
            "summary": summary,
            "critical_actions": critical_actions,
            "prioritized_roadmap": roadmap,
        }
