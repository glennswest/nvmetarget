#from nvmetarget.nvmelib import NvmeTarget
from nvmetarget import nvmelib
#from nvmetarget.nvmelib import NvmeTarget
symbols = dir()
print(symbols)

x = nvmelib.NvmeTarget()
x.subsystem('storage')
for drive in range(1,20):
   thedrive = str(drive)
   x.namespace(thedrive,'test' + thedrive + '.img','10 MB')
