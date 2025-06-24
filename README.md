# 🔍 Netspend Account Checker

A robust and **multithreaded email validation tool** designed for Netspend accounts. This tool is built for **educational**, **research**, and **security testing** purposes only.

---

## 🌟 Features

* **Multithreaded Validation**: Efficiently verifies multiple emails concurrently.
* **Proxy Support**: Optional integration with `proxy.txt` for anonymous requests.
* **Dynamic User-Agents**: Utilizes `fake-useragent` for randomized User-Agent headers.
* **Automatic Retries**: Employs `tenacity` to automatically retry on connection failures.
* **Colored CLI Output**: Enhances readability with colored console output via `colorama` and `termcolor`.
* **Automatic Result Saving**: Saves valid emails to `live.txt` and invalid ones to `dead.txt`.
* **Detailed Debugging**: Provides response time and IP debug information for each check.

---

## 🛠️ Tech Stack

* Python 3.8+
* Requests
* Colorama
* Termcolor
* Tenacity
* Fake-useragent

---

## ⚙️ Installation Guide

> 🧠 Ensure you have Python 3.8+ installed on your system. You can verify your Python version by running:
> ```bash
> python --version
> ```

### 1. Clone the Repository

```bash
git clone https://github.com/martinversacodeG/netspend-checker.git
cd netspend-checker
````

### 2\. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

This command will install all necessary libraries: `requests`, `colorama`, `termcolor`, `tenacity`, and `fake-useragent`.

-----

## 🚀 How to Use

### 1\. Prepare Your Email List

Create a text file (e.g., `emails.txt`) with one email address per line:

```
test1@example.com
test2@example.com
```

### 2\. Prepare Your Proxy List (Optional)

If you wish to use proxies, create a `proxy.txt` file with one proxy per line. Both `IP:Port` and `username:password@IP:Port` formats are supported:

```
127.0.0.1:8080
user:pass@192.168.1.1:8888
```

### 3\. Run the Script

```bash
python gass.py
```

The script will prompt you to enter the email list filename and the desired number of threads.

-----

## 🗃️ Output

All results are automatically saved in the `result/` directory:

```
result/
├── live.txt    # ✅ Contains valid email addresses
└── dead.txt    # ❌ Contains invalid email addresses
```

Each line in the output files will include the email and its status, along with any relevant API descriptions.

-----

## 📸 Sample CLI Output

```
Enter Email List File Name (e.g., emails.txt): emails.txt
Enter Number of Threads (e.g., 120): 100

Proxy list successfully loaded from 'proxy.txt'. Total proxies: 50
Starting account check...
Total emails to be checked: 120
Number of threads used: 100
Results will be saved in folder: result/

[3/120] (2.50%) [LIVE - saved to result/live.txt] john@example.com [Time: 1.12s]
[4/120] (3.33%) [DEAD - saved to result/dead.txt] jane@example.com - Email not found [Time: 0.98s]
```

-----


## 📬 Contact & Support

For any questions, customization requests, or if you find this tool helpful, feel free to reach out:

  * **Telegram**: @martinversa

-----

## ⚠️ Disclaimer

This tool is strictly for:

  * **Educational use**.
  * **Authorized penetration testing**.
  * **Security research**.

**Do not use this tool for unauthorized or illegal activities.** The author is not responsible for any misuse of this script.
