# CoreGraph: Data Ingestion Pipeline (Simplified)

This document explains how we load data into the system.

## 1. The Challenge
We need to load 3.81 million nodes. Doing this one by one would take hours.

## 2. The Phalanx Solution
We built a pipeline that loads 150,000 nodes every second. 
- It groups data into large "batches."
- It uses a direct copy command (`PG_COPY`) to push data straight into the database quickly.

## 3. Error Handling
If a batch contains bad data, the system simply drops that batch and logs an error. It does not crash, and the rest of the data continues to load safely.
