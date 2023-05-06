"""Validate a stream of synthetic order CSV rows without loading the entire file."""
import argparse
import csv
from dataclasses import dataclass
from decimal import Decimal
import json
from pathlib import Path
import re
import sys


COLUMNS = ("order_id", "customer_email", "quantity", "unit_price")


class SchemaError(ValueError):
    pass


@dataclass(frozen=True)
class RowResult:
    line_number: int
    values: object
    errors: tuple

    @property
    def valid(self):
        return not self.errors
