import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult

class TestCheckoutService(unittest.TestCase):
	
	def setUp(self):
		self.mock_payments = Mock()
		self.mock_email = Mock()
		self.mock_fraud = Mock()
		self.mock_repo = Mock()
		self.mock_pricing = Mock()

		self.service = CheckoutService( payments=self.mock_payments, email=self.mock_email,
			fraud=self.mock_fraud, repo=self.mock_repo, pricing=self.mock_pricing
		)

	def test_checkout_invalid_user(self):
		result = self.service.checkout(user_id="", items=[], payment_token="tok", country="CL")
		self.assertEqual(result, "INVALID_USER")
	
	def test_checkout_pricing_error(self):
		self.mock_pricing.total_cents.side_effect = PricingError()
		result = self.service.checkout(user_id="user1", items=[], payment_token="tok", country="CL")
		self.assertEqual(result, "INVALID_CART:")
	
	def test_checkout_fraud_rejected(self):
		self.mock_pricing.total_cents.return_value = 1000
		self.mock_fraud.score.return_value = 85
		result = self.service.checkout(user_id="user1", items=[], payment_token="tok", country="CL")
		self.assertEqual(result, "REJECTED_FRAUD")
	
	def test_checkout_payment_failed(self):
		self.mock_pricing.total_cents.return_value = 1000
		self.mock_fraud.score.return_value = 10
		self.mock_payments.charge.return_value = ChargeResult(ok=False, reason="No funds")
		result = self.service.checkout(user_id="user1", items=[], payment_token="tok", country="CL")
		self.assertEqual(result, "PAYMENT_FAILED:No funds")
	
	def test_checkout_success_with_unknown_charge_id(self):
		self.mock_pricing.total_cents.return_value = 5000
		self.mock_fraud.score.return_value = 5
		self.mock_payments.charge.return_value = ChargeResult(ok=True, charge_id=None)
		result = self.service.checkout(user_id="user1", items=[], payment_token="tok", country="CL")
		self.assertTrue(result.startswith("OK:"))
		self.mock_repo.save.assert_called_once()

		order_saved = self.mock_repo.save.call_args[0][0]
		self.assertEqual(order_saved.payment_charge_id, "UNKNOWN")
	
	def test_checkout_full_success(self):
		self.mock_pricing.total_cents.return_value = 10000
		self.mock_fraud.score.return_value = 0
		self.mock_payments.charge.return_value = ChargeResult(ok=True, charge_id="ch_123")
		result = self.service.checkout(user_id="user1", items=[], payment_token="tok", country="CL")
		self.assertTrue(result.startswith("OK:"))
		self.mock_repo.save.assert_called_once()
		self.mock_email.send_receipt.assert_called_once()