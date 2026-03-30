import subprocess
import re
import os
import shutil
from vulnerability import analyze_service

# 🔥 FIX PATH pour PyInstaller
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"
os.environ["PATH"] += os.pathsep + "/usr/local/bin"

# 🔥 Détection automatique de nmap
NMAP_PATH = shutil.which("nmap") or "/opt/homebrew/bin/nmap"

# 🔥 IA (OpenAI)
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    AI_ENABLED = True
except:
    AI_ENABLED = False


class HackerBot:

    # ---------------- SCAN ----------------
    def scan(self, target):
        try:
            env = os.environ.copy()
            env['LANG'] = 'C'
            env['LC_ALL'] = 'C'

            result = subprocess.check_output(
                [NMAP_PATH, "-F", "-sV", target],
                stderr=subprocess.STDOUT,
                env=env
            )
            return result.decode()

        except Exception as e:
            return str(e)

    # ---------------- DEEP SCAN ----------------
    def deep_scan(self, target):
        try:
            env = os.environ.copy()
            env['LANG'] = 'C'
            env['LC_ALL'] = 'C'

            result = subprocess.check_output(
                [NMAP_PATH, "-sV", "--script", "vuln", target],
                stderr=subprocess.STDOUT,
                env=env
            )
            return result.decode()

        except Exception as e:
            return str(e)

    # ---------------- OS ----------------
    def detect_os(self, target):
        try:
            env = os.environ.copy()
            env['LANG'] = 'C'
            env['LC_ALL'] = 'C'

            try:
                result = subprocess.check_output(
                    ["sudo", NMAP_PATH, "-O", target],
                    stderr=subprocess.STDOUT,
                    env=env
                )
                return result.decode()

            except:
                result = subprocess.check_output(
                    [NMAP_PATH, "-sV", target],
                    stderr=subprocess.STDOUT,
                    env=env
                )
                return "⚠️ OS detection needs admin (sudo)\n\nFallback scan:\n\n" + result.decode()

        except Exception as e:
            return str(e)

    # ---------------- PORT SCAN ----------------
    def port_scan(self, target):
        try:
            env = os.environ.copy()
            env['LANG'] = 'C'
            env['LC_ALL'] = 'C'

            result = subprocess.check_output(
                [NMAP_PATH, "-p-", target],
                stderr=subprocess.STDOUT,
                env=env
            )
            return result.decode()

        except Exception as e:
            return str(e)

    # ---------------- EXTRACTION SERVICES ----------------
    def extract_services(self, scan_output):
        services = []

        for line in scan_output.split("\n"):
            if "open" in line:
                parts = line.split()
                if len(parts) >= 3:
                    service = parts[2]
                    version = " ".join(parts[3:])
                    services.append(service + " " + version)

        return services

    # ---------------- ANALYSE ----------------
    def analyze_scan(self, scan_output):

        # 🔥 IA
        if AI_ENABLED:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional penetration tester. Analyze this Nmap scan and provide vulnerabilities, CVEs, attack vectors, and recommendations."
                        },
                        {
                            "role": "user",
                            "content": scan_output
                        }
                    ]
                )

                return response.choices[0].message.content

            except Exception as e:
                return f"AI error: {str(e)}"

        # 🔥 fallback manuel
        findings = []

        cves = re.findall(r"CVE-\d{4}-\d+", scan_output)

        for cve in set(cves):
            findings.append(f"🚨 Found CVE: {cve}")

        services = self.extract_services(scan_output)

        for s in services:
            vulns = analyze_service(s)
            findings.extend([f"{s} → {v}" for v in vulns])

        if not findings:
            return "✅ No vulnerabilities detected but manual testing advised"

        return "\n".join(set(findings))

    # ---------------- CHAT ----------------
    def chat(self, message):

        msg = message.lower()

        ip_match = re.search(r"\d{1,3}(?:\.\d{1,3}){3}", msg)
        ip = ip_match.group(0) if ip_match else None

        # SCAN
        if any(word in msg for word in ["scan", "scanner"]):
            if ip:
                return self.scan(ip)
            return "⚠️ Please provide a valid IP"

        # DEEP
        if any(word in msg for word in ["deep", "approfondi"]):
            if ip:
                return self.deep_scan(ip)
            return "⚠️ Please provide a valid IP"

        # PORT
        if any(word in msg for word in ["port", "ports"]):
            if ip:
                return self.port_scan(ip)
            return "⚠️ Please provide a valid IP"

        # OS
        if any(word in msg for word in ["os", "system", "système"]):
            if ip:
                return self.detect_os(ip)
            return "⚠️ Please provide a valid IP"

        # ANALYSE
        if any(word in msg for word in ["analyse", "analyze", "vuln"]):
            return "👉 Run a scan first, then click Analyze"

        # IA libre
        if AI_ENABLED:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an elite penetration tester."},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content

            except Exception as e:
                return f"AI error: {str(e)}"

        return "🤖 Use commands like: scan <ip>, deep <ip>, port <ip>, os <ip>"

    # ---------------- WELCOME ----------------
    def get_welcome(self):
        return """👋 Welcome to ScanBot

🔍 ScanBot helps you analyze machines via IP

• Scan ports
• Detect OS
• Find vulnerabilities
• Analyze results

💡 Enter an IP and start scanning

🤖 I help you understand and exploit results
"""