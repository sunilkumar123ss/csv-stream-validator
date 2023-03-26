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


