"""
SubAgents


"""


def get_subagents(tools):
    def select_tools(*names):
        allowed = set(names)
        return [tool for tool in tools if tool.name in allowed]

    shared_tools = ("retrieve_document",)
    evidence_contract = (
        "Return ONLY a structured report with these sections: domain, risk_rating, "
        "tool_calls, sources_used, verified_findings, inferences, missing_evidence, "
        "contradictions, and remediation_conditions. For every tool call, record "
        "the exact tool name and arguments in tool_calls. For every retrieved result, "
        "record the source filename in sources_used. Never claim a source was used "
        "unless you actually called the tool. Separate verified evidence from inference, "
        "and treat unavailable evidence as UNKNOWN rather than PASS. "
    )


    security_subagent = {
        "name": "security_subagent",
        "description": "A security risk specialist who evaluates vendor security evidence and policy compliance.",
        "system_prompt": 
            """
            You must call retrieve_document before writing any findings.

            Required calls:
            1. document_name="information-security-policy.pdf"
            query="data classification encryption access control SOC2 incident response penetration testing"
            2. document_name="vendor-x-security-questionnaire.pdf"
            query="authentication encryption SOC2 incident response penetration testing"

            Do not use filesystem search tools.
            Do not produce findings until these calls return.
            Record every call in tool_calls and every returned source in sources_used.
            """ + evidence_contract,
        "tools": select_tools(*shared_tools),
    }

    procurement_subagent = {
        "name": "procurement_subagent",
        "description": "A procurement and commercial risk specialist who evaluates pricing, budget, and total cost of ownership.",
        "system_prompt": 
            """
            You must call retrieve_document before writing any findings.

            Required calls:
            1. document_name="procurement-policy.pdf"
            query="pricing tiers volume discounts budget thresholds TCO requirements"
            2. document_name="vendor-x-pricing.pdf"
            query="price per user monthly subscription implementation support discount"

            After the pricing evidence is returned, you MUST call calculate_tco.
            Use only numeric values found in the retrieved evidence and the request.
            Pass employee_count, price_per_user_month, years, implementation_cost,
            annual_support_cost, and annual_discount_percent when available.
            If a required value is missing, report it as UNKNOWN and do not invent it.
            Do not use filesystem search tools as a substitute for these calls.
            Do not produce findings until retrieval and TCO calculation return.
            """ + evidence_contract,
        "tools": select_tools(*shared_tools, "calculate_tco"),
    }

    legal_subagent = {
        "name": "legal_subagent",
        "description": "A legal and compliance risk specialist who evaluates policy evidence and prior vendor assessments.",
        "system_prompt": 
        "You are the NFS Legal & Compliance Specialist. Audit the vendor against the vendor-risk-policy.pdf. "
            "Evaluate vendor liability, regulatory compliance, and risk categorization. Search historical vendor assessments "
            "to ensure consistency with past precedents. Enforce strict restrictions on High-Risk vendor approvals. " + evidence_contract,
        "tools": select_tools(*shared_tools, "get_vendor_history"),

    }

    ai_governance_subagent = {
        "name": "ai_governance_subagent",
        "description": "An AI governance specialist who evaluates responsible AI, data use, and governance policy evidence.",
        "system_prompt": 
            """
            You are the NFS AI Governance Specialist.
            You must call retrieve_document before writing any findings.

            Required calls:
            1. document_name="ai-governance-policy.pdf"
            query="responsible AI bias model provenance guardrails data retention"
            2. document_name="data-classification-policy.pdf"
            query="confidential corporate documents AI processing training retention"

            Do not use filesystem search tools as a substitute for retrieve_document.
            Do not produce findings until both retrieval calls return.
            Determine whether confidential corporate documents may be used for model
            training, and evaluate input/output guardrails, model provenance, bias
            mitigation, transparency, and data retention.
            """ + evidence_contract,
        "tools": select_tools(*shared_tools),
    }

    return [security_subagent, procurement_subagent, legal_subagent, ai_governance_subagent]