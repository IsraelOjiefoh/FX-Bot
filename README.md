# FX-Bot

Minimal Python MetaTrader 5 (MT5) bot scaffold for Linux (via Wine) focused on:

- `XAU/USD` (Gold) → `XAUUSD`
- `NASDAQ` (US tech index) → `USTEC` (with common aliases supported)

## Quick start

### 1) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Install MT5 terminal with Wine

1. Install Wine on your Linux host.
2. Install MT5 terminal inside Wine.
3. Note the MT5 terminal path (example):
   `~/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe`

### 3) Run the bot

```bash
python fx_bot.py \
  --symbol XAU/USD \
  --side buy \
  --login 123456 \
  --password "YOUR_PASSWORD" \
  --server "YOUR_BROKER_SERVER" \
  --terminal-path "$HOME/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"
```

For NASDAQ, you can use aliases such as `NASDAQ`, `NAS100`, `USTEC`, or `US100`.

## Safety

- Start with a demo account.
- Validate symbol names in your broker terminal.
- Use small lot sizes and adjust SL/TP carefully.
- Use `--dry-run` to validate request creation without sending orders.