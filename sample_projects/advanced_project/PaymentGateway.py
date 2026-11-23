"""Advanced Project: Multi-Feature Payment Gateway Service.

Demonstrates advanced security vulnerabilities across multiple OWASP categories:
1. Hardcoded AWS access credentials (OWASP A05)
2. Insecure deserialization via pickle (OWASP A08)
3. Path traversal in receipt retrieval (OWASP A01)
4. Weak cryptography via MD5 (OWASP A02)
5. Overly long nested function complexity
"""
import os
import pickle
import hashlib


# VULNERABILITY: Hardcoded AWS Credential Key
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"


def process_serialized_payment_batch(serialized_data_bytes):
    """Deserialize payment payload from untrusted client network source."""
    # VULNERABILITY: Insecure Deserialization via pickle.loads
    payment_batch = pickle.loads(serialized_data_bytes)
    return payment_batch


def read_customer_receipt_file(base_dir, user_requested_filename):
    """Read saved payment receipt file from disk."""
    # VULNERABILITY: Path Traversal via unvalidated path concatenation
    target_path = os.path.join(base_dir, user_requested_filename)
    with open(target_path, "r", encoding="utf-8") as f:
        return f.read()


def compute_legacy_checksum(data_string):
    """Generate message digest for integrity check."""
    # VULNERABILITY: Weak Cryptography - MD5 is vulnerable to collision attacks
    hasher = hashlib.md5()
    hasher.update(data_string.encode("utf-8"))
    return hasher.hexdigest()


def execute_complex_transaction_workflow(client_id, amount, currency, metadata, options, flags):
    """Overly long function exceeding recommended modularity threshold."""
    if client_id is None:
        return {"status": "error", "message": "Invalid client"}
    if amount <= 0:
        return {"status": "error", "message": "Invalid amount"}
    if currency not in ["USD", "EUR", "GBP", "INR"]:
        return {"status": "error", "message": "Unsupported currency"}

    # Nesting level 1
    if options.get("verify_fraud"):
        # Nesting level 2
        if metadata.get("risk_score", 0) > 80:
            # Nesting level 3
            if not flags.get("override_fraud"):
                return {"status": "declined", "reason": "High fraud risk score"}
            else:
                audit_log = "Fraud override approved by supervisor"
        else:
            audit_log = "Standard risk assessment passed"
    else:
        audit_log = "Fraud check bypassed"

    step_1 = f"Transaction initiated for {client_id}: {amount} {currency}"
    step_2 = f"Fee calculated: {amount * 0.025}"
    step_3 = f"Currency settlement: {currency} clearing network"
    step_4 = f"Ledger debit balance updated: {client_id}"
    step_5 = f"Audit recorded: {audit_log}"
    step_6 = "Dispatching notification webhook to merchant endpoint"

    summary = {
        "client": client_id,
        "amount": amount,
        "currency": currency,
        "steps": [step_1, step_2, step_3, step_4, step_5, step_6],
        "state": "COMPLETED"
    }
    return summary
