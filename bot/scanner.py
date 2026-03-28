import nmap
from vulnerability import analyze_service


class NetworkScanner:

    def __init__(self):
        self.scanner = nmap.PortScanner()

    def scan_target(self, target):

        print("\n[+] Scan intelligent en cours...\n")

        self.scanner.scan(target, arguments='-sT -sV -T4')

        results = []

        for host in self.scanner.all_hosts():

            print("Host :", host)

            for proto in self.scanner[host].all_protocols():

                ports = self.scanner[host][proto].keys()

                for port in ports:

                    service = self.scanner[host][proto][port]['name']

                    print(f"Port {port} → {service}")

                    vulns = analyze_service(service)

                    for v in vulns:
                        print("   ⚠", v)

                    results.append((port, service, vulns))

        return results