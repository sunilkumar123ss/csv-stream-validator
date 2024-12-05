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






if __name__ == '__main__':
    unittest.main()
