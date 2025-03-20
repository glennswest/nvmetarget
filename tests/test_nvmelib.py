#from nvmetarget.nvmelib import NvmeTarget
from nvmetarget import nvmelib
#from nvmetarget.nvmelib import NvmeTarget
symbols = dir()
print(symbols)

x = nvmelib.NvmeTarget()
x.subsystem('storage')

