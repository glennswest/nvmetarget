#from nvmetarget.nvmelib import NvmeTarget
from nvmetarget import nvmelib
#from nvmetarget.nvmelib import NvmeTarget

x = nvmelib.NvmeTarget()
data = x.targets()
print(data)
