#!/usr/bin/env python
## Insprired by:
##https://jing.rocks/2023/06/13/Experimenting-with-NVMe-over-TCP.html

import os
import subprocess
from pysondb import getDb
import socket


class NvmeTarget:
      def get_ip():
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
          print("Init Starting")
          os.system("modprobe nvmet_tcp")
          os.makedirs('~/.nvmetarget',exist_ok=True)
          target_db = getDb('/etc/nvmetarget.json')
          self.ip = get_ip()

      def run_command(command):
          process = subprocess.run(command, shell=True, capture_output=True, text=True)
          return process.stdout

      def get_loop_device():
          thedevice = self.run_command("losetup -f")
          return(thedevice)

      def bytesto(bytes, to, bsize=1024): 
          a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
          r = float(bytes)
          return bytes / (bsize ** a[to])

      def echo(thevalue, thefile):
          with open(thefile, "w") as text_file:
              text_file.write(thevalue)

      def read(thefile):
          with open(thefile) as f:
               thevalue = f.readline().strip('\n')
          return(thevalue)

      def create_thin_image(thefile,thesize):
          size_in_bytes = self.bytresto(thesize) - 512
          fd = os.open(thefile, os.O_RDWR+os.O_CREAT)
          os.lseek(fd,size_in_bytes,os.SEEK_SET)
          os.write(fd,zfill(512))
          os.close(fd)

      def namespace(thename,thefile,thesize):
          subsystem = self.read('~/.nvmetarget/subsystem')
          if len(thename):
             if not os.path.isfile('/etc/nvmetarget.namespace'):
                self.echo('1','/etc/nvmetarget.namespace')
             thename = self.read('/etc/nvmetarget.namespace')
             nextname = int(thename) + 1
             self.echo(str(nextname),'/etc/nvmetarget.namespace')
          self.echo(thename,'~/.nvmetarget/namespace')
          namespacepath = '/sys/kernel/config/nvmet/subsystems/' + subsystem + '/' + thename
          if not os.path.isdir(subpath):
             os.mkdir(namespacepath)
          device = self.get_loop_device()
          if not os.path.exists(thefile):
             create_thin_image(thefile,thesize)
          cmd = 'losetup ' + device + ' ' + thefile
          result = self.run_command(cmd)
          self.echo(device,namespacepath + '/' + thename + '/device_path')
          self.echo('1',   namespacepath + '/' + thename + '/enable')
          portpath = '/sys/kernel/config/nvmet/ports/1'
          if not os.path.isdir(portpath):
             os.mkdir(portpath)
             self.echo('ipv4', portpath + '/addr_adrfam')
             self.echo('tcp' , portpath + '/addr_trtype')
             self.echo('4420', portpath + '/addr_trsvcid')
             self.echo(self.ip,portpath + '/addr_traddr')
          subsystem_path = '/sys/kenrel/config/nvmet/subsystems/' + subsystem + '/'
          port_path      = portpath + 'subsystems/' + subsystem
          # ln -s /sys/kernel/config/nvmet/subsystems/mysub/ /sys/kernel/config/nvmet/ports/1/subsystems/mysub
          os.symlink(subsystem_path,port_path)
          theitem  = {"id": thename, "subsystem": subsystem, "device": device, "file": thefile, "size": thesize, "active": "True"}
          try:
             data =  self.target_db.getById(thename)
          except:
             item_id = self.target_db.add(theitem)
             print("Item id: " + item_id)
             return
          self.target_db.updateById(data.id, new_data=theitem)
         
      def create_device(thefile,thesize):
          if not os.path.exists(thefile):
             create_thin_image(thefile,thesize)
          thedevice = self.get_loop_device()
          

      def subsystem(thename):
          subpath = "/sys/kernel/config/nvmet/subsystems/" + thename
          if os.path.isdir(subpath):
             echo(thename,'~/.nvmetarget/subsystem')
             return
          os.mkdir(subpath)
          echo('1',subpath + '/attr_allow_any_host')
          echo(thename,'~/.nvmetarget/subsystem')

             
          


