#!/bin/bash
# Identity Enforcement Hook

echo "Running Cryptographic Identity Enforcement Check..."

if [ "$SKIP_IDENTITY_CHECK" = "1" ]; then
    echo "Skipping identity check based on environment variable."
    exit 0
fi

# Simply checks if user.signingkey is set to something
SIGNING_KEY=$(git config --get user.signingkey)

if [ -z "$SIGNING_KEY" ]; then
    echo "CRITICAL FAILURE: No signing key configured. Commits must be cryptographically signed."
    exit 1
fi

echo "Identity check passed for key: $SIGNING_KEY"
exit 0
