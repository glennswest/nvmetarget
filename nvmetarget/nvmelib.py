#!/usr/bin/env python
## Insprired by:
##https://jing.rocks/2023/06/13/Experimenting-with-NVMe-over-TCP.html

import os
import subprocess
import syslog
from pysondb import getDb
import socket


class NvmeTarget:
      def get_ip(self):
          s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          s.settimeout(0)
          try:
              # doesn't even have to be reachable
              s.connect(('10.254.254.254', 1))
              IP = s.getsockname()[0]
          except Exception:
              IP = '127.0.0.1'
          finally:
              s.close()
          return IP

      def __init__(self):
          # syslog(syslog.LOG_INFO, "NvmeTargetLib: Initializing")
          os.system("modprobe nvmet_tcp")
          self.home_dir = os.path.expanduser('~/.nvmetarget')
          print(self.home_dir)
          os.makedirs(self.home_dir,exist_ok=True)
          self.target_db = getDb('/etc/nvmetarget.json')
          self.ip = self.get_ip()

      def run_command(self,command):
          process = subprocess.run(command, shell=True, capture_output=True, text=True)
          return process.stdout

      def get_loop_device(self):
          thedevice = self.run_command("losetup -f")
          print("Loop Device: " + thedevice)
          return(thedevice)

      def parse_size(self,size):
          units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}
          number, unit = [string.strip() for string in size.split()]
          return int(float(number)*units[unit])

      def echo(self,thevalue, thefile):
          thepath = os.path.expanduser(thefile)
          with open(thepath, "w") as text_file:
              text_file.write(thevalue)

      def read(self,thefile):
          thepath = os.path.expanduser(thefile)
          with open(thepath) as f:
               theline = f.readline()
          thevalue = theline.strip('\n')
          return(thevalue)

      def create_thin_image(self,thefile,thesize):
          size_in_bytes = self.parse_size(thesize) - 512
          fd = os.open(thefile, os.O_RDWR+os.O_CREAT)
          os.lseek(fd,size_in_bytes,os.SEEK_SET)
          sector = bytearray(512)
          os.write(fd,sector)
          os.close(fd)

      def namespace(self,thename,thefile,thesize):
          subsystem = self.read('~/.nvmetarget/subsystem')
          if len(thename) == 0:
             if not os.path.isfile('/etc/nvmetarget.namespace'):
                self.echo('1','/etc/nvmetarget.namespace')
             thename = self.read('/etc/nvmetarget.namespace')
             nextname = int(thename) + 1
             self.echo(str(nextname),'/etc/nvmetarget.namespace')
          print("namespace: " + thename)
          self.echo(thename,'~/.nvmetarget/namespace')
          namespacepath = '/sys/kernel/config/nvmet/subsystems/' + subsystem + '/namespaces/' + thename
          if not os.path.isdir(namespacepath):
             print("Making namespace: " + namespacepath)
             os.mkdir(namespacepath)
          device = self.get_loop_device()
          print("Device: " + device)
          if not os.path.exists(thefile):
             self.create_thin_image(thefile,thesize)
          cmd = 'losetup ' + device + ' ' + thefile
          result = self.run_command(cmd)
          device = result.strip('\n')
          self.echo(device,namespacepath + '/device_path')
          self.echo('1',   namespacepath + '/enable')
          portpath = '/sys/kernel/config/nvmet/ports/1'
          # Only one port per subsystem and in our case per system
          if not os.path.isdir(portpath):
             os.mkdir(portpath)
             self.echo('ipv4', portpath + '/addr_adrfam')
             self.echo('tcp' , portpath + '/addr_trtype')
             self.echo('4420', portpath + '/addr_trsvcid')
             self.echo(self.ip,portpath + '/addr_traddr')
             subsystem_path = '/sys/kernel/config/nvmet/subsystems/' + subsystem + '/'
             port_path      = portpath + '/subsystems/' + subsystem
             # ln -s /sys/kernel/config/nvmet/subsystems/mysub/ /sys/kernel/config/nvmet/ports/1/subsystems/mysub
             os.symlink(subsystem_path,port_path)
          theitem  = {"namespace": thename, "subsystem": subsystem, "device": device, "file": thefile, "size": thesize, "active": "True"}
          try:
             data =  self.target_db.getBy({"namespace":thename})
             print("Existing: " + data)
          except:
             item_id = self.target_db.add(theitem)
             print("Item id: " + str(item_id))
             return
          print(data)
          self.target_db.updateById(data.id, new_data=theitem)
         
      def create_device(self,thefile,thesize):
          if not os.path.exists(thefile):
             create_thin_image(thefile,thesize)
          thedevice = self.get_loop_device()
          

      def subsystem(self,thename):
          subpath = "/sys/kernel/config/nvmet/subsystems/" + thename
          if os.path.isdir(subpath):
             self.echo(thename,'~/.nvmetarget/subsystem')
             return
          os.mkdir(subpath)
          self.echo('1',subpath + '/attr_allow_any_host')
          self.echo(thename,'~/.nvmetarget/subsystem')

             
          


