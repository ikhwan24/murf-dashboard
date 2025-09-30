# 🚀 Deploy MURF Dashboard ke Public

## Opsi Deploy:

### 1. **Railway (Recommended - Free & Easy)**

#### Langkah-langkah:
1. **Buat akun di [Railway.app](https://railway.app)**
2. **Connect GitHub repository**
3. **Deploy otomatis**

#### File yang sudah disiapkan:
- ✅ `requirements.txt` - Dependencies
- ✅ `Procfile` - Start command
- ✅ `railway.json` - Railway config
- ✅ Dashboard sudah production-ready

---

### 2. **Heroku (Alternative)**

#### Langkah-langkah:
1. **Install Heroku CLI**
2. **Login & Create app:**
   ```bash
   heroku login
   heroku create murf-dashboard
   ```
3. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy dashboard"
   git push heroku main
   ```

---

### 3. **Vercel (Static Alternative)**

#### Untuk static version:
1. **Install Vercel CLI**
2. **Deploy:**
   ```bash
   npm i -g vercel
   vercel --prod
   ```

---

### 4. **DigitalOcean App Platform**

#### Langkah-langkah:
1. **Buat akun DigitalOcean**
2. **Connect GitHub**
3. **Deploy otomatis**

---

## 🔧 **Production Features:**

### ✅ **Environment Variables:**
- `PORT` - Server port (auto-detect)
- `COINGECKO_API_KEY` - Optional untuk rate limiting

### ✅ **Production Ready:**
- Dynamic port binding
- 0.0.0.0 binding untuk external access
- Error handling
- Auto-refresh data

### ✅ **Security:**
- CORS headers
- Input validation
- Error logging

---

## 📊 **Dashboard Features:**

- **Live KTA Price** dari CoinGecko
- **Real-time MURF Data** dari Keeta API
- **Type 7 OTC Transactions** monitoring
- **Price History Chart** dengan Chart.js
- **Donation Section** untuk support
- **Auto-refresh** setiap 30 detik

---

## 🌐 **URL setelah deploy:**
Dashboard akan tersedia di URL yang diberikan platform (Railway/Heroku/etc)

**Contoh:**
- Railway: `https://murf-dashboard-production.up.railway.app`
- Heroku: `https://murf-dashboard.herokuapp.com`
