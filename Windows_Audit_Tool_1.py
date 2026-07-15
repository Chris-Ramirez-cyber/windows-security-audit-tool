import os 
import ctypes
import subprocess
import psutil
import platform
from datetime import datetime  
import socket
import winreg
import sys

report_file = open("audit_report.txt", "w")
sys.stdout = report_file

print("_" * 74, "BASIC INFO","_" * 74)
def get_user():
    return os.getenv('USER',os.getenv('USERNAME','user'))
def is_admin():
    return bool(ctypes.windll.shell32.IsUserAnAdmin() if os.name == 'nt' else os.getuid() == 0)
print(f"Current user: {get_user()}")
print(f"Admin: {is_admin()}")
print(f"Date: {datetime.now()}\n")



print("_" * 75, "USER LIST","_" * 74)
print("\nHere is a list of users on your computer:")

result = subprocess.run(
    ["net", "user"],
    capture_output=True,
    text=True
)
lines = result.stdout.splitlines()

users = []

reading_users = False

for line in lines:
    if '---' in line:
        reading_users = True
        continue

    if line == 'The command completed successfully.':
        break

    if reading_users:
        line = line.split()
        users.extend(line)
        
for user in users:
    print(user)




print("_" * 74, "ADMIN LIST","_" * 74)
print("\nList of admins:")

result = subprocess.run(
    ['net','localgroup','administrators'],
    capture_output=True,
    text=True
)

admin_lines = result.stdout.splitlines()

printing = False

for line in admin_lines:
    if '----' in line:
        printing = True
        continue

    if line == 'The command completed successfully.':
        break

    if printing:
        print(line)



print()
print("_" * 70, "SYSTEM INFORMATION","_" * 70)
sys_info = platform.uname()
print(f"\nSystem: {sys_info.system}")
print(f"Hostname: {sys_info.node}")
print(f"Release: {sys_info.release}")
print(f"Version: {sys_info.version}")
print(f"Machine: {sys_info.machine}")
print(f"Processor: {sys_info.processor}\n")



print("_" * 70, "NETWORK INFORMATION","_" * 70)
print()

def get_network_info():
    for interface, addresses in psutil.net_if_addrs().items():
        print(f"\nAdapter: {interface}")

        for addr in addresses:
            if addr.family == psutil.AF_LINK:
                print(f"  MAC Address: {addr.address}")

            if addr.family == socket.AF_INET:
                print(f"  IPv4 Address: {addr.address}")
                print(f"  Subnet Mask: {addr.netmask}")

            if addr.family == socket.AF_INET6:
                print(f"  IPv6 Address: {addr.address.split('%')[0]}")

    print()
    result = subprocess.run(
        ["ipconfig", "/all"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.splitlines()
    
    for i ,line in enumerate(lines):
        if "Default Gateway" in line:
            gateway = line.split(":")[1]

            if gateway.strip():
                print(f"  Default Gateway: {gateway.strip()}")

        if "DNS Servers" in line:
            dns = line.split(":")[1]
            
            if dns.strip():
                print(f"  DNS Server: {dns.strip()}")
                
                next_line = lines[i + 1].strip()

                if next_line and next_line[0].isdigit():
                    print(f"  DNS Server: {next_line}")

get_network_info()
print()




print ("_" * 70, "RUNNING PROCESSES", "_" * 70)
print()

print(f"{'PID':<10}{'Process Name':<30}{'Memory (MB)':<15}{'User':<30}{'Executable Path'}")
print("-" * 160)

for process in psutil.process_iter():
    try:
        memory = process.memory_info().rss / (1024 * 1024)
        user = process.username()
        path = process.exe()
        print(f"{process.pid:<10}{process.name():<30}{memory:<15.2f}{user:<30}{path}")
    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess
    ):
        pass

print()


print ("_" * 70, "INSTALLED SOFTWARE", "_" * 70)
print()
print(f"{'Name':<80}{'Version':<25}{'Publisher':<35}{'Installed'}")
print("_" * 160)

uninstall_key = winreg.OpenKey(
    winreg.HKEY_LOCAL_MACHINE,
    "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
    )

subkey_count, value_count, last_modified = winreg.QueryInfoKey(uninstall_key)

for i in range (subkey_count):
    try:
        subkey_iter = winreg.EnumKey(uninstall_key, i)
        single_key = winreg.OpenKey(
            uninstall_key,
            subkey_iter
        )        
    
        dis_name, reg_data_type = winreg.QueryValueEx(
            single_key,
            "DisplayName"
        )

        dis_name = dis_name.replace("\r\n", " ").replace("\n", " ").strip()

    except FileNotFoundError:
        continue

    try:

        dis_version, version_data_type = winreg.QueryValueEx(
            single_key,
            "DisplayVersion"
        )
    
    except FileNotFoundError:
        dis_version = "N/A"

    try:
        publisher, pub_data_type = winreg.QueryValueEx(
            single_key,
            "Publisher"
        )
    except FileNotFoundError:
        publisher = "N/A"

    try:
        install_date, install_date_data_type = winreg.QueryValueEx(
            single_key,
            "InstallDate"
        )
    except FileNotFoundError:
        install_date = "N/A"

    print(f"{dis_name:<80}{dis_version:<25}{publisher:<35}{install_date}")

    


print()
print ("_" * 67, "BASIC WINDOWS DEFENDER", "_" * 67)
print()

result = subprocess.run(
    ["powershell", "-Command", "Get-MpComputerStatus"],
    capture_output=True,
    text=True
)

lines = result.stdout.splitlines()
for line in lines:
    if line.startswith((
        "AMServiceEnabled",
        "AntivirusEnabled",
        "RealTimeProtectionEnabled",
        "AntivirusSignatureVersion",
    )):
        name, value = line.split(":",1)
        name = name.strip()
        value = value.strip()
        

        if name == "AMServiceEnabled":
            print(f"Defender Service: {value}")

        elif name == "AntivirusEnabled":
            print(f"Antivirus Enabled: {value}")

        elif name == "RealTimeProtectionEnabled":
            print(f"Real-Time Protection: {value}")

        elif name == "AntivirusSignatureVersion":
            print(f"SignatureVersion: {value}")



print("_" * 70, "WINDOWS FIREWALL", "_" * 70)
print()

result = subprocess.run(
    ["powershell", "-Command", "Get-NetFirewallProfile"],
    capture_output=True,
    text=True
)


lines = result.stdout.splitlines()

profile = ""

for line in lines:
    if line.startswith(("Name", "Enabled")):
        name, value = line.split(":", 1)
        name = name.strip()
        value = value.strip()

        if name == "Name":
            profile = value
        
        elif name == "Enabled":
            print(f"{profile} Firewall: {value}")



print("_" * 66, "OPEN NETWORK CONNECTIONS", "_" * 66)
print()

connections = psutil.net_connections()

print(f"{'Local IP':<20}{'Local Port':<15}{'Remote IP':<20}{'Remote Port':<15}{'Status':<15}{'PID':<10}{'Process Name':<25}")
print("_" * 158)


for conn in connections:
    if conn.raddr:
        try:
            process = psutil.Process(conn.pid).name()
        except:
            process = "Unknown"

        print(f"{conn.laddr.ip:<20}{conn.laddr.port:<15}{conn.raddr.ip:<20}{conn.raddr.port:<15}{conn.status:<15}{conn.pid:<10}{process:<25}")


print("_" * 70, "WINDOWS SERVICES", "_" * 70)
print()

services = psutil.win_service_iter()

print(f"{'Service Name':<45}{'Display Name':<60}{'Status':<25}")
print("_" * 158)

for service in services:
        display_name = service.display_name()

        if len(display_name) > 60:
            display_name = display_name[:57] + "..."
        print(f"{service.name():<45}{display_name:<60}{service.status():<25}")


report_file.close()