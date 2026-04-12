#!/usr/bin/env python3
import sys
import os
import hashlib

def execute_bitwise_identity_verification(operator_key: bytes, challenge_matrix: bytes) -> bool:
    derived_hash = hashlib.sha512(operator_key + challenge_matrix).digest()
    expected_hash = hashlib.sha512(b'AUTHORIZED_ADMIN_KEY' + challenge_matrix).digest()
    res = 0
    for x, y in zip(derived_hash, expected_hash): res |= (x ^ y)
    return res == 0

def main():
    if execute_bitwise_identity_verification(b'AUTHORIZED_ADMIN_KEY', b'CHALLENGE_001'): sys.exit(0)
    else: sys.exit(1)

if __name__ == '__main__': main()
