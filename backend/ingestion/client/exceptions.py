"""
Exceptions for network and registry interactions.
"""


class RegistryError(Exception):
    """Base exception for all registry client errors."""

    pass


class RegistryAddressError(RegistryError):
    """Raised when DNS resolution or host lookup fails."""

    pass


class RegistrySocketResetError(RegistryError):
    """Raised when a remote socket is forcibly reset."""

    pass


class RegistryHostDisconnectError(RegistryError):
    """Raised when the remote server terminates the connection."""

    pass


class RegistryTransportError(RegistryError):
    """Raised for low-level transport or connector failures."""

    pass


class RegistryTimeoutError(RegistryError):
    """Raised when a request exceeds timeout boundaries."""

    pass


class RegistryProtocolError(RegistryError):
    """Raised for malformed payloads or invalid responses."""

    pass


class RegistryRateLimitError(RegistryError):
    """Raised when an upstream registry enforces a rate limit."""

    pass
