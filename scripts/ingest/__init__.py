"""Shared state-backed ingestion machinery for Thermal Extraction Devices.

State adapters live under :mod:`scripts.ingest.states` and drive a common
pipeline: fetch -> snapshot -> normalize -> aggregate -> generate -> validate.

The reusable layer deliberately knows nothing about any specific regulator.
"""

__version__ = "0.1.0"
