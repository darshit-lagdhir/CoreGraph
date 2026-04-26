# CoreGraph: The Hadronic Core (Simplified)

This document explains the "engine" of our system in easy English.

## 1. What is the Core?
The Core is the brain of the application. It processes all 3.81 million nodes very quickly.

## 2. How it is Built
- **Small and Fast**: The core is packaged in a tiny 155MB container.
- **Zero Waste**: It does not waste memory. We use simple binary data (zeros and ones packed tightly) instead of heavy text files to track everything.
- **Self-Healing**: If a part of the core crashes, it automatically restarts and picks up exactly where it left off in less than 150 milliseconds.

## 3. Processing Power
The core is designed to maximize your computer's power:
- On powerful computers, it uses every available CPU core to process data instantly.
- On weak computers, it slows down gracefully but never stops working.
