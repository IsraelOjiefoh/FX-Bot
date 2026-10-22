import argparse
import importlib
import os
from typing import Dict


SUPPORTED_SYMBOLS: Dict[str, str] = {
    "XAUUSD": "XAUUSD",
    "XAU/USD": "XAUUSD",
    "GOLD": "XAUUSD",
    "USTEC": "USTEC",
    "NASDAQ": "USTEC",
    "NAS100": "USTEC",
    "US100": "USTEC",
}


def normalize_symbol(symbol: str) -> str:
    key = symbol.strip().upper()
    if key in SUPPORTED_SYMBOLS:
        return SUPPORTED_SYMBOLS[key]
    raise ValueError(f"Unsupported symbol '{symbol}'. Supported aliases: {sorted(SUPPORTED_SYMBOLS)}")


def is_supported_symbol(symbol: str) -> bool:
    try:
        normalize_symbol(symbol)
        return True
    except ValueError:
        return False


class MT5Bot:
    def __init__(
        self,
        login: int,
        password: str,
        server: str,
        terminal_path: str = "",
        lot: float = 0.01,
        deviation: int = 20,
        sl_points: int = 500,
        tp_points: int = 1000,
        dry_run: bool = False,
        mt5_module=None,
    ):
        self.login = login
        self.password = password
        self.server = server
        self.terminal_path = terminal_path
        self.lot = lot
        self.deviation = deviation
        self.sl_points = sl_points
        self.tp_points = tp_points
        self.dry_run = dry_run
        self.mt5 = mt5_module or importlib.import_module("MetaTrader5")

    def initialize(self) -> None:
        kwargs = {"login": self.login, "password": self.password, "server": self.server}
        if self.terminal_path:
            kwargs["path"] = self.terminal_path
        if not self.mt5.initialize(**kwargs):
            raise RuntimeError(f"MT5 initialize failed: {self.mt5.last_error()}")

    def shutdown(self) -> None:
        self.mt5.shutdown()

    def _build_request(self, symbol: str, side: str) -> dict:
        side = side.lower().strip()
        if side not in {"buy", "sell"}:
            raise ValueError("side must be either 'buy' or 'sell'")

        symbol = normalize_symbol(symbol)
        if not self.mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Could not select symbol {symbol}")

        tick = self.mt5.symbol_info_tick(symbol)
        symbol_info = self.mt5.symbol_info(symbol)
        if tick is None or symbol_info is None:
            raise RuntimeError(f"Could not read market data for {symbol}")

        point = symbol_info.point
        if side == "buy":
            order_type = self.mt5.ORDER_TYPE_BUY
            price = tick.ask
            sl = price - self.sl_points * point
            tp = price + self.tp_points * point
        else:
            order_type = self.mt5.ORDER_TYPE_SELL
            price = tick.bid
            sl = price + self.sl_points * point
            tp = price - self.tp_points * point

        return {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": self.lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": self.deviation,
            "magic": 26042026,
            "comment": "fx-bot-market-order",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }

    def send_market_order(self, symbol: str, side: str):
        request = self._build_request(symbol, side)
        if self.dry_run:
            return {"retcode": "DRY_RUN", "request": request}

        result = self.mt5.order_send(request)
        if result is None:
            raise RuntimeError(f"order_send failed: {self.mt5.last_error()}")
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal MT5 bot for XAUUSD and NASDAQ aliases")
    parser.add_argument("--symbol", required=True, help="e.g. XAU/USD, XAUUSD, NASDAQ, USTEC")
    parser.add_argument("--side", required=True, choices=["buy", "sell"], help="Order side")
    parser.add_argument("--login", type=int, required=True, help="MT5 account login")
    parser.add_argument("--password", required=True, help="MT5 account password")
    parser.add_argument("--server", required=True, help="Broker server name")
    parser.add_argument(
        "--terminal-path",
        default=os.getenv("MT5_TERMINAL_PATH", ""),
        help="Path to terminal64.exe in Wine",
    )
    parser.add_argument("--lot", type=float, default=0.01, help="Lot size")
    parser.add_argument("--sl-points", type=int, default=500, help="Stop-loss points")
    parser.add_argument("--tp-points", type=int, default=1000, help="Take-profit points")
    parser.add_argument("--deviation", type=int, default=20, help="Price deviation")
    parser.add_argument("--dry-run", action="store_true", help="Build request only, do not send order")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bot = MT5Bot(
        args.login,
        args.password,
        args.server,
        terminal_path=args.terminal_path,
        lot=args.lot,
        sl_points=args.sl_points,
        tp_points=args.tp_points,
        deviation=args.deviation,
        dry_run=args.dry_run,
    )

    bot.initialize()
    try:
        result = bot.send_market_order(symbol=args.symbol, side=args.side)
        print(result)
    finally:
        bot.shutdown()


if __name__ == "__main__":
    main()
