#from nvmetarget.nvmelib import NvmeTarget
from nvmetarget import nvmelib
#from nvmetarget.nvmelib import NvmeTarget
symbols = dir()
print(symbols)

x = nvmelib.NvmeTarget()
for drive in range(1,20):
   thedrive = str(drive)
   x.subsystem('storage' + thedrive)
   x.namespace(thedrive,'tests/drives/test' + thedrive + '.img','10 MB')
