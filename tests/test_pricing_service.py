import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError

class TestPricingService(unittest.TestCase):
	
	def setUp(self):
		self.pricing = PricingService()
	

	def test_subtotal_success(self):
		items = [ CartItem("Arroz", 100, 2), CartItem("Tallarines", 50, 1) ]
		self.assertEqual(self.pricing.subtotal_cents(items), 250)
	
	def test_subtotal_invalid_qty(self):
		with self.assertRaises(PricingError):
			self.pricing.subtotal_cents([ CartItem("Arroz", 100, 0) ])
	
	def test_subtotal_negative_price(self):
		with self.assertRaises(PricingError):
			self.pricing.subtotal_cents([ CartItem("Arroz", -10, 1) ])
	

	def test_apply_coupon_none(self):
		self.assertEqual(self.pricing.apply_coupon(1000, None), 1000)
		self.assertEqual(self.pricing.apply_coupon(1000, ""), 1000)
		self.assertEqual(self.pricing.apply_coupon(1000, "   "), 1000)
	
	def test_apply_coupon_save10(self):
		self.assertEqual(self.pricing.apply_coupon(1000, "SAVE10"), 900)
	
	def test_apply_coupon_cpl2000(self):
		self.assertEqual(self.pricing.apply_coupon(5000, "CLP2000"), 3000)
		self.assertEqual(self.pricing.apply_coupon(1500, "CLP2000"), 0)
	
	def test_apply_coupon_invalid(self):
		with self.assertRaises(PricingError):
			self.pricing.apply_coupon(1000, "invalid coupon")


	def test_tax_cents_countries(self):
		self.assertEqual(self.pricing.tax_cents(1000, "Cl"), 190)
		self.assertEqual(self.pricing.tax_cents(1000, "EU"), 210)
		self.assertEqual(self.pricing.tax_cents(1000, "US"), 0)
	
	def test_tax_unsupported_country(self):
		with self.assertRaises(PricingError):
			self.pricing.tax_cents(1000, "ZAR")
	

	def test_shipping_cl(self):
		self.assertEqual(self.pricing.shipping_cents(25000, "CL"), 0)
		self.assertEqual(self.pricing.shipping_cents(15000, "CL"), 2500)
	
	def test_shipping_us_eu(self):
		self.assertEqual(self.pricing.shipping_cents(1000, "US"), 5000)
		self.assertEqual(self.pricing.shipping_cents(1000, "EU"), 5000)
	
	def test_shipping_unsupported_country(self):
		with self.assertRaises(PricingError):
			self.pricing.shipping_cents(1000, "ZAR")
	

	def test_total_cents_full_flow(self):
		items = [CartItem("Arroz", 10000, 2)]
		total = self.pricing.total_cents(items, "SAVE10", "CL")
		self.assertEqual(total, 23920) 