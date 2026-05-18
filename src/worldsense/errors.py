class WorldSenseError(Exception):
    """Base error for this package."""


class LocationNotFoundError(WorldSenseError):
    """Raised when geocoding fails to resolve a location."""


class ExternalServiceError(WorldSenseError):
    """Raised when an external API cannot be reached reliably."""
