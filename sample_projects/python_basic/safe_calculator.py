"""Basic Python Project: Safe Calculator Helper.

Demonstrates secure, clean, PEP 8 compliant Python coding practices:
- Type annotations
- Defensive parameter validation
- Specific exception handling
- Clean modular design
"""
from typing import Union, List


def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate the discounted total price securely.

    Args:
        price: Positive float representation of price.
        discount_percent: Discount between 0.0 and 100.0.

    Returns:
        Discounted price float.

    Raises:
        ValueError: If price or discount percentage are out of valid range.
    """
    if price < 0.0:
        raise ValueError("Price must be a non-negative number.")
    if not (0.0 <= discount_percent <= 100.0):
        raise ValueError("Discount percentage must be between 0.0 and 100.0.")

    discount_amount = price * (discount_percent / 100.0)
    return round(price - discount_amount, 2)


def process_batch_totals(amounts: List[float]) -> float:
    """Sum a list of numeric amounts safely."""
    try:
        return sum(float(x) for x in amounts)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric input in batch amounts: {exc}") from exc
