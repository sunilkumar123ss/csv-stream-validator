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


def validate_stream(stream):
    reader = csv.reader(stream, strict=True)
    try:
        headers = next(reader)
    except StopIteration:
        raise SchemaError("CSV is empty; header row is required")
    except csv.Error as exc:
        raise SchemaError("invalid CSV header: " + str(exc)) from exc
    if len(set(headers)) != len(headers):
        raise SchemaError("duplicate column names")
    if set(headers) != set(COLUMNS):
        raise SchemaError("columns must be exactly: " + ", ".join(COLUMNS))
    seen_ids = set()
    while True:
        try:
            row = next(reader)
        except StopIteration:
            return
        except csv.Error as exc:
            yield RowResult(reader.line_num, None, ("CSV syntax error: " + str(exc),))
            return  # A malformed quote makes subsequent record boundaries ambiguous.
        line_number = reader.line_num
        if len(row) != len(headers):
            yield RowResult(line_number, None, ("expected four fields, found {}".format(len(row)),))
            continue
        raw = {name: value.strip() for name, value in zip(headers, row)}
        errors = []
        order_id = raw["order_id"]
        if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]*", order_id):
            errors.append("order_id must use uppercase letters, digits, and hyphens")
        elif order_id in seen_ids:
            errors.append("duplicate order_id")
        else:
            seen_ids.add(order_id)
        if not re.fullmatch(r"[^\s@,]+@[^\s@,]+\.[^\s@,]+", raw["customer_email"]):
            errors.append("customer_email must have a simple local@domain.tld shape")
        quantity = None
        if re.fullmatch(r"[0-9]+", raw["quantity"]) and len(raw["quantity"]) <= 9:
            quantity = int(raw["quantity"])
        if quantity is None or quantity < 1:
            errors.append("quantity must be an integer between 1 and 999999999")
        price = None
        if re.fullmatch(r"(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,2})?", raw["unit_price"]):
            price = Decimal(raw["unit_price"])
        else:
            errors.append("unit_price must be nonnegative, with at most 12 integer digits and 2 decimal places")
        values = None if errors else {"order_id": order_id, "customer_email": raw["customer_email"],
                                      "quantity": quantity, "unit_price": price,
                                      "total": quantity * price}
        yield RowResult(line_number, values, tuple(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path(__file__).resolve().parent / "sample.csv")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any row is invalid")
    args = parser.parse_args()
    invalid = 0
    try:
        with args.file.open(encoding="utf-8", newline="") as stream:
            for row in validate_stream(stream):
                invalid += not row.valid
                print(json.dumps({"line": row.line_number, "valid": row.valid,
                                  "values": row.values, "errors": row.errors}, default=str))
    except (OSError, UnicodeError, SchemaError) as exc:
        parser.error(str(exc))
    return 1 if args.strict and invalid else 0


if __name__ == "__main__":
    sys.exit(main())
