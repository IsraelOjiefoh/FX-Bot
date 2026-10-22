import types
import unittest

from fx_bot import MT5Bot, is_supported_symbol, normalize_symbol


class TestSupportedSymbols(unittest.TestCase):
    def test_normalize_xau_aliases(self):
        self.assertEqual(normalize_symbol("XAU/USD"), "XAUUSD")
        self.assertEqual(normalize_symbol("gold"), "XAUUSD")
        self.assertEqual(normalize_symbol("xauusd"), "XAUUSD")

    def test_normalize_nasdaq_aliases(self):
        self.assertEqual(normalize_symbol("NASDAQ"), "USTEC")
        self.assertEqual(normalize_symbol("nas100"), "USTEC")
        self.assertEqual(normalize_symbol("us100"), "USTEC")
        self.assertEqual(normalize_symbol("ustec"), "USTEC")

    def test_supported_symbol_guard(self):
        self.assertTrue(is_supported_symbol("XAU/USD"))
        self.assertTrue(is_supported_symbol("NASDAQ"))
        self.assertFalse(is_supported_symbol("EURUSD"))

    def test_dry_run_builds_request_for_nasdaq_alias(self):
        mt5 = types.SimpleNamespace(
            ORDER_TYPE_BUY=0,
            ORDER_TYPE_SELL=1,
            TRADE_ACTION_DEAL=2,
            ORDER_TIME_GTC=3,
            ORDER_FILLING_IOC=4,
            symbol_select=lambda symbol, selected: symbol == "USTEC" and selected,
            symbol_info_tick=lambda _symbol: types.SimpleNamespace(ask=19000.0, bid=18999.5),
            symbol_info=lambda _symbol: types.SimpleNamespace(point=0.1),
        )
        bot = MT5Bot(1, "p", "s", dry_run=True, mt5_module=mt5)
        result = bot.send_market_order("NASDAQ", "buy")
        self.assertEqual(result["retcode"], "DRY_RUN")
        self.assertEqual(result["request"]["symbol"], "USTEC")


if __name__ == "__main__":
    unittest.main()
