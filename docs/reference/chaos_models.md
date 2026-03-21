# Chaos Engineering: The Poisson Distribution Model

## 1. Introduction

The Chaos Engine utilizes a mathematical model for failure injection based on the Poisson Distribution. The probability of k failure events occurring in a given time interval is modeled as:

UTF8P(k \text{ events in interval}) = \frac{\lambda^k e^{-\lambda}}{k!}UTF8

Where $\lambda$ (Lambda) represents the "Chaos Intensity Factor."

## 2. Intensity Profiles
- **Low Intensity ($\lambda = 0.5$):** Simulates standard developer errors (e.g., accidental linting violations, unformatted files).
- **High Intensity ($\lambda = 5.0$):** Simulates a "Worst-Case Deployment" scenario, where network partitions, database locks, and malformed telemetry streams occur simultaneously across the cluster.

## 3. Failure Vector Mapping
The 16-worker Celery cluster is rigorously tested utilizing this probabilistic model to reveal latent race conditions within the non-blocking execution matrices.
