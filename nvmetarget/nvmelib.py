#!/usr/bin/env python
## Insprired by:
##https://jing.rocks/2023/06/13/Experimenting-with-NVMe-over-TCP.html

import os
from pysondb import getDb


class NvmeTarget
      def __init__(self)
          os.system("modprobe nvmet_tcp")
          os.makedirs('~/.nvmetarget',exist_ok=True)
          target_db = getDb('/etc/nvmetarget.json')

      def bytesto(bytes, to, bsize=1024): 
          a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
          r = float(bytes)
          return bytes / (bsize ** a[to])

      def echo(thevalue, thefile)
          with open(thefile, "w") as text_file:
              text_file.write(thevalue)

      def read(thefile)
          with open(thefile) as f:
               thevalue = f.readline().strip('\n')
          return(thevalue)

      def create_thin_image(thefile,thesize)
          size_in_bytes = self.bytresto(thesize) - 512
          fd = os.open(thefile, os.O_RDWR+os.O_CREAT)
          os.lseek(fd,size_in_bytes,os.SEEK_SET)
          os.write(fd,zfill(512))
	  os.close(fd)

      def create_device(thefile,thesize)
          if not os.path.exists(thefile)
             create_thin_image(thefile,thesize)
          

      def subsystem(thename)
          subpath = "/sys/kernel/config/nvmet/subsystems/" + thename
          if os.path.isdir(subpath):
             echo(thename,'~/.nvmetarget/subsystem')
             return
          os.mkdir(subpath)
          echo('1',subpath + '/attr_allow_any_host')
	  echo(thename,'~/.nvmetarget/subsystem)

             
          


