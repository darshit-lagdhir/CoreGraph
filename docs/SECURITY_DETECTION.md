# CoreGraph: Security & Detection (Simplified)

This document explains how we keep the system secure.

## 1. Internal Security
The application runs inside a locked "Faraday Cage." It does not allow random connections. Only the specific database and cache are allowed to talk to the main engine.

## 2. Detecting Threats
The system constantly watches the data for strange patterns. If a piece of data tries to create too many connections too quickly, it is flagged as a threat.

## 3. Self-Defense (SIGKILL Survival)
If an attacker manages to crash a part of the system, it doesn't matter. The system uses a "Shared-Memory Heartbeat" to instantly restart the crashed part and continue working safely.
