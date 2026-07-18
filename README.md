# EURUSD Pullback EA

Expert Advisor (EA) trading otomatis untuk pair **EUR/USD** dengan strategi **Moving Average Pullback**. Project ini berisi dua implementasi strategi yang sama:

1. **Python** (`pullback_ea (1).py`) — dijalankan via library [`MetaTrader5`](https://pypi.org/project/MetaTrader5/), terhubung langsung ke terminal MetaTrader 5 di komputer lokal.
2. **MQL5** (`ea_pullback.html`) — source code Expert Advisor untuk MetaTrader 5 (MQL5), ditampilkan dalam halaman HTML sebagai referensi kode yang bisa disalin ke MetaEditor.

Kedua versi menjalankan logika entry/exit yang identik, hanya berbeda platform eksekusi.

## Strategi

Strategi menggunakan 3 Simple Moving Average (SMA) pada timeframe **M15**:

- **Fast MA** — periode 5
- **Slow MA** — periode 10
- **Trend MA** — periode 200 (filter arah tren)

**Kondisi entry BUY (pullback di uptrend):**
- Harga berada di atas Trend MA (uptrend)
- Fast MA sebelumnya di atas Slow MA, tapi saat ini Fast MA sudah turun di bawah Slow MA (pullback)
- Candle close saat ini lebih tinggi dari close sebelumnya (momentum mulai naik lagi)

**Kondisi entry SELL (pullback di downtrend):**
- Harga berada di bawah Trend MA (downtrend)
- Fast MA sebelumnya di bawah Slow MA, tapi saat ini Fast MA sudah naik di atas Slow MA (pullback)
- Candle close saat ini lebih rendah dari close sebelumnya (momentum mulai turun lagi)

**Manajemen posisi:**
- Stop Loss dan Take Profit ditentukan dalam satuan poin/pip tetap
- Posisi otomatis ditutup jika profit mengapai target USD tertentu, atau rugi mencapai batas maksimum USD tertentu (money-based exit, bukan hanya SL/TP harga)
- Ada cooldown (jeda waktu) setelah entry sebelum EA boleh membuka posisi baru lagi
- Hanya membuka satu posisi pada satu waktu (tidak menambah posisi selama posisi lain masih terbuka)

## Fitur Utama

- Deteksi tren otomatis dengan MA 200 sebagai filter arah
- Entry berbasis pullback (menghindari entry di puncak/dasar pergerakan)
- Exit berbasis profit/rugi dalam USD, terpisah dari SL/TP harga
- Cooldown antar-trade untuk menghindari overtrading
- Tersedia dalam dua platform: Python (MetaTrader5 API) dan MQL5 native EA

## Tech Stack

| Komponen | Detail |
|---|---|
| Platform | MetaTrader 5 |
| Bahasa | Python 3, MQL5 |
| Library Python | `MetaTrader5` |
| Symbol | EURUSD |
| Timeframe | M15 |

## Instalasi & Menjalankan

### Versi Python

**Prasyarat:**
- Terminal MetaTrader 5 sudah terpasang dan login ke akun broker (demo/real)
- Python 3.x

**Langkah:**

```bash
pip install MetaTrader5
python "pullback_ea (1).py"
```

Script akan otomatis konek ke terminal MT5 yang sedang berjalan di komputer yang sama (`mt5.initialize()`), lalu memantau harga EURUSD tiap 1-2 detik dan mengeksekusi order sesuai kondisi strategi.

### Versi MQL5 (Expert Advisor)

1. Buka source code EA dari `ea_pullback.html` (di dalam tag `<pre>`), salin isinya.
2. Buka **MetaEditor** dari MetaTrader 5, buat file `.mq5` baru, tempel kode tersebut.
3. Compile (F7).
4. Attach EA ke chart **EURUSD** dengan timeframe **M15** di MetaTrader 5.
5. Aktifkan **Algo Trading** di toolbar MT5.

## Parameter Konfigurasi

| Parameter | Default | Keterangan |
|---|---|---|
| Lot Size | 0.01 | Ukuran lot per posisi |
| Fast MA | 5 | Periode MA cepat |
| Slow MA | 10 | Periode MA lambat |
| Trend MA | 200 | Periode MA filter tren |
| Stop Loss | 10 pips | Jarak stop loss dari harga entry |
| Take Profit | 25 pips | Jarak take profit dari harga entry |
| Profit Target | $0.50 | Auto-close posisi jika profit mengapai nilai ini |
| Max Loss | $0.30 | Auto-close posisi jika rugi mencapai nilai ini |
| Cooldown | 180 detik | Jeda waktu sebelum boleh entry baru |

Semua parameter di atas bisa diubah langsung di source code (Python: variabel di bagian `SETTINGS`; MQL5: `input` di bagian atas file).

## Disclaimer

Project ini dibuat untuk tujuan edukasi dan eksperimen strategi trading otomatis. Trading forex mengandung risiko kerugian finansial yang signifikan. Selalu uji strategi ini di akun **demo** terlebih dahulu, pahami risikonya, dan gunakan modal yang siap Anda rugikan sebelum menjalankannya di akun real. Penulis tidak bertanggung jawab atas kerugian yang timbul dari penggunaan kode ini.
