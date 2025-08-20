from app import create_app
import subprocess, time

"""
pip install redis ➝ hanya menginstall Python client library (modul redis), bukan servernya.
redis-server.exe ➝ adalah Redis server (proses yang benar-benar nyimpen data di RAM, di port 6379).

Redis tidak punya versi resmi untuk Windows,

# Update repositori
sudo apt update && sudo apt upgrade -y

# Install Redis server
sudo apt install redis-server -y

👉 Git Bash tidak punya sudo ataupun apt karena itu package manager khusus Linux (Debian/Ubuntu).
"""

def start_redis():
    try:
        # cek apakah redis-cli bisa ping
        import redis

        r = redis.Redis(host="localhost", port=6379)
        r.ping()

        print("✅ Redis sudah jalan")

    except:
        print("🚀 Menjalankan Redis server...")
        
        subprocess.Popen(["redis-server"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # tunggu x detik biar siap

if __name__ == "__main__":
    start_redis()
    app = create_app()
    app.run(debug = True, host='localhost', port=6379)