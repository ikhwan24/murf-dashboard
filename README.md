# 🚀 MURF Token Dashboard

**Real-time dashboard untuk MURF token dengan OTC trading monitoring, price tracking, dan holder analytics.**

![Dashboard Preview](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Flask](https://img.shields.io/badge/Flask-HTTP%20Server-green)
![Railway](https://img.shields.io/badge/Deploy-Railway-purple)

## 📊 **Live Dashboard Features**

### 💰 **Real-time Price Data**
- **MURF Price**: Live price dari OTC transactions
- **MURF FDV (USD)**: Fully Diluted Valuation dalam USD  
- **MURF Market Cap**: Market capitalization dalam USD
- **KTA Price**: Live price dari CoinGecko API

### 📈 **OTC Trading Features**
- **Type 7 MURF Trades**: Jumlah total OTC transactions
- **OTC Volume (1H)**: Volume trading dalam 1 jam terakhir
- **OTC Volume (1D)**: Volume trading dalam 24 jam terakhir
- **OTC Volume (Total)**: Total volume semua OTC transactions
- **Recent MURF Trades**: List transaksi OTC terbaru dengan:
  - KTA ↔ MURF amounts
  - Exchange rate (1 KTA = X MURF)
  - Sender/Receiver addresses
  - Timestamp (relative time)
  - Block explorer links

### 📊 **Chart & Analytics**
- **Price History Chart**: Interactive chart dengan Chart.js
- **Timeframe Selection**: 1H, 4H, 1D, 1W
- **Real-time Updates**: Chart update hanya saat ada OTC baru
- **Historical Data**: Data tersimpan di database

### 👥 **Token Holders**
- **Top MURF Holders**: List holder dengan balance terbesar
- **Holder Statistics**: Total holders, circulation, airdropped
- **Real-time Balance**: Balance update setiap jam
- **OTC Participants**: Auto-track penjual/pembeli OTC
- **Explorer Links**: Link ke Keeta explorer untuk setiap holder

### 💾 **Data Persistence**
- **OTC Transactions DB**: Simpan semua OTC transactions
- **Price History DB**: Simpan historical price data
- **MURF Holders DB**: Simpan data token holders
- **Duplicate Prevention**: Mencegah data duplikat
- **API Fallback**: Gunakan database saat API error

### 🔄 **Smart Features**
- **Auto-refresh**: Holders data refresh setiap jam
- **Real-time OTC Detection**: Deteksi OTC baru secara real-time
- **API Error Handling**: Graceful fallback ke database
- **Timezone Fix**: Volume calculation dengan UTC timezone
- **Data Validation**: Hanya data valid yang ditampilkan

### 🎨 **UI/UX Features**
- **Modern Design**: Gradient cards dengan hover effects
- **Responsive Layout**: Mobile-friendly design
- **Loading States**: Smooth loading animations
- **Error Handling**: User-friendly error messages
- **Manual Refresh**: Button untuk refresh manual

### ☕ **Support Features**
- **Donation Section**: "Buy Me a Coffee" dengan address
- **MURF CA Verification**: Contract address dengan copy button
- **Professional Styling**: Eye-catching design dengan kontras tinggi

## 🚀 **Quick Start**

### **Prerequisites**
```bash
Python 3.11+
pip install requests
```

### **Local Development**
```bash
# Clone repository
git clone https://github.com/ikhwan24/murf-dashboard.git
cd murf-dashboard

# Install dependencies
pip install -r requirements.txt

# Run dashboard
python real_live_dashboard.py

# Access dashboard
http://localhost:5000
```

### **Production Deployment (Railway)**
```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to production"
git push origin main

# 2. Railway auto-deploy
# Railway akan otomatis detect dan deploy
```

## 📁 **Project Structure**

```
murf-dashboard/
├── real_live_dashboard.py      # Main dashboard application
├── price_history_db.py        # Price history database
├── otc_transactions_db.py     # OTC transactions database
├── murf_holders_db.py         # Token holders database
├── smart_holders_manager.py   # Smart holders management
├── requirements.txt           # Python dependencies
├── README.md                 # Documentation
└── *.db                      # SQLite databases
```

## 🔧 **Technical Features**

### **Backend Architecture**
- **Flask HTTP Server**: Lightweight web server
- **SQLite Databases**: Local data persistence
- **Keeta API Integration**: Real-time blockchain data
- **CoinGecko API**: External price data
- **Multi-threading**: Concurrent API calls

### **Data Flow**
1. **API Data Fetch**: Keeta API → Real-time OTC detection
2. **Data Processing**: Parse Type 7 KTA + Type 0 MURF pairs
3. **Database Storage**: Save to SQLite with duplicate prevention
4. **UI Rendering**: Display with real-time updates
5. **Chart Updates**: Update only on new OTC transactions

### **Performance Optimizations**
- **Batch API Calls**: Multi-threading untuk speed
- **Database Indexing**: Fast queries
- **Caching**: Reduce API calls
- **Error Recovery**: Robust error handling

## 📊 **API Endpoints**

### **Keeta Network API**
- **History**: `https://rep2.main.network.api.keeta.com/api/node/ledger/history`
- **Account**: `https://rep2.main.network.api.keeta.com/api/node/ledger/account/{address}`
- **Limit**: 200 entries per request

### **CoinGecko API**
- **KTA Price**: `https://api.coingecko.com/api/v3/simple/price?ids=keeta&vs_currencies=usd`

## 🗄️ **Database Schema**

### **OTC Transactions**
```sql
CREATE TABLE otc_transactions (
    id INTEGER PRIMARY KEY,
    tx_hash TEXT UNIQUE,
    kta_amount REAL,
    murf_amount REAL,
    from_address TEXT,
    to_address TEXT,
    timestamp TEXT,
    block_hash TEXT
);
```

### **Price History**
```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    price REAL,
    volume REAL
);
```

### **MURF Holders**
```sql
CREATE TABLE murf_holders (
    id INTEGER PRIMARY KEY,
    address TEXT UNIQUE,
    current_balance REAL,
    total_received REAL,
    total_sent REAL,
    first_tx_date TEXT,
    last_tx_date TEXT,
    is_airdrop_recipient INTEGER
);
```

## 🔄 **Deployment**

### **Railway Deployment**
1. **Connect GitHub**: Link repository ke Railway
2. **Auto-deploy**: Railway detect changes otomatis
3. **Environment**: Production environment variables
4. **URL**: Railway provide public URL

### **Environment Variables**
```bash
PORT=5000                    # Server port
```

## 📈 **Monitoring & Analytics**

### **Real-time Metrics**
- **OTC Volume**: 1H, 1D, Total
- **Price Tracking**: Historical price data
- **Holder Analytics**: Top holders, distribution
- **Transaction Monitoring**: Real-time OTC detection

### **Data Sources**
- **Keeta Blockchain**: OTC transactions, holder data
- **CoinGecko**: KTA price data
- **Internal Database**: Historical data, caching

## 🛠️ **Development**

### **Adding New Features**
1. **Backend**: Modify `real_live_dashboard.py`
2. **Database**: Update schema files
3. **Frontend**: Modify HTML/CSS in main file
4. **Testing**: Test locally before push
5. **Deploy**: Push to GitHub for auto-deploy

### **Debugging**
- **Local Testing**: `python real_live_dashboard.py`
- **Database Check**: SQLite browser
- **API Testing**: Check API responses
- **Error Logs**: Terminal output

## 📞 **Support**

### **Donation**
**Buy Me a Coffee**: `keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay`

### **MURF Contract**
**Contract Address**: `keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm`

## 📄 **License**

MIT License - Feel free to use and modify!

## 🤝 **Contributing**

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

**🚀 MURF Dashboard - Real-time OTC Trading Monitor**

*Built with ❤️ for MURF token community*