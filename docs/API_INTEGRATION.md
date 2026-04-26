# CoreGraph: API Integration (Simplified)

This document explains how other systems can talk to CoreGraph.

## 1. The Air-Gapped Rule
First and foremost: CoreGraph is designed to be "Air-Gapped." This means it runs on an internal network. Outside internet traffic cannot reach it unless explicitly allowed.

## 2. WebSockets for Live Data
We use a technology called WebSockets to send live updates to the screen (HUD). WebSockets keep a permanent connection open, which is much faster than asking for updates over and over.

## 3. REST API
For basic tasks (like starting the system or checking if it is healthy), we use standard web requests (REST). 
- All data is checked and validated before the system accepts it.
- If invalid data is sent, the system rejects it immediately to stay safe.
