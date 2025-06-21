import requests
import json
import time
import random
import urllib.parse
from datetime import datetime, timedelta
from colorama import init, Fore, Style
import threading
import sys
import os

# Initialize colorama
init(autoreset=True)

# Global headers template
HEADERS_TEMPLATE = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Host': 'bot.ibvm.io:3000',
    'Origin': 'https://bot.ibvm.io',
    'Referer': 'https://bot.ibvm.io/',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
}

def get_headers(content_type=None):
    """Copy headers template untuk setiap fungsi"""
    headers = HEADERS_TEMPLATE.copy()
    if content_type:
        headers['Content-Type'] = content_type
    return headers

def print_welcome_message():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
          """)
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop $IBVM")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop")
    print(Fore.CYAN + "=" * 60)

def load_accounts():
    """Memuat akun dari data.txt"""
    try:
        with open('data.txt', 'r') as file:
            accounts = [line.strip() for line in file if line.strip()]
        print(Fore.GREEN + f"✅ Berhasil memuat {len(accounts)} akun dari data.txt")
        return accounts
    except FileNotFoundError:
        print(Fore.RED + "❌ File data.txt tidak ditemukan!")
        return []

def load_proxies(filename='proxy.txt'):
    """Load proxies dari file"""
    try:
        with open(filename, 'r') as file:
            proxies = []
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(":")
                    if len(parts) == 4:
                        ip, port, user, password = parts
                        proxy_url = f"http://{user}:{password}@{ip}:{port}"
                    elif len(parts) == 2:
                        ip, port = parts
                        proxy_url = f"http://{ip}:{port}"
                    else:
                        continue
                    proxies.append(proxy_url)
        
        if proxies:
            print(Fore.BLUE + f"🔗 Berhasil memuat {len(proxies)} proxy")
        return proxies
    except FileNotFoundError:
        print(Fore.YELLOW + f"⚠️ File {filename} tidak ditemukan. Melanjutkan tanpa proxy")
        return []

def get_proxy(proxies):
    """Mengambil proxy secara random"""
    if not proxies:
        return None
    proxy_url = random.choice(proxies)
    return {"http": proxy_url, "https": proxy_url}

def parse_query_data(query_string):
    """Parse query string untuk mendapatkan data user"""
    try:
        parsed_data = urllib.parse.parse_qs(query_string)
        user_data = json.loads(parsed_data['user'][0])
        return {
            'id': user_data['id'],
            'first_name': user_data['first_name'],
            'username': user_data.get('username', ''),
            'query_id': parsed_data['query_id'][0]
        }
    except Exception as e:
        print(Fore.RED + f"❌ Error parsing query data: {str(e)}")
        return None

def make_request(method, url, headers, data=None, proxies=None, timeout=30):
    """Fungsi untuk melakukan request dengan error handling"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        else:
            response = requests.post(url, headers=headers, json=data, proxies=proxies, timeout=timeout)
        
        return response
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"❌ Request error: {str(e)}")
        return None

def user_login(user_data, proxies=None):
    """Login user dan mendapatkan data profil"""
    url = "https://bot.ibvm.io:3000/user"
    headers = get_headers('application/json')
    
    payload = {
        "id": user_data['id'],
        "first_name": user_data['first_name']
    }
    
    proxy = get_proxy(proxies) if proxies else None
    response = make_request('POST', url, headers, payload, proxy)
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('status'):
            user_info = data['data']
            print(Fore.GREEN + f"✅ Login berhasil: {user_data['first_name']} (@{user_data.get('username', 'N/A')})")
            print(Fore.CYAN + f"   💰 Coins: {user_info.get('coins', 0)} | " +
                  f"Unclaimed: {user_info.get('unclaimed', 0)} | " +
                  f"Total Tasks: {user_info.get('totalTasks', 0)}")
            return user_info
        else:
            print(Fore.RED + f"❌ Login gagal untuk {user_data['first_name']}")
    else:
        print(Fore.RED + f"❌ Tidak dapat terhubung ke server untuk {user_data['first_name']}")
    
    return None

def get_daily_rewards(user_id, proxies=None):
    """Mendapatkan informasi daily rewards"""
    url = f"https://bot.ibvm.io:3000/dailyrewards/{user_id}"
    headers = get_headers()
    
    proxy = get_proxy(proxies) if proxies else None
    response = make_request('GET', url, headers, proxies=proxy)
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('status'):
            rewards = data['data']
            
            
            current_day = None
            for reward in rewards:
                if reward.get('current') == True and reward.get('clamied') == False:
                    current_day = reward
                    break
            
            if current_day:
                print(Fore.YELLOW + f"🎁 Daily reward tersedia: Hari {current_day['day']} - {current_day['points']} poin")
                return current_day
            else:
                # Cek status semua rewards untuk info
                claimed_days = [r['day'] for r in rewards if r.get('clamied') == True]
                current_days = [r['day'] for r in rewards if r.get('current') == True]
                
                if claimed_days:
                    print(Fore.BLUE + f"ℹ️ Daily reward sudah diklaim untuk hari: {', '.join(map(str, claimed_days))}")
                if current_days and not current_day:
                    print(Fore.BLUE + f"ℹ️ Daily reward hari {current_days[0]} sudah diklaim")
                else:
                    print(Fore.BLUE + f"ℹ️ Tidak ada daily reward yang tersedia saat ini")
    else:
        print(Fore.RED + f"❌ Gagal mendapatkan daily rewards")
    
    return None

def claim_daily_reward(user_id, proxies=None):
    """Klaim daily reward"""
    url = f"https://bot.ibvm.io:3000/dailyrewards/claim/{user_id}"
    headers = get_headers()
    
    proxy = get_proxy(proxies) if proxies else None
    response = make_request('GET', url, headers, proxies=proxy)
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('status'):
            print(Fore.GREEN + f"✅ {data.get('message', 'Daily reward berhasil diklaim!')}")
            return True
        else:
            print(Fore.RED + f"❌ Gagal klaim daily reward")
    else:
        print(Fore.RED + f"❌ Tidak dapat mengklaim daily reward")
    
    return False

def get_daily_tasks(user_id, proxies=None):
    """Mendapatkan daftar daily tasks"""
    url = f"https://bot.ibvm.io:3000/dailytask/{user_id}"
    headers = get_headers()
    
    proxy = get_proxy(proxies) if proxies else None
    response = make_request('GET', url, headers, proxies=proxy)
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('status'):
            return data['data']
        else:
            print(Fore.RED + f"❌ Gagal mendapatkan daily tasks")
    else:
        print(Fore.RED + f"❌ Tidak dapat terhubung untuk mendapatkan tasks")
    
    return []

def complete_task(user_id, task_id, day, proxies=None):
    """Menyelesaikan task"""
    url = "https://bot.ibvm.io:3000/dailytask/complete"
    headers = get_headers('application/json')
    
    payload = {
        "id": user_id,
        "taskId": task_id,
        "day": day
    }
    
    proxy = get_proxy(proxies) if proxies else None
    response = make_request('POST', url, headers, payload, proxy)
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('status'):
            print(Fore.GREEN + f"✅ {data.get('message', 'Task berhasil diselesaikan!')}")
            return True
        else:
            print(Fore.RED + f"❌ Gagal menyelesaikan task")
    else:
        print(Fore.RED + f"❌ Tidak dapat menyelesaikan task")
    
    return False

def process_account(account_data, account_num, total_accounts, proxies=None):
    """Memproses satu akun"""
    print(Fore.CYAN + f"\n{'='*60}")
    print(Fore.WHITE + Style.BRIGHT + f"🔄 Memproses Akun {account_num}/{total_accounts}")
    print(Fore.CYAN + f"{'='*60}")
    
    # Parse query data
    user_data = parse_query_data(account_data)
    if not user_data:
        print(Fore.RED + f"❌ Gagal parsing data akun {account_num}")
        return
    
    try:
        # Login user
        user_info = user_login(user_data, proxies)
        if not user_info:
            return
        
        user_id = user_info['id']
        
        # Cek daily rewards
        print(Fore.YELLOW + f"\n🎁 Mengecek daily rewards...")
        current_reward = get_daily_rewards(user_id, proxies)
        if current_reward:
            time.sleep(2)
            claim_daily_reward(user_id, proxies)
        
        # Cek daily tasks
        print(Fore.YELLOW + f"\n📋 Mengecek daily tasks...")
        tasks_data = get_daily_tasks(user_id, proxies)
        
        if tasks_data:
            total_tasks_available = 0
            total_tasks_completed = 0
            
            for day_task in tasks_data:
                day = day_task.get('day', 0)
                title = day_task.get('title', 'Unknown')
                tasks = day_task.get('tasks', [])
                
                print(Fore.BLUE + f"\n📅 {title} (Hari {day}):")
                
                available_tasks = []
                completed_tasks = []
                
                for task in tasks:
                    task_name = task.get('name', 'Unknown Task')
                    points = task.get('points', 0)
                    is_completed = task.get('isCompleted', False)
                    task_id = task.get('_id', '')
                    
                    if is_completed:
                        completed_tasks.append({'name': task_name, 'points': points})
                        total_tasks_completed += 1
                    elif task_id:  # Task belum selesai dan punya ID
                        available_tasks.append({
                            'name': task_name, 
                            'points': points, 
                            'id': task_id
                        })
                        total_tasks_available += 1
                
                # Tampilkan status tasks
                if completed_tasks:
                    print(Fore.GREEN + f"   ✅ Tasks yang sudah selesai:")
                    for task in completed_tasks:
                        print(Fore.GREEN + f"      • {task['name']} ({task['points']} poin)")
                
                if available_tasks:
                    print(Fore.YELLOW + f"   ⏳ Tasks yang tersedia:")
                    for task in available_tasks:
                        print(Fore.YELLOW + f"      • {task['name']} ({task['points']} poin)")
                        time.sleep(2)  # Jeda sebelum complete task
                        
                        success = complete_task(user_id, task['id'], day, proxies)
                        if success:
                            total_tasks_completed += 1
                            total_tasks_available -= 1
                        
                        time.sleep(1)  # Jeda antar task
                
                if not available_tasks and not completed_tasks:
                    print(Fore.BLUE + f"   ℹ️ Tidak ada tasks untuk hari ini")
            
            # Summary tasks
            print(Fore.CYAN + f"\n📊 Ringkasan Tasks:")
            print(Fore.GREEN + f"   ✅ Tasks selesai: {total_tasks_completed}")
            if total_tasks_available > 0:
                print(Fore.YELLOW + f"   ⏳ Tasks tersisa: {total_tasks_available}")
            else:
                print(Fore.GREEN + f"   🎉 Semua tasks telah diselesaikan!")
        else:
            print(Fore.BLUE + f"   ℹ️ Tidak ada daily tasks yang tersedia")
        
        print(Fore.GREEN + f"✅ Selesai memproses akun {user_data['first_name']}")
        
    except Exception as e:
        print(Fore.RED + f"❌ Error saat memproses akun {account_num}: {str(e)}")

def countdown_timer(seconds):
    """Hitung mundur dengan tampilan yang bergerak"""
    end_time = datetime.now() + timedelta(seconds=seconds)
    
    while datetime.now() < end_time:
        remaining_time = end_time - datetime.now()
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Clear line and print countdown
        sys.stdout.write(f"\r{Fore.YELLOW}⏰ Menunggu: {remaining_time.days} hari, {hours:02d}:{minutes:02d}:{seconds:02d} ")
        sys.stdout.flush()
        time.sleep(1)
    
    print(f"\n{Fore.GREEN}✅ Waktu tunggu selesai!")

def main():
    """Fungsi utama"""
    print_welcome_message()
    
    # Load accounts dan proxies
    accounts = load_accounts()
    if not accounts:
        print(Fore.RED + "❌ Tidak ada akun untuk diproses!")
        return
    
    proxies = load_proxies()
    
    while True:
        try:
            print(Fore.WHITE + Style.BRIGHT + f"\n🚀 Memulai proses untuk {len(accounts)} akun")
            print(Fore.CYAN + f"⏰ Waktu mulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Proses setiap akun
            for i, account in enumerate(accounts, 1):
                process_account(account, i, len(accounts), proxies)
                
                # Jeda antar akun kecuali akun terakhir
                if i < len(accounts):
                    print(Fore.BLUE + f"\n⏳ Menunggu 5 detik sebelum akun berikutnya...")
                    time.sleep(5)
            
            print(Fore.GREEN + Style.BRIGHT + f"\n🎉 Semua akun telah diproses!")
            print(Fore.YELLOW + f"⏰ Selesai pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Hitung mundur 1 hari (24 jam)
            print(Fore.CYAN + f"\n⏰ Menunggu 1 hari untuk siklus berikutnya...")
            countdown_timer(24 * 60 * 60)  # 24 jam dalam detik
            
        except KeyboardInterrupt:
            print(Fore.RED + f"\n❌ Program dihentikan pengguna!")
            break
        except Exception as e:
            print(Fore.RED + f"\n❌ Error dalam main loop: {str(e)}")
            print(Fore.YELLOW + f"⏳ Menunggu 60 detik sebelum mencoba lagi...")
            time.sleep(60)

if __name__ == "__main__":
    main()
