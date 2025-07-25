# config section
dalam pembuatan aplikasi khusus nya pada config environment (dev, stag, prod) ditaruh di dalam folder sendiri bersamaan dengan base-nya

usahakan dalam pembuatan config dalam web urutannya yakni sebagai berikut:
1. log
2. data
3. backup
4. base
5. environment yang ingin di terapkan
6. notifikasi

# crypto section
* untuk secret key sebaiknya membuat script baru untuk generate keynya, misal **generate_key.py** namun hasil enkripsi disimpan pada masing" variabel .env-nya
* dalam melakukan enkripsi .env-nya usahakan per .env, misal (.env.dev.enc, dsb), dan untuk secret keynya disimpan dalam variabel .env-nya

```bash
py encrypt_env.py stag || py encrypt_env.py pro 
```

* jika sudah maka tinggal buat file decrypt-nya di direktori config, lalu di implementasikan ke dalamm app utama