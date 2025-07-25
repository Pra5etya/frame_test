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
* penerapan enkripsi environemnt dijalankan ketika ada perubahana di dalam setiap .env.* dimana terdapat modifikasi jika pada terminal:
```bash
py encrypt_env.py stag || py encrypt_env.py pro 
```
maka akan membuat enrkipsi di dalam variabel .env setiap masing" environmentnya dengan default untuk menajalankan script di atas tanpa stag atau pro dia akan menjalankan environemnt untuk development