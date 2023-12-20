import paramiko
import subprocess

def check_ssh(ip, port, user, password):
    try:
        subprocess.check_output(
            ['sshpass', '-p', password, 'ssh', '-o', 'StrictHostKeyChecking=no', '-p', port, f'{user}@{ip}', 'echo 2>&1'],
            timeout=5,
            stderr=subprocess.STDOUT,
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except subprocess.TimeoutExpired:
        return False

def get_server_info(ip, port, user, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=int(port), username=user, password=password, timeout=5)

        # Command to retrieve RAM information
        ram_command = "free -h | awk '/^Mem:/ {print $2}'"

        # Command to retrieve storage information
        storage_command = "df -h --total | grep total | awk '{print $2}'"

        # Command to retrieve Unix information
        unix_command = "uname -a"

        # Command to retrieve country information
        country_command = "curl ipinfo.io/country"

        # Execute commands and retrieve output
        server_info = {
            "Ram": run_command(ssh, ram_command),
            "Storage": run_command(ssh, storage_command),
            "Unix": run_command(ssh, unix_command),
            "Country": run_command(ssh, country_command)
        }

        return server_info

    except Exception as e:
        print(f"Error getting information from {ip}: {e}")
        return None

def run_command(ssh, command):
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode("utf-8").strip()
        return result if result else "N/A"
    except Exception as e:
        print(f"Error running command: {command}, Error: {e}")
        return "N/A"

def main(input_file):
    live_output_file = 'live_ssh.txt'
    server_info_file = 'server_info.txt'

    with open(input_file, 'r') as f:
        lines = f.readlines()

    live_ssh_list = []

    for line in lines:
        fields = line.strip().split('|')
        if len(fields) == 4:
            ip, port, user, password = fields
            print(f'Checking {ip}|{port}|{user}')
            if check_ssh(ip, port, user, password):
                print(f'Success: {ip}|{port}|{user} is live')
                live_ssh_list.append(fields)
                server_info = get_server_info(ip, port, user, password)
                if server_info:
                    print(f"Server Info for {ip}: {server_info}\n")
                    with open(server_info_file, 'a') as info_file:
                        info_file.write(f"{ip}|{port}|{user}|{password}\n")
                        info_file.write(f"Ram: {server_info['Ram']}\n")
                        info_file.write(f"Storage: {server_info['Storage']}\n")
                        info_file.write(f"Unix: {server_info['Unix']}\n")
                        info_file.write(f"Country: {server_info['Country']}\n\n")

    print(f'SSH check complete. Results saved to {live_output_file} and {server_info_file}')

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python script.py <ssh_list_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
