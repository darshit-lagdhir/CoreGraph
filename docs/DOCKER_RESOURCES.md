# CoreGraph: Docker & Resources Guide

This document explains how our application runs safely inside Docker containers.

## 1. What is Docker?
Docker is a tool that packages our code into a "container." Think of a container as a tiny, isolated computer that has exactly what our app needs to run, and nothing else.

## 2. The Distroless Container
Our main container is "Distroless." This means:
- **Tiny Size**: It only takes up 155MB of space.
- **Super Secure**: It has no extra tools (like a command line or shell). Hackers cannot run commands inside it because those tools simply do not exist.
- **Air-Gapped Ready**: It is designed to work perfectly even if you completely disconnect it from the internet.

## 3. Resource Limits
We control exactly how much power the system can use:
- **CPU Control**: It can use all cores if needed, but we can limit it to run smoothly even on weak computers (Potato-Tier).
- **Memory Limit**: We cap the memory usage so it never crashes the host computer.

## 4. Multi-Architecture
The container is built to run on almost any modern computer:
- It works on standard Intel/AMD processors (x86_64).
- It also works perfectly on ARM processors (like Apple Silicon or edge devices).
