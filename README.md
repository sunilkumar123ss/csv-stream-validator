# CSV Stream Validator

Validate order imports one record at a time and keep precise decimal totals.

All bundled examples use synthetic data.

## Run

Requires Python 3.9 or later; no third-party packages or network access are needed.

```sh
python3 main.py
python3 main.py --help
python3 -m unittest -v
```

Run these commands from this repository's directory. The demo can also be launched from any directory by passing the absolute path to `main.py`.

## How it works

The reader requires exactly the four named columns, in any order, with no duplicate headers. It checks uppercase order IDs, a deliberately simple email shape, positive integer quantities, and nonnegative prices with at most two decimal places. Valid rows carry typed values and `Decimal` totals. Invalid rows carry all detected field errors and no partial typed record.

Row results identify the ending physical line number, including quoted multiline records. Duplicate IDs are tracked even when the first row has other errors. Work is O(input size), with memory for the current record and the set of observed IDs.

## Reuse

```python
import io
from decimal import Decimal
from main import validate_stream

text = "order_id,customer_email,quantity,unit_price\nA-1,a@example.invalid,3,0.10\n"
row = next(validate_stream(io.StringIO(text)))
assert row.valid
assert row.values["total"] == Decimal("0.30")
```

## Demo behavior

The bundled `sample.csv` intentionally mixes valid and invalid synthetic rows. Default demo exit status is 0 so the report can be inspected. Use `python3 main.py --strict` to return 1 for row failures, or `python3 main.py --file orders.csv --strict` for another file. The bundled file resolves relative to `main.py`, independent of the current working directory.

## Boundaries

The email rule is a shape check, not full RFC validation or delivery verification. IDs and numeric bounds are an example import policy. CSV syntax errors terminate processing because damaged quoting can obscure later record boundaries. The `csv` module's field-size limit still applies. Keeping seen IDs means memory grows with unique IDs; large imports may need an external uniqueness index. Missing or invalid headers cause exit status 2.

## Verification

`test_main.py` exercises boundary conditions, invalid inputs, and meaningful behavior specific to this implementation. The default demo is deterministic and completes without external services. See the collection's verification report for the recorded run; run the commands above to verify this repository independently.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
