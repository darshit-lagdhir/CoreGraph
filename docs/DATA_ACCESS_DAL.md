# CoreGraph: Data Access & Database Guide

This document explains how we store and manage data in simple English. 

## 1. The Main Database (PostgreSQL)
We use PostgreSQL to permanently save our 3.81 million nodes. It is like a giant, very safe filing cabinet.
- **Super Safe (ACID)**: If the power goes out, Postgres uses special logs (called WAL) to make sure no data is corrupted.
- **Fast Loading**: We use a technique called `PG_COPY` to load 150,000 items per second. It is much faster than saving them one by one.

## 2. The Fast Cache (Redis)
We use Redis as our temporary fast memory. It is like a notepad on your desk.
- **Speed**: It tracks live changes to the nodes instantly.
- **Recovery**: If it crashes, it reads a backup file (AOF) to restore everything in less than half a second.

## 3. How They Work Together
1. When new data comes in, it goes to Postgres for safe keeping.
2. The live system reads from Redis so the visual map (HUD) stays fast and smooth.
3. Everything runs inside isolated Docker containers, so it never messes up your computer's files.
