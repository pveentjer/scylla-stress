import os
import subprocess
import time
from sso.util import run_parallel


# Parallel SSH
class PSSH:

    def __init__(self, ip_list, user, ssh_options, wait_for_connect=True, silent_seconds=30):
        self.ip_list = ip_list
        self.user = user
        self.ssh_options = ssh_options
        self.wait_for_connect = wait_for_connect
        self.silent_seconds = silent_seconds
        self.log_ssh = False

    def __new_ssh(self, ip):
        return SSH(ip, self.user, self.ssh_options, wait_for_connect=self.wait_for_connect,
                   silent_seconds=self.silent_seconds)

    def __exec(self, ip, cmd):
        self.__new_ssh(ip).exec(cmd)

    def exec(self, cmd):
        run_parallel(self.__exec, [(ip, cmd) for ip in self.ip_list])

    def async_exec(self, command):
        thread = WorkerThread(self.exec, (command))
        thread.start()
        return thread.future

    def __update(self, ip):
        self.__new_ssh(ip).update()

    def update(self):
        # todo: needs to be fixed; should be parallel, now sequential
        for ip in self.ip_list:
            ssh = SSH(ip, self.user, self.ssh_options)
            ssh.update()

        # can't get this to run correctly.
        #run_parallel(self.__update, [ip for ip in self.ip_list])

    def __install_one(self, ip, *packages):
        self.__new_ssh(ip).install_one(*packages)

    def install_one(self, *packages):
        run_parallel(self.__install_one, [(ip, *packages) for ip in self.ip_list])

    def __try_install(self, ip, *packages):
        self.__new_ssh(ip).try_install(*packages)

    def try_install(self, *packages):
        run_parallel(self.__try_install, [(ip, *packages) for ip in self.ip_list])

    def __install(self, ip, *packages):
        self.__new_ssh(ip).install(*packages)

    def install(self, *packages):
        run_parallel(self.__install, [(ip, *packages) for ip in self.ip_list])

    def __scp_from_remote(self, src, dst_dir, ip):
        self.__new_ssh(ip).scp_from_remote(src,  os.path.join(dst_dir, ip))

    def scp_from_remote(self, src, dst_dir):
        run_parallel(self.__scp_from_remote, [(src, dst_dir, ip) for ip in self.ip_list])

    def __scp_to_remote(self, src, dst, ip):
         self.__new_ssh(ip).scp_to_remote(src, dst)
         
    def scp_to_remote(self, src, dst):
        run_parallel(self.__scp_to_remote, [(src, dst, ip) for ip in self.ip_list])

  
class SSH:

    def __init__(self, ip, user, ssh_options, wait_for_connect=True, silent_seconds=30):
        self.ip = ip
        self.user = user
        self.ssh_options = ssh_options
        self.wait_for_connect = wait_for_connect
        self.silent_seconds = silent_seconds
        self.log_ssh = False

    def __wait_for_connect(self):
        if not self.wait_for_connect:
            return

        cmd = f'ssh {self.ssh_options} {self.user}@{self.ip} ls'
        exitcode = None
        for i in range(1, 300):
            if i > self.silent_seconds:
                print(f"[{i}] Connect to {self.ip}")
                exitcode = subprocess.call(cmd, shell=True)
            else:
                exitcode = subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if exitcode == 0 or exitcode == 1:  # todo: we need to deal better with exit code
                self.wait_for_connect = False
                return
            time.sleep(1)

        raise Exception(f"Failed to connect to {self.ip}, exitcode={exitcode}")

    def scp_from_remote(self, src, dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
        cmd = f'scp {self.ssh_options} -r -q {self.user}@{self.ip}:{src} {dst_dir}'
        self.__scp(cmd)

    def scp_to_remote(self, src, dst):
        cmd = f'scp {self.ssh_options} -r -q {src} {self.user}@{self.ip}:{dst}'
        self.__scp(cmd)

    def __scp(self, cmd):
        self.__wait_for_connect()
        exitcode = subprocess.call(cmd, shell=True)
        # raise Exception(f"Failed to execute {cmd} after {self.max_attempts} attempts")

    def exec(self, command, ignore_errors=False):
        self.__wait_for_connect()

        cmd = f'ssh {self.ssh_options} {self.user}@{self.ip} \'{command}\''
        exitcode = subprocess.call(cmd, shell=True)

        if ignore_errors or exitcode == 0 or exitcode == 1:  # todo: we need to deal better with exit code
            return
        else:
            raise Exception(f"Failed to execute {cmd}, exitcode={exitcode}")

    def async_exec(self, command):
        thread = WorkerThread(self.exec, (command))
        thread.start()
        return thread.future

    def update(self):
        print(f'    [{self.ip}] Update: started')
        self.exec(
            f"""
            set -e
            if hash apt-get 2>/dev/null; then
                sudo apt-get -y -qq update
            elif hash yum 2>/dev/null; then
                sudo yum -y -q update
            else
                echo "Cannot update: yum/apt not found"
                exit 1
            fi""")
        print(f'    [{self.ip}] Update: done')

    def install_one(self, *packages):
        self.exec(
            f"""
            set -e
            for package in {" ".join(packages)} 
            do                
                echo Trying package [$package]
                if hash apt-get 2>/dev/null ; then
                    if sudo apt show $package >/dev/null 2>&1; then
                        echo      [{self.ip}] Installing $package
                        sudo apt-get install -y -qq $package
                        exit 0
                    fi    
                elif hash yum 2>/dev/null; then
                    if sudo yum info $package >/dev/null 2>&1; then
                        echo      [{self.ip}] Installing $package
                        sudo yum -y -q install $package
                        exit 0
                    fi                        
                else
                    echo "     [{self.ip}] Cannot install $package: yum/apt not found"
                    exit 1
                fi
                    
                echo Not found $package                       
            done
            echo "Could not find any of the packages from {packages}"
            exit 1
            """)

    def try_install(self, *packages):
        self.install(*packages, ignore_errors=True)

    def install(self, *packages, ignore_errors=False):
        for package in packages:
            print(f'    [{self.ip}] Install: {package}')
            self.exec(
                f"""
                set -e
                if hash apt-get 2>/dev/null; then
                    sudo apt-get install -y -qq {package}
                elif hash yum 2>/dev/null; then
                    sudo yum -y -q install {package}
                else
                    echo "Cannot install {package}: yum/apt not found"
                    exit 1
                fi
                """, ignore_errors=ignore_errors)
