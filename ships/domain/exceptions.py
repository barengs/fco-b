"""
Ship Domain Exceptions
Business rule violations and domain-specific errors for vessel management.
"""

class ShipDomainException(Exception):
    """Base exception for ship domain errors."""
    pass

class QuotaExceededException(ShipDomainException):
    """Raised when allocated quota is completely exhausted."""
    pass

class InvalidVesselRegistrationException(ShipDomainException):
    """Raised when vessel registration format is invalid."""
    pass
