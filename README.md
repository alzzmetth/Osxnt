

---

OSXNT

OSXNT adalah toolkit OSINT (Open Source Intelligence) berbasis Python yang dirancang untuk pengumpulan informasi publik, analisis infrastruktur jaringan, enumerasi domain, dan riset keamanan.

Tool ini dibuat untuk kebutuhan edukasi, security research, dan pengujian yang memiliki izin (authorized testing).


---

✨ Features

IP Geolocation & Network Intelligence

DNS & WHOIS Analysis

Multi-threaded Port Scanning

Subdomain Enumeration (Wordlist-based)

Website Source Downloader (HTML, CSS, JS)

Multi-target Scanning

JSON Export Support

Proxy & Tor Support

Configurable Threading & Timeout

Modular CLI Architecture



---

📦 Requirements

Python 3.8+

pip


Dependencies

Package	Purpose

requests	HTTP Requests
dnspython	DNS Resolution
python-whois	WHOIS Lookup
colorama	CLI Color Output
beautifulsoup4	HTML Parsing
pysocks	Proxy Support


Install dependencies:

pip install -r requirements.txt


---

🚀 Installation

git clone https://github.com/alzzdevmaret/osxnt.git
cd osxnt
pip install -r requirements.txt
mkdir -p requiments
python osxnt.py --version


---

🧭 Usage

Global Options

Option	Description

-h, --help	Show help menu
--version	Show version
-v	Verbose mode
-s <file>	Save output to JSON
-about	Tool information



---

Modules


---

1️⃣ IP Tracking

Track geolocation and network metadata from IP address or domain.

python osxnt.py -trackip 8.8.8.8
python osxnt.py -trackip google.com -v

Output includes:

IP Address

Country

Region

City

ISP

Organization

ASN

Coordinates

Proxy/VPN Detection (verbose)



---

2️⃣ Web Tracking

IP Resolution Mode

python osxnt.py -webtrack ip -ip google.com

Returns:

IPv4 / IPv6

Reverse DNS

DNS Records

WHOIS Information


DNS Lookup Mode

python osxnt.py -webtrack dns -dns google.com

Supported DNS Types: A, AAAA, MX, NS, TXT, CNAME, SOA, CAA


---

3️⃣ Port Scanner

Multi-threaded TCP scanner with service detection.

python osxnt.py -scan -p 80,443,22 target.com
python osxnt.py -scan -p 1-1000 192.168.1.1 -v

Supported formats:

Single: -p 80

Multiple: -p 22,80,443

Range: -p 1-1000

Mixed: -p 22,80,8000-9000



---

4️⃣ Subdomain Scanner

Enumerate subdomains using wordlists.

python osxnt.py -sbdomain target.com
python osxnt.py -sbdomain -use 50 -w custom.txt target.com

Options:

Option	Description	Default

-use	Thread count	20
-w	Custom wordlist	requiments/subdomain.txt



---

5️⃣ Web Source Downloader

Download website source for offline analysis.

python osxnt.py -trackweb target.com -c html,css,js -o output/$result$

Placeholder $result$ otomatis diganti dengan nama domain yang disanitasi.


---

6️⃣ Gmail Spam

Simulasi pengiriman email untuk skenario edukasi.

python osxnt.py -gmail-spam user@gmail.com -subj "Test" -body "Hello" -c 10

Tidak mengirim email nyata. next update asli! 


---

📂 Multi-Target Support

Gunakan file berisi daftar target:

8.8.8.8
google.com
192.168.1.1

Contoh:

python osxnt.py -trackip -ft targets.txt -v


---

💾 JSON Output

Semua modul mendukung ekspor JSON:

python osxnt.py -trackip 8.8.8.8 -s output.json

Struktur output:

{
  "timestamp": "...",
  "target": "...",
  "module": "...",
  "data": { }
}


---

🔌 Proxy & Tor Support

Tor (SOCKS5)

Automatic service detection

IP rotation

Control port support


Default port:

9050 (SOCKS)
9051 (Control)

HTTP / SOCKS Proxy

Format file:

127.0.0.1:8080
user:pass@proxy:8080
socks5://127.0.0.1:9050


---

⚙️ Configuration

Edit:

config/config.json

Example:

{
  "threads": 20,
  "timeout": 3,
  "output_dir": "output",
  "user_agent": "Mozilla/5.0 ...",
  "tor_port": 9050,
  "tor_control_port": 9051,
  "max_retries": 3,
  "default_delay": 1
}


---

🛠 Troubleshooting

Issue	Solution

ModuleNotFoundError	Install requirements
DNS Resolution Failed	Check domain
Rate Limit	Increase delay
Connection Refused	Verify proxy / network



---

📜 License

MIT License

Copyright (c) 2026 alzzdevmaret

Software provided "AS IS" without warranty.


---

⚠️ Legal Notice

Tool ini hanya untuk:

Security research

Educational purposes

Authorized penetration testing


Pengguna bertanggung jawab penuh atas penggunaan dan kepatuhan terhadap hukum yang berlaku.


---

🤝 Contributing

Contributions are welcome.

Fork repository

Create feature branch

Submit pull request



---

⭐ Support

Jika tool ini bermanfaat:

Star repository

Report issues

Suggest improvements

Contribute code



---
## last updated 2.2 

<img width="602" height="399" alt="1000216628" src="https://github.com/user-attachments/assets/603a8101-71b9-4015-8086-478a3d1eb5d5" />
