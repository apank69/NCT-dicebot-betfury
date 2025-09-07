# NCT-dicebot-betfury
Berikut contoh lengkap satu "Dicebot" Python yang bisa dipakai sebagai starting point untuk otomatisasi login + bermain di situs (mis. Betfury). Script ini dibuat fleksibel — banyak selector dikonfigurasi lewat config sehingga Anda bisa menyesuaikannya dengan struktur HTML aktual situs (karena selector situs sering berubah)

 Dicebot (Python) — Template for Betfury automation

Perhatian penting
- Otomatisasi login atau bermain di situs perjudian dapat melanggar Terms of Service situs tersebut dan/atau hukum setempat. Gunakan kode ini hanya untuk tujuan pendidikan, pengujian di lingkungan yang Anda miliki, atau dengan izin eksplisit.
- Saya tidak bertanggung jawab atas akun yang diblokir, kehilangan dana, atau konsekuensi hukum akibat penggunaan script ini.

Apa yang diberikan
- bot.py : script Python utama. Menggunakan Selenium untuk membuka browser, mencoba login (jika credential + selectors tersedia), lalu melakukan loop "roll" menggunakan selector yang Anda tentukan di config.json.
- config.json : template konfigurasi selector CSS/XPath dan parameter lain. Sesuaikan selector dengan struktur HTML Betfury aktual (gunakan DevTools > copy selector).
- .env.example : contoh variabel lingkungan (salin ke .env).
- requirements.txt : dependencies.

Cara pakai (singkat)
1. Salin .env.example ke .env dan isi BETFURY_EMAIL/BETFURY_PASSWORD jika ingin auto login.
2. Sesuaikan selector di config.json:
   - Buka situs, klik kanan elemen (login button, email input, submit, bet amount, roll button, hasil, balance) > Copy > Copy selector atau gunakan XPath. Ganti nilai di config.json.
   - Jika situs menggunakan Web3 / MetaMask untuk login, automatisasi email/password biasanya tidak mungkin — gunakan manual login flow (script akan menunggu Anda login jika login selectors tidak cocok).
3. Pasang dependencies:
   - pip install -r requirements.txt
4. Jalankan:
   - python bot.py
   - Jika HEADLESS=false di .env maka browser akan terlihat dan Anda bisa login manual jika diperlukan.

Tips debugging
- Jika script tidak menemukan elemen: buka browser biasa (HEADLESS=false), gunakan DevTools untuk menemukan selector yang benar dan masukkan ke config.json.
- Untuk web3/metamask flows: lebih rumit — Anda mungkin perlu ekstensi Metamask atau menggunakan akun testnet dev environment.

Kalau mau saya bantu lebih lanjut
- Saya bisa menyesuaikan config.json berdasarkan HTML aktual Betfury jika Anda paste HTML/selector dari DevTools atau beri URL halaman spesifik.
- Saya juga bisa membuat versi yang menyimpan session cookie dan memakai API jika Anda peroleh token dari browser devtools.
