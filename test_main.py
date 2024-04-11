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









if __name__ == '__main__':
    unittest.main()
