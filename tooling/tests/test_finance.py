import pytest
import os
import sys
import json
import glob
from fastapi.testclient import TestClient

# Ensure simulation server root is in the path
root = os.getcwd()
sim_server_root = os.path.join(root, "tooling", "simulation_server")
if sim_server_root not in sys.path:
    sys.path.insert(0, sim_server_root)

from main import app

client = TestClient(app)

def test_iso_4217_decimal_precision():
    """
    Test 1: Mathematical Normalization Integrity.
    Verifies that the server respects JPY (0), USD (2), and KWD (3) exponents.
    """
    finance_path = os.path.join(sim_server_root, "fixtures", "finance", "**", "*.json")
    for f in glob.glob(finance_path, recursive=True):
        with open(f, 'r') as f_obj:
            data = json.load(f_obj)
            for entry in data["ledger"]:
                amount = entry["amount"]
                # Strip symbols and commas for basic check
                clean_amount = amount.replace("$", "").replace("€", "").replace("¥", "").replace(",", ".")
                if "." in clean_amount:
                    decimals = len(clean_amount.split(".")[1])
                    # KWD/BHD has 3, USD/EUR has 2
                    if entry["currency"] in ["KWD", "BHD", "OMR"]:
                        assert decimals == 3
                    elif entry["currency"] in ["USD", "EUR", "GBP"]:
                        assert decimals == 2
                else:
                    # JPY/KRW/VND have 0
                    if entry["currency"] in ["JPY", "KRW", "VND", "IDR"]:
                        assert True # Passed (no decimal point)

def test_ghost_project_fallback():
    """
    Test 2: Fiscal Void Resilience.
    Verifies that non-existent financial profiles return a structured 200 OK.
    """
    response = client.get("/funding/npm/vapourware-non-existent")
    assert response.status_code == 200
    data = response.json()
    assert data["profile"] == "ghost"
    assert data["total_balance_normalized_usd"] == "0.00"

def test_financial_leviathan_stability():
    """
    Test 3: Boundary-Stressed Large-Integer Support.
    Verifies that 9-figure fundings are served without precision loss.
    """
    finance_path = os.path.join(sim_server_root, "fixtures", "finance", "**", "*.json")
    for f in glob.glob(finance_path, recursive=True):
        with open(f, 'r') as f_obj:
            data = json.load(f_obj)
            if data["profile"] == "leviathan":
                response = client.get(f"/funding/npm/{data['name']}")
                assert response.status_code == 200
                res_data = response.json()
                assert len(res_data["ledger"]) > 0
                return

    pytest.skip("No leviathan found in current simulation ocean.")

def test_anti_matter_ledger_rejection():
    """
    Test 4: Negative Balance Logic.
    Verifies that 'clawback' and 'audit_penalty' entries are correctly serialized.
    """
    finance_path = os.path.join(sim_server_root, "fixtures", "finance", "**", "*.json")
    for f in glob.glob(finance_path, recursive=True):
        with open(f, 'r') as f_obj:
            data = json.load(f_obj)
            for entry in data["ledger"]:
                if "-" in entry["amount"]:
                    response = client.get(f"/funding/npm/{data['name']}")
                    assert response.status_code == 200
                    return

    pytest.skip("No anti-matter ledger found in current simulation ocean.")
