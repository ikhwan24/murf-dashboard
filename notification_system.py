#!/usr/bin/env python3
"""
Keeta Notification System
Sistem notifikasi untuk perubahan harga dan transaksi besar
"""

import smtplib
import json
import sqlite3
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeetaNotifier:
    def __init__(self, db_path: str = "keeta_trades.db"):
        self.db_path = db_path
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        
        # Threshold untuk notifikasi
        self.price_change_threshold = 0.05  # 5% perubahan harga
        self.large_trade_threshold = 10000000  # 10M token
        self.volume_threshold = 100000000  # 100M volume
        
    def get_latest_price(self) -> float:
        """Ambil harga terbaru MURF/KTA"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ambil transaksi terbaru untuk kedua token
        cursor.execute('''
            SELECT token_id, amount_decimal, timestamp 
            FROM trades 
            WHERE token_id IN (?, ?) 
            ORDER BY timestamp DESC 
            LIMIT 20
        ''', (self.murf_token, self.kta_token))
        
        trades = cursor.fetchall()
        conn.close()
        
        if len(trades) < 2:
            return 0.0
        
        # Hitung rasio dari transaksi terbaru
        murf_trades = [t for t in trades if t[0] == self.murf_token]
        kta_trades = [t for t in trades if t[0] == self.kta_token]
        
        if murf_trades and kta_trades:
            latest_murf = murf_trades[0]
            latest_kta = kta_trades[0]
            
            if latest_murf[1] > 0 and latest_kta[1] > 0:
                return latest_murf[1] / latest_kta[1]
        
        return 0.0
    
    def get_previous_price(self) -> float:
        """Ambil harga sebelumnya untuk perbandingan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ambil transaksi dari 1 jam yang lalu
        one_hour_ago = datetime.now().timestamp() - 3600
        
        cursor.execute('''
            SELECT token_id, amount_decimal, timestamp 
            FROM trades 
            WHERE token_id IN (?, ?) AND timestamp < ?
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (self.murf_token, self.kta_token, datetime.fromtimestamp(one_hour_ago).isoformat()))
        
        trades = cursor.fetchall()
        conn.close()
        
        if len(trades) < 2:
            return 0.0
        
        murf_trades = [t for t in trades if t[0] == self.murf_token]
        kta_trades = [t for t in trades if t[0] == self.kta_token]
        
        if murf_trades and kta_trades:
            prev_murf = murf_trades[0]
            prev_kta = kta_trades[0]
            
            if prev_murf[1] > 0 and prev_kta[1] > 0:
                return prev_murf[1] / prev_kta[1]
        
        return 0.0
    
    def check_price_change(self) -> Dict:
        """Cek perubahan harga"""
        current_price = self.get_latest_price()
        previous_price = self.get_previous_price()
        
        if current_price == 0 or previous_price == 0:
            return {"change": 0, "percentage": 0, "alert": False}
        
        change = current_price - previous_price
        percentage = (change / previous_price) * 100
        
        alert = abs(percentage) >= (self.price_change_threshold * 100)
        
        return {
            "current_price": current_price,
            "previous_price": previous_price,
            "change": change,
            "percentage": percentage,
            "alert": alert
        }
    
    def check_large_trades(self) -> List[Dict]:
        """Cek transaksi besar dalam 1 jam terakhir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        one_hour_ago = datetime.now().timestamp() - 3600
        
        cursor.execute('''
            SELECT * FROM trades 
            WHERE timestamp > ? AND amount_decimal >= ?
            ORDER BY amount_decimal DESC
        ''', (datetime.fromtimestamp(one_hour_ago).isoformat(), self.large_trade_threshold))
        
        columns = [description[0] for description in cursor.description]
        large_trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return large_trades
    
    def check_otc_trades(self) -> List[Dict]:
        """Cek transaksi OTC dalam 1 jam terakhir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        one_hour_ago = datetime.now().timestamp() - 3600
        
        cursor.execute('''
            SELECT * FROM trades 
            WHERE timestamp > ? AND is_otc = 1
            ORDER BY timestamp DESC
        ''', (datetime.fromtimestamp(one_hour_ago).isoformat(),))
        
        columns = [description[0] for description in cursor.description]
        otc_trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return otc_trades
    
    def check_volume_spike(self) -> Dict:
        """Cek lonjakan volume trading"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Volume 1 jam terakhir
        one_hour_ago = datetime.now().timestamp() - 3600
        
        cursor.execute('''
            SELECT SUM(amount_decimal) as total_volume, COUNT(*) as trade_count
            FROM trades 
            WHERE timestamp > ?
        ''', (datetime.fromtimestamp(one_hour_ago).isoformat(),))
        
        current_volume = cursor.fetchone()
        
        # Volume 1 jam sebelumnya
        two_hours_ago = datetime.now().timestamp() - 7200
        
        cursor.execute('''
            SELECT SUM(amount_decimal) as total_volume, COUNT(*) as trade_count
            FROM trades 
            WHERE timestamp > ? AND timestamp < ?
        ''', (datetime.fromtimestamp(two_hours_ago).isoformat(), 
              datetime.fromtimestamp(one_hour_ago).isoformat()))
        
        previous_volume = cursor.fetchone()
        
        conn.close()
        
        if not current_volume[0] or not previous_volume[0]:
            return {"spike": False, "current_volume": 0, "previous_volume": 0}
        
        current_vol = current_volume[0] or 0
        previous_vol = previous_volume[0] or 0
        
        if previous_vol == 0:
            return {"spike": current_vol > self.volume_threshold, "current_volume": current_vol, "previous_volume": 0}
        
        volume_increase = (current_vol - previous_vol) / previous_vol
        spike = volume_increase > 2.0  # 200% increase
        
        return {
            "spike": spike,
            "current_volume": current_vol,
            "previous_volume": previous_vol,
            "increase_percentage": volume_increase * 100
        }
    
    def send_email_notification(self, subject: str, body: str, to_email: str = None):
        """Kirim notifikasi email (perlu konfigurasi SMTP)"""
        if not to_email:
            logger.info("No email configured, skipping email notification")
            return
        
        # Implementasi email notification
        # Perlu konfigurasi SMTP server
        logger.info(f"Email notification: {subject}")
        logger.info(f"Body: {body}")
    
    def send_telegram_notification(self, message: str, bot_token: str = None, chat_id: str = None):
        """Kirim notifikasi Telegram (perlu bot token)"""
        if not bot_token or not chat_id:
            logger.info("No Telegram configured, skipping Telegram notification")
            return
        
        # Implementasi Telegram notification
        logger.info(f"Telegram notification: {message}")
    
    def generate_notification_message(self, alert_type: str, data: Dict) -> str:
        """Generate pesan notifikasi"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if alert_type == "price_change":
            direction = "📈 UP" if data["change"] > 0 else "📉 DOWN"
            return f"""
🚨 Keeta Price Alert - {timestamp}
{direction} {abs(data['percentage']):.2f}%

Current Price: {data['current_price']:.8f} MURF/KTA
Previous Price: {data['previous_price']:.8f} MURF/KTA
Change: {data['change']:.8f} MURF/KTA
            """.strip()
        
        elif alert_type == "large_trade":
            trades_text = "\n".join([
                f"  • {trade['amount_decimal']:,} {trade['token_id'][:20]}... at {trade['timestamp']}"
                for trade in data[:3]  # Show top 3
            ])
            return f"""
🐋 Large Trade Alert - {timestamp}
{len(data)} large trades detected:

{trades_text}
            """.strip()
        
        elif alert_type == "volume_spike":
            return f"""
📊 Volume Spike Alert - {timestamp}
Volume increased by {data['increase_percentage']:.1f}%

Current Volume: {data['current_volume']:,}
Previous Volume: {data['previous_volume']:,}
            """.strip()
        
        elif alert_type == "otc_trade":
            trades_text = "\n".join([
                f"  • {trade['amount_decimal']:,} {trade['token_id'][:20]}... "
                f"⇄ {trade.get('counterpart_amount', 0):,} {trade.get('counterpart_token', '')[:20]}... "
                f"(Ratio: {trade.get('exchange_ratio', 0):.8f}) at {trade['timestamp']}"
                for trade in data[:3]  # Show top 3
            ])
            return f"""
🔄 OTC SWAP Alert - {timestamp}
{len(data)} OTC trades detected:

{trades_text}
            """.strip()
        
        return f"Keeta Alert - {timestamp}: {alert_type}"
    
    def check_alerts(self):
        """Cek semua alert dan kirim notifikasi"""
        logger.info("Checking alerts...")
        
        # Cek perubahan harga
        price_data = self.check_price_change()
        if price_data["alert"]:
            message = self.generate_notification_message("price_change", price_data)
            logger.warning(f"PRICE ALERT: {message}")
            # self.send_email_notification("Keeta Price Alert", message)
            # self.send_telegram_notification(message)
        
        # Cek transaksi besar
        large_trades = self.check_large_trades()
        if large_trades:
            message = self.generate_notification_message("large_trade", large_trades)
            logger.warning(f"LARGE TRADE ALERT: {message}")
            # self.send_email_notification("Keeta Large Trade Alert", message)
            # self.send_telegram_notification(message)
        
        # Cek transaksi OTC
        otc_trades = self.check_otc_trades()
        if otc_trades:
            message = self.generate_notification_message("otc_trade", otc_trades)
            logger.warning(f"OTC TRADE ALERT: {message}")
            # self.send_email_notification("Keeta OTC Trade Alert", message)
            # self.send_telegram_notification(message)
        
        # Cek lonjakan volume
        volume_data = self.check_volume_spike()
        if volume_data["spike"]:
            message = self.generate_notification_message("volume_spike", volume_data)
            logger.warning(f"VOLUME ALERT: {message}")
            # self.send_email_notification("Keeta Volume Alert", message)
            # self.send_telegram_notification(message)
        
        logger.info("Alert check completed")

def main():
    """Main function untuk menjalankan notifier"""
    notifier = KeetaNotifier()
    
    print("🔔 Keeta Notification System")
    print("Checking for alerts...")
    print()
    
    notifier.check_alerts()
    
    print("✅ Alert check completed")

if __name__ == "__main__":
    main()
