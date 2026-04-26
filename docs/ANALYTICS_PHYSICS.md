# CoreGraph: Physics and Speed (Simplified)

This document explains the raw speed of our application.

## 1. Binary Speed
Instead of processing slow, readable text files (like JSON), our system converts everything into tiny, unreadable binary blocks. This makes the system hundreds of times faster.

## 2. Smooth Visuals
We measure speed in "Frames Per Second" (FPS). Our goal is a smooth 144Hz experience. This means the screen updates 144 times every second. To achieve this, our math and data processing have to finish in less than 7 milliseconds.

## 3. No Stuttering (Jitter-Free)
If the system gets overwhelmed, it does not freeze. It simply skips a minor update and prioritizes keeping the visual screen smooth and responsive.
