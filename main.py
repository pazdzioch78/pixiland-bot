from datetime import datetime
import time
from colorama import Fore
import requests
import random
from fake_useragent import UserAgent
import asyncio
import json
import gzip
import brotli
import zlib
import chardet
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class pixiland:
    BASE_URL = "https://play.pixiland.app/api/v1/"
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://play.pixiland.app",
        "priority": "u=1, i",
        "referer": "https://play.pixiland.app/",
        "sec-ch-ua": '"Microsoft Edge";v="134", "Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge WebView2";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
    }

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.config = self.load_config()
        self.session = self.sessions()
        self._original_requests = {
            "get": requests.get,
            "post": requests.post,
            "put": requests.put,
            "delete": requests.delete,
        }
        self.proxy_session = None

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Pixiland Free Bot", Fore.CYAN)
        self.log("🚀 Created by LIVEXORDS", Fore.CYAN)
        self.log("📢 Channel: t.me/livexordsscript\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
        safe_message = message.encode("utf-8", "backslashreplace").decode("utf-8")
        print(
            Fore.LIGHTBLACK_EX
            + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |")
            + " "
            + color
            + safe_message
            + Fore.RESET
        )
    
    def sessions(self):
        session = requests.Session()
        retries = Retry(total=3,
                        backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504, 520])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session
    
    def decode_response(self, response):
        """
        Mendekode response dari server secara umum.

        Parameter:
            response: objek requests.Response

        Mengembalikan:
            - Jika Content-Type mengandung 'application/json', maka mengembalikan objek Python (dict atau list) hasil parsing JSON.
            - Jika bukan JSON, maka mengembalikan string hasil decode.
        """
        # Ambil header
        content_encoding = response.headers.get('Content-Encoding', '').lower()
        content_type = response.headers.get('Content-Type', '').lower()

        # Tentukan charset dari Content-Type, default ke utf-8
        charset = 'utf-8'
        if 'charset=' in content_type:
            charset = content_type.split('charset=')[-1].split(';')[0].strip()

        # Ambil data mentah
        data = response.content

        # Dekompresi jika perlu
        try:
            if content_encoding == 'gzip':
                data = gzip.decompress(data)
            elif content_encoding in ['br', 'brotli']:
                data = brotli.decompress(data)
            elif content_encoding in ['deflate', 'zlib']:
                data = zlib.decompress(data)
        except Exception:
            # Jika dekompresi gagal, lanjutkan dengan data asli
            pass

        # Coba decode menggunakan charset yang didapat
        try:
            text = data.decode(charset)
        except Exception:
            # Fallback: deteksi encoding dengan chardet
            detection = chardet.detect(data)
            detected_encoding = detection.get("encoding", "utf-8")
            text = data.decode(detected_encoding, errors='replace')

        # Jika konten berupa JSON, kembalikan hasil parsing JSON
        if 'application/json' in content_type:
            try:
                return json.loads(text)
            except Exception:
                # Jika parsing JSON gagal, kembalikan string hasil decode
                return text
        else:
            return text

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log(
                "❌ Failed to parse config.json. Please check the file format.",
                Fore.RED,
            )
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def login(self, index: int) -> None:
        self.log("🔒 Attempting to log in...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        # Get token from query_list and log it (truncated for security)
        token = self.query_list[index]
        self.log(f"📋 Using token: {token[:10]}... (truncated)", Fore.CYAN)

        # Build the login URL and headers
        login_url = f"{self.BASE_URL}auth/signin/tma"
        headers = {**self.HEADERS, "Authorization": f"TMA {token}"}

        # Define the payload as specified
        payload = {"platform": "tdesktop", "token": token, "version": "8.0"}

        try:
            self.log("📡 Sending login request...", Fore.CYAN)
            login_response = requests.post(login_url, headers=headers, json=payload)
            login_response.raise_for_status()
            login_data = login_response.json()

            # Check if login was successful based on the "status" field
            if login_data.get("status") == 200:
                self.token = f"TMA {token}"
                self.log("✅ Login successful!", Fore.GREEN)

                # Display only the important account information
                data = login_data.get("data", {})
                self.log(f"👤 User ID: {data.get('id', 'N/A')}", Fore.CYAN)
                self.log(f"🆔 TID: {data.get('tid', 'N/A')}", Fore.CYAN)
                self.log(f"📛 Username: {data.get('username', 'N/A')}", Fore.CYAN)
                self.log(f"👋 First Name: {data.get('first_name', 'N/A')}", Fore.CYAN)
                self.log(f"👥 Last Name: {data.get('last_name', 'N/A')}", Fore.CYAN)
                self.log(
                    f"🍽️ Last Feeding Time: {data.get('last_time_feeding', 'N/A')}",
                    Fore.CYAN,
                )
                self.log(
                    f"🏆 Last Treasure Claim: {data.get('last_time_claim_treasure', 'N/A')}",
                    Fore.CYAN,
                )
                self.log(
                    f"💌 Referral Code: {data.get('referral_code', 'N/A')}", Fore.CYAN
                )
            else:
                message = login_data.get("message", "Unknown error")
                self.log(f"❌ Login failed: {message}", Fore.RED)
                self.log(f"📄 Response content: {login_response.text}", Fore.RED)
                return

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
            if "login_response" in locals():
                self.log(f"📄 Response content: {login_response.text}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error (JSON decode issue): {e}", Fore.RED)
            if "login_response" in locals():
                self.log(f"📄 Response content: {login_response.text}", Fore.RED)
        except KeyError as e:
            self.log(f"❌ Key error: {e}", Fore.RED)
            if "login_response" in locals():
                self.log(f"📄 Response content: {login_response.text}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)
            if "login_response" in locals():
                self.log(f"📄 Response content: {login_response.text}", Fore.RED)

    def task(self) -> None:
        self.log("📝 Fetching tasks for kinds 0 to 6...", Fore.GREEN)
        all_tasks = []

        # Fase 1: Ambil semua tugas dari kinds 0 hingga 5
        for kind in range(0, 6):
            url = f"{self.BASE_URL}quests?kind={kind}"
            headers = {**self.HEADERS, "Authorization": self.token}
            self.log(f"📡 Requesting tasks for kind {kind}...", Fore.CYAN)
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data.get("status") == 200:
                    tasks = data.get("data", [])
                    self.log(f"📋 Found {len(tasks)} tasks for kind {kind}.", Fore.CYAN)
                    for task_item in tasks:
                        title = task_item.get("title", "No Title")
                        task_id = task_item.get("id", "N/A")
                        self.log(f"🔸 Task: {title} (ID: {task_id})", Fore.CYAN)
                    all_tasks.extend(tasks)
                else:
                    message = data.get("message", "Unknown error")
                    self.log(f"❌ Failed to fetch tasks for kind {kind}: {message}", Fore.RED)
            except requests.exceptions.Timeout as e:
                self.log(f"❌ Timeout error for tasks of kind {kind}: {e}", Fore.RED)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Request error for tasks of kind {kind}: {e}", Fore.RED)
            time.sleep(2)

        if not all_tasks:
            self.log("ℹ️ No tasks found.", Fore.YELLOW)
            return

        # Fase 2: Mulai tugas yang belum selesai (done == False)
        started_tasks = []
        for task_item in all_tasks:
            # Jika tugas sudah selesai, tidak perlu dimulai
            if task_item.get("done", False):
                continue

            quest_id = task_item.get("id")
            task_title = task_item.get("title", "No Title")
            self.log(f"🚀 Starting task: {task_title} (ID: {quest_id})", Fore.CYAN)

            complete_url = f"{self.BASE_URL}quests/complete"
            complete_payload = {"quest_id": quest_id}
            self.log("📡 Sending request to start the task...", Fore.CYAN)
            try:
                complete_response = requests.post(
                    complete_url,
                    headers={**self.HEADERS, "Authorization": self.token},
                    json=complete_payload,
                    timeout=10
                )
                if complete_response.status_code == 200:
                    complete_data = complete_response.json()
                    if complete_data.get("status") == 200:
                        self.log("✅ Task started successfully!", Fore.GREEN)
                        started_tasks.append(task_item)
                    else:
                        message = complete_data.get("message", "Unknown error")
                        self.log(f"❌ Failed to start task: {message}", Fore.RED)
                else:
                    self.log(
                        f"❌ Failed to start task: HTTP {complete_response.status_code}",
                        Fore.RED,
                    )
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Request error in complete task: {e}", Fore.RED)
            time.sleep(2)

        # Fase 3: Klaim reward untuk tugas yang belum diklaim
        # Tugas yang akan diklaim adalah:
        # - Tugas yang sudah selesai (done == True) dan belum diklaim (claimed == False)
        # - Tugas yang berhasil dimulai (dari fase 2) dan belum diklaim
        claimable_tasks = {}
        for task in all_tasks:
            if task.get("done", False) and not task.get("claimed", False):
                claimable_tasks[task.get("id")] = task

        for task in started_tasks:
            # Pastikan tidak terjadi duplikasi
            if not task.get("claimed", False):
                claimable_tasks[task.get("id")] = task

        if not claimable_tasks:
            self.log("ℹ️ No claimable tasks found.", Fore.YELLOW)
            return

        for quest_id, task_item in claimable_tasks.items():
            task_title = task_item.get("title", "No Title")
            self.log(f"📡 Claiming reward for task: {task_title} (ID: {quest_id})", Fore.CYAN)
            claim_url = f"{self.BASE_URL}quests/rewards/claim"
            claim_payload = {"quest_id": quest_id}
            try:
                claim_response = requests.post(
                    claim_url,
                    headers={**self.HEADERS, "Authorization": self.token},
                    json=claim_payload,
                    timeout=10
                )
                if claim_response.status_code == 200:
                    claim_data = claim_response.json()
                    if claim_data.get("status") == 200:
                        self.log("🎉 Reward claimed successfully!", Fore.GREEN)
                    else:
                        message = claim_data.get("message", "Unknown error")
                        self.log(f"❌ Failed to claim reward: {message}", Fore.RED)
                else:
                    self.log(
                        f"❌ Failed to claim reward: HTTP {claim_response.status_code}",
                        Fore.RED,
                    )
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Request error in claim reward: {e}", Fore.RED)
            time.sleep(2)

    def farming(self) -> None:
        self.log("🌱 Starting farming process...", Fore.GREEN)

        # Request user state to get current building information
        state_url = f"{self.BASE_URL}user/state"
        headers = {**self.HEADERS, "Authorization": self.token}

        try:
            self.log("📡 Fetching user state...", Fore.CYAN)
            state_response = requests.get(state_url, headers=headers)
            state_response.raise_for_status()
            state_data = self.decode_response(state_response)

            if state_data.get("status") == 200:
                user_data = state_data.get("data", {})
                buildings = user_data.get("buildings", [])
                if not buildings:
                    self.log("ℹ️ No buildings found for farming.", Fore.YELLOW)
                    return

                self.log(f"🏢 Found {len(buildings)} building(s) for farming.", Fore.CYAN)
                for building in buildings:
                    building_id = building.get("id")
                    if not building_id:
                        self.log("❌ Found a building with no ID, skipping...", Fore.RED)
                        continue

                    self.log(f"🏠 Claiming reward for building {building_id}...", Fore.CYAN)
                    claim_url = f"{self.BASE_URL}building/claim"
                    payload = {"id": building_id}

                    claim_response = requests.put(claim_url, headers=headers, json=payload)
                    claim_response.raise_for_status()
                    claim_data = self.decode_response(claim_response)

                    if claim_data.get("status") == 200:
                        self.log(f"✅ Reward claimed for building {building_id}!", Fore.GREEN)
                    else:
                        message = claim_data.get("message", "Unknown error")
                        self.log(f"❌ Failed to claim reward for building {building_id}: {message}", Fore.RED)
            else:
                message = state_data.get("message", "Unknown error")
                self.log(f"❌ Failed to fetch user state: {message}", Fore.RED)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request error: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ JSON decode error: {e}", Fore.RED)
        except KeyError as e:
            self.log(f"❌ Key error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)
            
    def dungeon(self) -> None:
        self.log("🗺️ Starting dungeon process...", Fore.GREEN)
        headers = {**self.HEADERS, "Authorization": self.token}
        
        # Fetch current dungeon list (once)
        dungeon_url = f"{self.BASE_URL}pve/dungeon"
        try:
            self.log("📡 Fetching dungeon list...", Fore.CYAN)
            response = requests.get(dungeon_url, headers=headers)
            response.raise_for_status()
            dungeon_data = response.json()
            if dungeon_data.get("status") != 200:
                message = dungeon_data.get("message", "Unknown error")
                self.log(f"❌ Failed to fetch dungeons: {message}", Fore.RED)
                return
            dungeons = dungeon_data.get("data", [])
            self.log(f"📋 Found {len(dungeons)} dungeons.", Fore.CYAN)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request error while fetching dungeons: {e}", Fore.RED)
            return
        except ValueError as e:
            self.log(f"❌ JSON decode error while fetching dungeons: {e}", Fore.RED)
            return

        # Process claimable dungeons first:
        # Those that already have a hero assigned and are not yet claimed.
        claimable_dungeons = [
            d for d in dungeons 
            if (d.get("hero_id") or d.get("hero")) and not d.get("claimed", False)
        ]
        for d in claimable_dungeons:
            dungeon_id = d.get("id")
            boss_name = d.get("boss_name", "Unknown Boss")
            self.log(f"💰 Claiming reward for dungeon '{boss_name}' (ID: {dungeon_id})", Fore.CYAN)
            claim_url = f"{self.BASE_URL}pve/dungeon/{dungeon_id}/claim"
            try:
                claim_response = requests.put(claim_url, headers=headers, json={})
                if claim_response.status_code == 200:
                    try:
                        claim_data = claim_response.json()
                    except ValueError as e:
                        self.log(f"❌ JSON decode error in dungeon claim: {e}", Fore.RED)
                        claim_data = {"status": 200}  # Assume success if HTTP 200.
                    if claim_data.get("status") == 200:
                        self.log(f"🏆 Reward claimed for dungeon '{boss_name}'!", Fore.GREEN)
                    else:
                        message = claim_data.get("message", "Unknown error")
                        self.log(f"❌ Failed to claim reward for dungeon '{boss_name}': {message}", Fore.RED)
                else:
                    self.log(f"❌ Failed to claim reward for dungeon '{boss_name}': HTTP {claim_response.status_code}", Fore.RED)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Request error while claiming reward for dungeon '{boss_name}': {e}", Fore.RED)
            time.sleep(2)
        
        # Process exploration dungeons:
        # Dungeons with state == 0 and no hero assigned.
        exploration_dungeons = [
            d for d in dungeons 
            if d.get("state") == 0 and not (d.get("hero_id") or d.get("hero"))
        ]
        for d in exploration_dungeons:
            dungeon_id = d.get("id")
            boss_name = d.get("boss_name", "Unknown Boss")
            self.log(f"⚔️ Processing dungeon '{boss_name}' (ID: {dungeon_id}) for exploration", Fore.CYAN)
            
            # Fetch active heroes for this dungeon
            hero_url = f"{self.BASE_URL}pve/dungeon/{dungeon_id}/hero"
            try:
                self.log(f"📡 Fetching active heroes for dungeon {dungeon_id}...", Fore.CYAN)
                hero_response = requests.get(hero_url, headers=headers)
                hero_response.raise_for_status()
                hero_data = hero_response.json()
                if hero_data.get("status") != 200:
                    message = hero_data.get("message", "Unknown error")
                    self.log(f"❌ Failed to fetch heroes for dungeon {dungeon_id}: {message}", Fore.RED)
                    continue
                active_heroes = hero_data.get("data", [])
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Error fetching heroes for dungeon {dungeon_id}: {e}", Fore.RED)
                continue
            except ValueError as e:
                self.log(f"❌ JSON decode error while fetching heroes for dungeon {dungeon_id}: {e}", Fore.RED)
                continue

            if not active_heroes:
                self.log(f"ℹ️ No active heroes available for dungeon {dungeon_id}. Skipping exploration.", Fore.YELLOW)
                continue

            # Choose the first active hero
            chosen_hero = active_heroes[0]
            hero_id = chosen_hero.get("id")
            hero_name = chosen_hero.get("name", "Unknown Hero")
            self.log(f"👾 Found active hero: {hero_name} (ID: {hero_id}) for dungeon {dungeon_id}.", Fore.CYAN)
            
            # Start exploration using the chosen hero
            explore_url = f"{self.BASE_URL}pve/dungeon/{dungeon_id}/explore"
            payload = {"hero_id": hero_id}
            self.log(f"🚀 Starting exploration for dungeon '{boss_name}' with hero {hero_name}...", Fore.CYAN)
            try:
                explore_response = requests.put(explore_url, headers=headers, json=payload)
                if explore_response.status_code == 200:
                    try:
                        explore_data = explore_response.json()
                    except ValueError as e:
                        self.log(f"❌ JSON decode error in dungeon explore: {e}", Fore.RED)
                        explore_data = {"status": 200}  # Assume success if HTTP 200.
                    if explore_data.get("status") == 200:
                        self.log(f"🏆 Dungeon '{boss_name}' exploration started successfully!", Fore.GREEN)
                    else:
                        message = explore_data.get("message", "Unknown error")
                        self.log(f"❌ Failed to start exploration for dungeon '{boss_name}': {message}", Fore.RED)
                else:
                    self.log(f"❌ Failed to start exploration for dungeon '{boss_name}': HTTP {explore_response.status_code}", Fore.RED)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Request error while starting exploration for dungeon '{boss_name}': {e}", Fore.RED)
            time.sleep(2)

        self.log("🔚 Dungeon process complete.", Fore.GREEN)

    def load_proxies(self, filename="proxy.txt"):
        """
        Reads proxies from a file and returns them as a list.

        Args:
            filename (str): The path to the proxy file.

        Returns:
            list: A list of proxy addresses.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                proxies = [line.strip() for line in file if line.strip()]
            if not proxies:
                raise ValueError("Proxy file is empty.")
            return proxies
        except Exception as e:
            self.log(f"❌ Failed to load proxies: {e}", Fore.RED)
            return []

    def set_proxy_session(self, proxies: list) -> requests.Session:
        """
        Creates a requests session with a working proxy from the given list.

        If a chosen proxy fails the connectivity test, it will try another proxy
        until a working one is found. If no proxies work or the list is empty, it
        will return a session with a direct connection.

        Args:
            proxies (list): A list of proxy addresses (e.g., "http://proxy_address:port").

        Returns:
            requests.Session: A session object configured with a working proxy,
                            or a direct connection if none are available.
        """
        # If no proxies are provided, use a direct connection.
        if not proxies:
            self.log("⚠️ No proxies available. Using direct connection.", Fore.YELLOW)
            self.proxy_session = requests.Session()
            return self.proxy_session

        # Copy the list so that we can modify it without affecting the original.
        available_proxies = proxies.copy()

        while available_proxies:
            proxy_url = random.choice(available_proxies)
            self.proxy_session = requests.Session()
            self.proxy_session.proxies = {"http": proxy_url, "https": proxy_url}

            try:
                test_url = "https://httpbin.org/ip"
                response = self.proxy_session.get(test_url, timeout=5)
                response.raise_for_status()
                origin_ip = response.json().get("origin", "Unknown IP")
                self.log(
                    f"✅ Using Proxy: {proxy_url} | Your IP: {origin_ip}", Fore.GREEN
                )
                return self.proxy_session
            except requests.RequestException as e:
                self.log(f"❌ Proxy failed: {proxy_url} | Error: {e}", Fore.RED)
                # Remove the failed proxy and try again.
                available_proxies.remove(proxy_url)

        # If none of the proxies worked, use a direct connection.
        self.log("⚠️ All proxies failed. Using direct connection.", Fore.YELLOW)
        self.proxy_session = requests.Session()
        return self.proxy_session

def override_requests(self):
    """Override requests functions globally when proxy is enabled."""
    if self.config.get("proxy", False):
        self.log("[CONFIG] 🛡️ Proxy: ✅ Enabled", Fore.YELLOW)
        proxies = self.load_proxies()
        if not proxies:
            self.log("⚠️ No proxies available. Using direct connection.", Fore.YELLOW)
            return
            
        self.set_proxy_session(proxies)
        
        # Zapisz oryginalne funkcje, jeśli jeszcze nie zapisano
        if not self._original_requests.get("get"):
            self._original_requests = {
                "get": requests.get,
                "post": requests.post,
                "put": requests.put,
                "delete": requests.delete,
            }

        # Override request methods
        requests.get = self.proxy_session.get
        requests.post = self.proxy_session.post
        requests.put = self.proxy_session.put
        requests.delete = self.proxy_session.delete
        self.log("✅ Request methods overridden with proxy session", Fore.GREEN)
    else:
        self.log("[CONFIG] proxy: ❌ Disabled", Fore.RED)
        # Restore original functions if proxy is disabled and originals exist
        if self._original_requests.get("get"):
            requests.get = self._original_requests["get"]
            requests.post = self._original_requests["post"]
            requests.put = self._original_requests["put"]
            requests.delete = self._original_requests["delete"]
            self.log("✅ Request methods restored to originals", Fore.GREEN)

async def process_account(account, original_index, account_label, pix, config):
    # Wyświetlanie informacji o koncie
    display_account = account[:10] + "..." if len(account) > 10 else account
    pix.log(f"👤 Przetwarzanie {account_label}: {display_account}", Fore.YELLOW)
    
    # Zachowanie oryginalnych funkcji requests
    original_get = requests.get
    original_post = requests.post
    original_put = requests.put
    original_delete = requests.delete
    
    try:
        # Sprawdzanie i ustawianie proxy, jeśli włączone
        if config.get("proxy", False):
            proxies = pix.load_proxies()
            if not proxies:
                pix.log("⚠️ Brak dostępnych proxy. Używam bezpośredniego połączenia.", Fore.YELLOW)
            else:
                # Wybierz proxy, używając modulo aby nie wyjść poza zakres
                proxy_index = original_index % len(proxies)
                proxy_url = proxies[proxy_index]
                
                pix.log(f"🔄 Próba użycia proxy #{proxy_index}: {proxy_url} dla konta {account_label}", Fore.CYAN)
                
                # Utwórz sesję z wybranym proxy
                pix.proxy_session = requests.Session()
                pix.proxy_session.proxies = {"http": proxy_url, "https": proxy_url}
                
                # Testuj proxy
                try:
                    test_url = "https://httpbin.org/ip"
                    response = pix.proxy_session.get(test_url, timeout=5)
                    response.raise_for_status()
                    origin_ip = response.json().get("origin", "Unknown IP")
                    pix.log(f"✅ Proxy działa: {proxy_url} | IP: {origin_ip}", Fore.GREEN)
                    
                    # Zastąp globalne funkcje requests
                    requests.get = pix.proxy_session.get
                    requests.post = pix.proxy_session.post
                    requests.put = pix.proxy_session.put
                    requests.delete = pix.proxy_session.delete
                except requests.RequestException as e:
                    pix.log(f"❌ Proxy niedziałające: {proxy_url} | Błąd: {e}", Fore.RED)
                    pix.log(f"⚠️ Używam bezpośredniego połączenia dla konta {account_label}", Fore.YELLOW)
                    # Zachowaj oryginalne funkcje requests w przypadku błędu proxy
        else:
            pix.log("[CONFIG] Proxy: ❌ Wyłączone", Fore.RED)
        
        # Login (funkcja blokująca, uruchamiana w osobnym wątku) używając oryginalnego indeksu
        await asyncio.to_thread(pix.login, original_index)
        
        # Sprawdź czy login się powiódł
        if not pix.token:
            pix.log(f"❌ Logowanie nie powiodło się dla konta {account_label}. Pomijam.", Fore.RED)
            return
        
        pix.log("🛠️ Rozpoczynam wykonywanie zadań...", Fore.CYAN)
        tasks_config = {
            "task": "Automatyczne wykonywanie codziennych zadań! 🤖✅",
            "farming": "Automatyczne zbieranie zasobów! 🌾🍀",
            "dungeon": "Podbijanie lochów i zbieranie nagród! 🏰⚔️"
        }
        
        for task_key, task_name in tasks_config.items():
            task_status = config.get(task_key, False)
            color = Fore.YELLOW if task_status else Fore.RED
            pix.log(f"[CONFIG] {task_name}: {'✅ Włączone' if task_status else '❌ Wyłączone'}", color)
            if task_status:
                pix.log(f"🔄 Wykonuję {task_name}...", Fore.CYAN)
                await asyncio.to_thread(getattr(pix, task_key))
        
    except Exception as e:
        pix.log(f"❌ Błąd podczas przetwarzania konta {account_label}: {e}", Fore.RED)
    finally:
        # Zawsze przywracaj oryginalne funkcje requests
        requests.get = original_get
        requests.post = original_post
        requests.put = original_put
        requests.delete = original_delete
    
    delay_switch = config.get("delay_account_switch", 10)
    pix.log(f"➡️ Zakończono przetwarzanie {account_label}. Oczekiwanie {Fore.WHITE}{delay_switch}{Fore.CYAN} sekund przed następnym kontem.", Fore.CYAN)
    await asyncio.sleep(delay_switch)

async def worker(worker_id, pix, config, queue):
    """
    Setiap worker akan mengambil satu akun dari antrian dan memprosesnya secara berurutan.
    Worker tidak akan mengambil akun baru sebelum akun sebelumnya selesai diproses.
    """
    while True:
        try:
            original_index, account = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        account_label = f"Worker-{worker_id} Account-{original_index+1}"
        await process_account(account, original_index, account_label, pix, config)
        queue.task_done()
    pix.log(f"Worker-{worker_id} finished processing all assigned accounts.", Fore.CYAN)

async def main():
    pix = pixiland() 
    config = pix.load_config()
    all_accounts = pix.query_list
    num_threads = config.get("thread", 1)  # Jumlah worker sesuai konfigurasi
    
    if config.get("proxy", False):
        proxies = pix.load_proxies()
    
    pix.log("🎉 [LIVEXORDS] === Welcome to Pixiland Automation === [LIVEXORDS]", Fore.YELLOW)
    pix.log(f"📂 Loaded {len(all_accounts)} accounts from query list.", Fore.YELLOW)
    
    while True:
        # Buat queue baru dan masukkan semua akun (dengan index asli)
        queue = asyncio.Queue()
        for idx, account in enumerate(all_accounts):
            queue.put_nowait((idx, account))
        
        # Buat task worker sesuai dengan jumlah thread yang diinginkan
        workers = [asyncio.create_task(worker(i+1, pix, config, queue)) for i in range(num_threads)]
        
        # Tunggu hingga semua akun di queue telah diproses
        await queue.join()
        
        # Opsional: batalkan task worker (agar tidak terjadi tumpang tindih)
        for w in workers:
            w.cancel()
        
        pix.log("🔁 All accounts processed. Restarting loop.", Fore.CYAN)
        delay_loop = config.get("delay_loop", 30)
        pix.log(f"⏳ Sleeping for {Fore.WHITE}{delay_loop}{Fore.CYAN} seconds before restarting.", Fore.CYAN)
        await asyncio.sleep(delay_loop)

if __name__ == "__main__":
    asyncio.run(main())
