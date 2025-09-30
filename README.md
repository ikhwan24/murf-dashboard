# Keeta Network Token Monitor

Bot untuk memantau transaksi OTC MURF-KTA di blockchain Keeta Network.

## 🎯 Fitur

- **Real-time Monitoring**: Memantau transaksi MURF-KTA secara real-time
- **OTC Trade Detection**: Deteksi transaksi OTC (type 7) dengan analisis detail
- **Price Analysis**: Analisis harga dan volume trading
- **Alert System**: Notifikasi untuk perubahan harga, transaksi besar, dan OTC
- **Database Storage**: Menyimpan riwayat transaksi untuk analisis
- **Whale Detection**: Deteksi transaksi besar (whale trades)
- **Multi-Type Support**: Support berbagai jenis transaksi (0-10)

## 📊 Token yang Dimonitor

- **MURF**: `keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm`
- **KTA**: `keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg`

## 🚀 Cara Menjalankan

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Monitor

```bash
python run_monitor.py
```

### 3. Analisis Harga

```bash
python price_analyzer.py
```

### 4. Cek Notifikasi

```bash
python notification_system.py
```

## 📁 File Structure

```
├── keeta_monitor.py      # Main monitoring script
├── price_analyzer.py     # Price analysis tool
├── notification_system.py # Alert system
├── run_monitor.py        # Main runner
├── requirements.txt      # Dependencies
├── README.md            # Documentation
└── keeta_trades.db      # SQLite database (auto-created)
```

## 🔧 Konfigurasi

### Threshold Alert

Edit `notification_system.py` untuk mengubah threshold:

```python
self.price_change_threshold = 0.05  # 5% perubahan harga
self.large_trade_threshold = 10000000  # 10M token
self.volume_threshold = 100000000  # 100M volume
```

### Monitoring Interval

Edit `run_monitor.py` untuk mengubah interval:

```python
time.sleep(30)  # Check every 30 seconds
time.sleep(300)  # Update every 5 minutes
time.sleep(60)  # Check alerts every minute
```

## 📈 Database Schema

### Trades Table
- `id`: Primary key
- `timestamp`: Waktu transaksi
- `block_hash`: Hash block
- `from_address`: Alamat pengirim
- `to_address`: Alamat penerima
- `token_id`: ID token
- `amount_hex`: Jumlah dalam hex
- `amount_decimal`: Jumlah dalam desimal
- `trade_type`: Jenis transaksi

### Price History Table
- `id`: Primary key
- `timestamp`: Waktu
- `token_id`: ID token
- `price`: Harga
- `volume`: Volume

## 🔔 Alert Types

1. **Price Change Alert**: Perubahan harga > 5%
2. **Large Trade Alert**: Transaksi > 10M token
3. **OTC Trade Alert**: Transaksi OTC (type 7) terdeteksi
4. **Volume Spike Alert**: Lonjakan volume > 200%

## 🔄 Transaction Types Supported

- **Type 0**: Transfer
- **Type 1**: Mint
- **Type 2**: Burn
- **Type 3**: Freeze
- **Type 4**: Unfreeze
- **Type 5**: Approve
- **Type 6**: Revoke
- **Type 7**: OTC Trade ⭐ (Fokus utama)
- **Type 8**: Swap
- **Type 9**: Stake
- **Type 10**: Unstake

## 📊 Contoh Output

```
📊 Keeta Token Price Report
==================================================
⏰ Time: 2025-01-27T10:30:00

💰 Price Information:
   1 KTA = 258,620.69 MURF
   Ratio: 258620.68965517

📈 Volume (24h):
   MURF Volume: 1,000,000,000
   KTA Volume: 3,870
   Total Trades: 15

🔄 OTC Analysis:
   Total OTC Trades: 3
   OTC Volume: 30,000,000
   Average Price: 258620.68965517
   Buy/Sell/Swap: 1/1/1

📋 Recent OTC Trades:
   • 30,000,000 MURF... (swap) at 2025-01-27T10:25:00
   • 116 KTA... (buy) at 2025-01-27T10:20:00

🐋 Large Trades Detected:
   30,000,000 MURF at 2025-01-27T10:25:00
   116 KTA at 2025-01-27T10:25:00

🔍 Market Analysis:
   Active Trading: ✅
   High Volume: ✅
   Whale Activity: ✅
   OTC Activity: ✅
```

## 📊 Dashboard

### Desktop Dashboard
```bash
python dashboard.py
```

### Web Dashboard
```bash
python web_dashboard.py
# Buka http://localhost:5000
```

### Dashboard Runner
```bash
python run_dashboard.py
# Pilih jenis dashboard yang diinginkan
```

## 🛠️ Development

### Menambah Token Baru

Edit `keeta_monitor.py`:

```python
self.new_token = "keeta_new_token_id"
```

### Custom Alert Logic

Edit `notification_system.py`:

```python
def custom_alert_check(self):
    # Your custom logic here
    pass
```

### Dashboard Customization

Edit `dashboard.py` untuk mengubah tampilan desktop dashboard:

```python
def _create_statistics_panel(self, ax, stats: Dict):
    # Customize statistics display
    pass
```

Edit `web_dashboard.py` untuk mengubah tampilan web dashboard:

```python
HTML_TEMPLATE = """
<!-- Customize HTML template -->
"""
```

## 📞 Support

Untuk pertanyaan atau bantuan:
- Email: support@keeta.com
- Documentation: https://docs.keeta.com

## ⚠️ Disclaimer

Bot ini hanya untuk monitoring dan analisis. Tidak memberikan saran investasi. Gunakan dengan risiko sendiri.
