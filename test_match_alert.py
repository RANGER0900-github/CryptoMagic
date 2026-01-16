"""Test match alert Telegram notification feature"""
import os
import sys
import time

# Create a test address file with one known address
test_addresses = ["0x1234567890123456789012345678901234567890"]
with open('test_addresses.txt', 'w') as f:
    f.write('\n'.join(test_addresses))

# Create a test FoundMATCHAddr.txt with sample match (as if worker found it)
test_match_content = """[WORKER 1]
0x1234567890123456789012345678901234567890
a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
abandon ability able about above absent absolute absorb abstract abuse access accident account accuse
b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2
------------------------- MMDRZA.Com -------------------
"""

with open('FoundMATCHAddr.txt', 'w') as f:
    f.write(test_match_content)

print("✅ Test files created:")
print(f"  - test_addresses.txt: {test_addresses}")
print(f"  - FoundMATCHAddr.txt: Sample match entry")
print("\nMatch alert format test:")
print(test_match_content)
