#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime
from decimal import Decimal


def parse_amount(value):
    """Amounts arrive as numbers or as strings like "4,804.15"."""
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return Decimal(str(value))


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue 
        if not isinstance(event, dict):
            continue
        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        ts = parse_ts(event["ts"])
        current = latest.get(txn_id)
        if current is None or ts > current[0]:
            latest[txn_id] = (ts, event)

total = Decimal("0")
count = 0
for _, event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
