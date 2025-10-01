# MURF Token Dashboard

Real-time dashboard for MURF token with live price data, OTC transactions, and holder statistics.

## Features

- 🚀 **Live MURF Price**: Real-time price from CoinGecko API
- 📊 **Price Chart**: Interactive Chart.js with historical data
- 💰 **OTC Transactions**: Type 7 KTA + Type 0 MURF detection
- 🏆 **Top Holders**: 1,528 MURF holders with rankings
- 📈 **Market Data**: FDV, Market Cap, Exchange Rate
- ☕ **Donation**: Support the project

## Data Sources

- **Keeta Network API**: Blockchain transaction data
- **CoinGecko API**: Real-time KTA price
- **SQLite Database**: Price history and OTC transactions
- **Airdrop Analysis**: 1,528 holders from airdrop wallet

## Statistics

- **Total Holders**: 1,528
- **Total Circulation**: 59.3B MURF
- **Top Holder**: 333.36M MURF
- **Database**: SQLite with persistent storage

## Deployment

This dashboard is deployed on Railway and includes:

1. **Real-time API Integration**
2. **Database Persistence**
3. **Holder Rankings**
4. **OTC Transaction Detection**
5. **Professional UI/UX**

## Files

- `real_live_dashboard.py` - Main dashboard application
- `murf_holders_db.py` - Holders database management
- `price_history_db.py` - Price history storage
- `otc_transactions_db.py` - OTC transactions storage
- `populate_holders_data.py` - Data population script

## API Endpoints

- `/` - Main dashboard
- `/stats` - JSON statistics
- `/api/price` - Price data
- `/api/holders` - Holders data

Built with Python Flask and deployed on Railway.