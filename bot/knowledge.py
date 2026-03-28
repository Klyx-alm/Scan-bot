import subprocess
import re
import os
from vulnerability import analyze_service

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
                ["nmap", "-F", "-sV", target],
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
                ["nmap", "-sV", "--script", "vuln", target],
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
            result = subprocess.check_output(
                ["nmap", "-sV", target],
                stderr=subprocess.STDOUT,
                env=env
            )
            return result.decode()
        except Exception as e:
            return str(e)

    # ---------------- PORT SCAN ----------------
    def port_scan(self, target):
        try:
            env = os.environ.copy()
            env['LANG'] = 'C'
            env['LC_ALL'] = 'C'
            result = subprocess.check_output(
                ["nmap", "-p-", target],
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

    # ---------------- ANALYSE INTELLIGENTE ----------------
    def analyze_scan(self, scan_output):

        # 🔥 Si IA dispo → analyse avancée
        if AI_ENABLED:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional penetration tester. Analyze this Nmap scan and provide: vulnerabilities, CVEs, attack vectors, and recommendations."
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

        # 🔥 fallback manuel (sans IA)
        findings = []

        # CVE détectées dans output
        cves = re.findall(r"CVE-\d{4}-\d+", scan_output)

        for cve in set(cves):
            findings.append(f"🚨 Found CVE: {cve}")

        # Analyse services
        services = self.extract_services(scan_output)

        for s in services:
            vulns = analyze_service(s)
            findings.extend([f"{s} → {v}" for v in vulns])

        if not findings:
            return "✅ No vulnerabilities detected but manual testing advised"

        return "\n".join(set(findings))

    # ---------------- CHAT IA ----------------
    def chat(self, message):

        msg = message.lower()

        # 🔥 EXTRAIRE IP automatiquement
        ip_match = re.search(r"\d{1,3}(?:\.\d{1,3}){3}", msg)
        ip = ip_match.group(0) if ip_match else None

        # ---------------- INTENT DETECTION ----------------

        # SCAN
        if any(word in msg for word in ["scan", "scanner"]):
            if ip:
                return self.scan(ip)
            return "⚠️ Please provide a valid IP"

        # DEEP SCAN
        if any(word in msg for word in ["deep", "approfondi"]):
            if ip:
                return self.deep_scan(ip)
            return "⚠️ Please provide a valid IP"

        # PORT SCAN
        if any(word in msg for word in ["port", "ports"]):
            if ip:
                return self.port_scan(ip)
            return "⚠️ Please provide a valid IP"

        # OS DETECTION
        if any(word in msg for word in ["os", "system", "système"]):
            if ip:
                return self.detect_os(ip)
            return "⚠️ Please provide a valid IP"

        # ANALYSE VULN
        if any(word in msg for word in ["analyse", "analyze", "vuln", "vulnerability"]):
            return "👉 Run a scan first, then click 'Analyze' button for full report"

        # ---------------- IA MODE ----------------

        if AI_ENABLED:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are an elite penetration tester.

Be professional, detailed and practical.

When user asks:
- Explain vulnerabilities
- Suggest exploits
- Give attack scenarios
- Give mitigation steps

Always answer like a real cybersecurity expert."""
                        },
                        {
                            "role": "user",
                            "content": message
                        }
                    ],
                    temperature=0.7
                )

                return response.choices[0].message.content

            except Exception as e:
                return f"AI error: {str(e)}"

        # ---------------- FALLBACK ----------------

        return """🤖 Available commands:
- scan <ip>
- deep <ip>
- port <ip>
- os <ip>
- analyze

Example:
scan 192.168.1.1
"""

    def get_welcome(self):
        if AI_ENABLED:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are Scan Bot, a professional pentesting AI assistant. Welcome the user cordially, introduce yourself, describe what Scan Bot does and how to use it."
                        },
                        {
                            "role": "user",
                            "content": "Welcome message"
                        }
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                return "Welcome to Scan Bot! I am your AI assistant for pentesting. Scan Bot helps you perform network scans, vulnerability analysis, and directory busting. Enter an IP and use the buttons to scan, or ask me questions."
        else:
            return "Welcome to Scan Bot! I am your AI assistant for pentesting. Scan Bot helps you perform network scans, vulnerability analysis, and directory busting. Enter an IP and use the buttons to scan, or ask me questions."