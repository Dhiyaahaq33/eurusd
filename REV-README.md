# SI KECIL PEMBURU PULLBACK
### EURUSD — Expert Advisor Pullback Sederhana untuk MetaTrader 5

## Apa Ini?

Skrip trading otomatis (Expert Advisor / EA) super sederhana untuk pasangan mata uang EUR/USD di MetaTrader 5. Bot ini pakai strategi "pullback" — masuk posisi berdasarkan pergerakan harga pendek dengan lot kecil (0.01), stop loss dan take profit dalam pip, plus ada target profit harian dan batas rugi harian dalam dollar. Ada dua bentuk kode di folder ini: satu versi Python (pakai library `MetaTrader5`) dan satu versi MQL5 native yang ditulis dalam file HTML (sepertinya cuma buat nyimpen/nampilin kode-nya, bukan file MQL5 yang bisa langsung di-compile).

## Fitur Utama

- Entry berbasis moving average sederhana (di versi Python: MA custom; di versi HTML/MQL5: kombinasi FastMA/SlowMA/TrendMA)
- Lot tetap kecil: 0.01
- Stop Loss 10 pip, Take Profit 25 pip (rasio risk-reward sekitar 1:2.5)
- Target profit harian (`PROFIT_TARGET` = $0.50) dan batas rugi maksimal (`MAX_LOSS` = -$0.30) — bot berhenti kalau target/limit ini kena
- Cooldown 180 detik antar-transaksi biar tidak overtrading
- Timeframe M15 (15 menit)

## Teknologi yang Dipakai

- Python 3 + library `MetaTrader5` (`pullback_ea (1).py`) — jalan sebagai script yang terhubung ke terminal MT5 yang sudah login
- MQL5 (kode ditampilkan dalam `ea_pullback.html`, bukan file `.mq5` asli — perlu disalin manual ke MetaEditor kalau mau dipakai sebagai EA native MT5)

## Cara Instalasi

**Untuk versi Python:**
1. Install MetaTrader 5 dari broker forex kamu (download resmi dari situs broker, bukan lewat winget — MT5 tidak tersedia di package manager Windows).
2. Pastikan Python 3.11 terpasang (`python --version`).
3. Install library MetaTrader5 untuk Python:
   ```powershell
   pip install MetaTrader5
   ```
4. Login ke akun trading kamu di aplikasi MT5 terlebih dulu (biarkan terminal MT5 tetap terbuka), baru jalankan skrip Python — library ini butuh terminal MT5 aktif untuk terhubung.

**Untuk versi MQL5 (`ea_pullback.html`):**
1. Buka file `ea_pullback.html` di browser atau text editor untuk copy kodenya.
2. Buka MetaEditor dari dalam aplikasi MT5 (`F4` atau menu Tools → MetaQuotes Language Editor).
3. Buat Expert Advisor baru, paste kode dari HTML tersebut, lalu compile (`F7`).
4. Attach EA hasil compile ke chart EURUSD M15 di MT5.

## Cara Menjalankan

Versi Python:
```powershell
cd "D:\BOT\MONEY\EURUSD"
python "pullback_ea (1).py"
```
(Pastikan terminal MT5 sudah terbuka dan login terlebih dulu.)

Versi MQL5: cukup attach EA yang sudah di-compile ke chart EURUSD di MT5, lalu aktifkan "AutoTrading".

## Catatan Penting

- **Ini bot yang benar-benar mengeksekusi order asli** lewat MetaTrader 5 (`mt5.order_send`) — beda dengan sebagian besar bot lain di folder `MONEY` yang masih simulasi. Pastikan dulu coba di akun **demo** sebelum pakai akun real.
- Tidak ada file kredensial (`.env`) di folder ini — login MT5 dilakukan lewat aplikasi MT5 itu sendiri, bukan disimpan di kode. Tetap hati-hati jangan hardcode nomor akun/password MT5 kalau nanti menambahkan fitur auto-login.
- Target profit ($0.50) dan batas rugi (-$0.30) sangat kecil — sepertinya file ini dipakai untuk testing/eksperimen dengan lot sangat kecil (0.01), bukan setup produksi serius. Sesuaikan angka ini kalau mau dipakai lebih serius.
- Nama file `pullback_ea (1).py` mengandung " (1)" yang biasanya nunjukin ini adalah hasil download duplikat — cek apakah ada versi lain yang lebih baru sebelum dipakai.

## Riwayat Perbaikan (2026-07-22)

Bot ini beresiko crash/silent-fail karena tidak ada pengecekan hasil koneksi/order sama sekali:

1. **`mt5.initialize()` tidak pernah dicek return value-nya** — kalau MT5 belum login/terhubung, semua panggilan berikutnya (`symbol_info_tick`, `copy_rates_from_pos`) akan return `None`, dan script langsung crash `AttributeError` di iterasi loop berikutnya tanpa pesan error yang jelas.
   **Fix:** ditambahkan pengecekan `if not mt5.initialize(): print(error); sys.exit(1)`.
2. **`order_send()` tidak pernah dicek `retcode`-nya**, baik untuk buka posisi (`open_trade`) maupun tutup posisi (`close_position`). Kalau broker menolak order (harga berubah, saldo kurang, market ditutup), bot tetap menganggap order berhasil dan lanjut seolah-olah posisi sudah terbuka/tertutup — bisa bikin bot "buta" terhadap posisi nyata di akun.
   **Fix:** kedua fungsi sekarang mengecek `result.retcode == mt5.TRADE_RETCODE_DONE`, print error yang jelas kalau gagal, dan return `False` supaya loop utama bisa retry di iterasi berikutnya alih-alih menganggap sukses.
3. **Repaint risk pada sinyal entry** — perhitungan MA cepat/lambat dan `close`/`prev_close` sebelumnya pakai `shift=0`, yaitu candle yang **belum selesai terbentuk**. Ini artinya sinyal bisa berubah-ubah di tengah candle berjalan (repaint), tidak reliable untuk live trading.
   **Fix:** semua perhitungan sinyal (fast/slow MA, trend MA200, close/prev_close) digeser ke `shift=1`/`shift=2` — candle yang sudah closed — supaya sinyal stabil begitu terbentuk dan tidak berubah lagi.

**Catatan:** tidak bisa dites end-to-end karena butuh terminal MT5 yang login aktif (tidak tersedia di lingkungan ini). Sudah lolos `py_compile` (cek syntax), tapi **wajib dites dulu di akun DEMO** sebelum dipakai live, terutama untuk memverifikasi behavior order-rejection handling yang baru.

## Kebutuhan API LLM

- **Butuh API LLM?** Tidak — Expert Advisor MT5 rule-based untuk forex, logic teknikal murni.
- **Bisa pakai API Claude (Anthropic)?** Tidak relevan — proyek ini tidak memproses bahasa alami / tidak butuh LLM sama sekali.

## Instalasi & Eksekusi Offline

- **Bisa instalasi offline?** Tidak untuk instalasi pertama — download installer MetaTrader 5 dari broker dan `pip install MetaTrader5` sama-sama butuh internet. Setelah pernah terinstall/ter-cache, instalasi ulang di komputer yang sama bisa lebih cepat dari cache pip, tapi MT5 sendiri tetap perlu didownload dari server broker kalau install ulang dari nol.
- **Bisa dijalankan offline (setelah terinstall)?** Tidak — EA ini mengeksekusi order trading beneran lewat terminal MT5 yang butuh koneksi live ke server broker untuk data harga dan eksekusi order. Tanpa internet/koneksi ke server broker, MT5 tidak bisa connect dan script Python (`mt5.initialize()`) akan gagal terhubung.
