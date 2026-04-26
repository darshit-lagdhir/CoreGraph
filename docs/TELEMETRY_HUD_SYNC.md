# CoreGraph: Telemetry & HUD Sync (Simplified)

This document explains the visual map on your screen.

## 1. The HUD (Heads Up Display)
The HUD is your window into the 3.81 million nodes. It runs at an incredibly fast 144Hz.

## 2. Synchronization
When a node changes in the database, the HUD updates instantly. We achieve this by using a high-speed connection that skips slow text formatting and sends raw binary data straight to your screen.

## 3. Smoothness
The system never stutters. It calculates precisely how much time it has to draw the screen (6.94 milliseconds). If it takes too long, it skips minor details to ensure the map remains smooth and interactive.
