import io
import unittest
from decimal import Decimal
from main import validate_stream, SchemaError


HEADER = 'order_id,customer_email,quantity,unit_price\n'


class CSVValidationTests(unittest.TestCase):
    def read(self, body):
        return list(validate_stream(io.StringIO(body, newline='')))

    def test_valid_typed_values_and_decimal_total(self):
        row = self.read(HEADER + 'A-1,a@example.invalid,3,0.10\n')[0]
        self.assertTrue(row.valid)
        self.assertEqual(row.values['total'], Decimal('0.30'))
        self.assertEqual(row.values['quantity'], 3)

    def test_missing_and_duplicate_headers(self):
        for data in ('', 'order_id,quantity\n', 'order_id,order_id,quantity,unit_price\n'):
            with self.subTest(data=data), self.assertRaises(SchemaError): self.read(data)

    def test_column_order_can_change(self):
        rows = self.read('quantity,unit_price,customer_email,order_id\n2,1.50,a@example.invalid,A\n')
        self.assertEqual(rows[0].values['total'], Decimal('3.00'))

    def test_field_count_error_does_not_abort_later_rows(self):
        rows = self.read(HEADER + 'A,a@example.invalid,1\nB,b@example.invalid,1,2.00\n')
        self.assertFalse(rows[0].valid)
        self.assertTrue(rows[1].valid)

    def test_multiple_field_errors_accumulated(self):
        row = self.read(HEADER + 'lower,invalid,0,1.234\n')[0]
        self.assertEqual(len(row.errors), 4)
        self.assertIsNone(row.values)

    def test_duplicate_id_flagged_even_if_prior_row_invalid(self):
        rows = self.read(HEADER + 'A,invalid,1,1\nA,a@example.invalid,1,1\n')
        self.assertIn('duplicate order_id', rows[1].errors)

    def test_quoted_comma_is_one_field(self):
        row = self.read(HEADER + 'A,"a,b@example.invalid",1,2.00\n')[0]
        self.assertEqual(len(row.errors), 1)
        self.assertIn('customer_email', row.errors[0])

    def test_malformed_quote_reports_terminal_error(self):
        rows = self.read(HEADER + 'A,"unterminated,1,2.00\n')
        self.assertEqual(len(rows), 1)
        self.assertIn('CSV syntax error', rows[0].errors[0])

    def test_quantity_and_price_ranges(self):
        for quantity, price in [('1e3', '1'), ('-1', '1'), ('1', '-2'), ('1', '1e2'), ('1000000000', '1')]:
            with self.subTest(quantity=quantity, price=price):
                self.assertFalse(self.read(HEADER + 'A,a@example.invalid,{},{}\n'.format(quantity, price))[0].valid)


if __name__ == '__main__':
    unittest.main()
