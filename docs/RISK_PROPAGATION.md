# CoreGraph: Risk Propagation (Simplified)

This document explains how we track danger across the graph.

## 1. The Blast Radius
When the system finds a dangerous node (like a malicious user or file), it checks everything connected to it. This is called the "Blast Radius."

## 2. Visual Warnings
If a node is dangerous, it turns red on the screen. If the danger is spreading, the connected nodes will also start flashing red.

## 3. Quarantine
If the danger is severe, the system locks that part of the graph (Quarantine). It turns white and stops interacting with the rest of the healthy data.
