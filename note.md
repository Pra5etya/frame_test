# config section
dalam pembuatan aplikasi khusus nya pada config environment (dev, stag, prod) ditaruh di dalam folder sendiri bersamaan dengan base-nya

usahakan dalam pembuatan config dalam web urutannya yakni sebagai berikut:

1. logger
2. environment (set dan load env; base -> dev, stag, prod)

3. data
4. backup
5. notifikasi


# crypto section
* untuk secret key sebaiknya membuat script baru untuk generate keynya, misal **generate_key.py** namun hasil enkripsi disimpan pada masing" variabel .env-nya

* dalam melakukan enkripsi .env-nya usahakan per .env, misal (.env.dev.enc, dsb), dan untuk secret keynya disimpan dalam variabel .env-nya

```bash
py encrypt_env.py stag || py encrypt_env.py pro 
```


* note: jangan sampai file permission longgar pada hosting

* .masterkey diterapkan pada **.env.development** dengan otomatsi disimpan pada **/instance**

* penggunaan APP_MASTER_KEY hanya diterapkan pada runtimen (tidak disimpan). Pada production tambahkan secret manager (bisa vendor / bikin sendiri)


# NEXT
* bagaimana pembuatan production key bisa validasi pada setiap halaman di website baik front end atau backend, serta bagaimana jika terdapat kasus halaman tersebut dibiarkan lama apakah akan berpengaruh terhadap validasi kuncinya pada key pool

* Kemanan tambahan
    * Replay attack protection → sertakan timestamp + nonce di payload dan validasi.
    * Audit log → simpan key ID yang digunakan untuk verifikasi.
    * Gunakan TLS → rotasi key tidak berguna kalau koneksi tidak dienkripsi.

1. Caching (misalnya cache hasil query database biar nggak query berulang-ulang).
2. Session store (menyimpan data session login user).
3. Message broker (pub/sub).
4. Rate limiting (membatasi request API).
5. Leaderboard (menggunakan sorted set).



# Developer Activity Bar
* bagaimana cara bundle atau minify di web menggunaan flask
* apa itu Headers dan bagaimana saya bisa memanfaatkan hal tersebut seperti -> Content-Type, Authorization (JWT token, session cookie), dll.


* Penerapana local / session storage menggunakan python tidak bisa karena, Ini murni fitur browser. Server (Python/Flask) tidak bisa langsung nulis ke localStorage/sessionStorage.


# Middleware:
1. Session + Cookie hybrid
    * Session Flask = mirror payload token (server side).
    * Cookie SAMPLE_MK_AUTH = menyimpan token "key|user_id|iat|exp|scope".
    * Kalau salah satunya invalid, sistem auto-refresh token.

2. Multi-user
    * Tiap user (browser) diberi USER_ID (UUID) via cookie USER_ID.
    * Jadi tidak ada bentrok antar user.

3. Expiry & Key rotation
    * Token expired otomatis di-refresh.
    * Kalau active_key (dari key_pool) berubah, middleware juga otomatis rotasi.

4. Anti redirect loop
    * Redirect hanya sekali (pakai query _mk=1 + cookie MK_BOOTSTRAPPED).
    * Kalau setelah bounce masih gagal, diarahkan ke /forbidden.

5. Strict mode (baru ditambahkan)
    * Dekorator @require_scope("admin") bisa dipasang di route.
    * Cek scope user (default "basic").
    * Kalau mismatch → redirect ke /forbidden.

# Session type using flask_session
| `SESSION_TYPE`  | Backend penyimpanan                           | Keterangan                                                                     |
| --------------- | --------------------------------------------- | ------------------------------------------------------------------------------ |
| `"null"`        | Tidak menyimpan apa-apa                       | Cocok untuk testing (dummy).                                                   |
| `"filesystem"`  | Filesystem lokal                              | Default paling mudah, session disimpan di file sementara.                      |
| `"redis"`       | Redis                                         | Disimpan di in-memory database Redis. Sangat cepat dan cocok untuk production. |
| `"memcached"`   | Memcached                                     | Alternatif cache in-memory, mirip Redis.                                       |
| `"mongodb"`     | MongoDB                                       | Disimpan di koleksi MongoDB.                                                   |
| `"sqlalchemy"`  | Database SQL (PostgreSQL, MySQL, SQLite, dll) | Disimpan di tabel via SQLAlchemy.                                              |
| `"gaememcache"` | Google App Engine memcache                    | Khusus jika aplikasi jalan di GAE.                                             |




# server-side sessions + Cookies