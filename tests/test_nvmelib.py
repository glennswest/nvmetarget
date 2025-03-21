#from nvmetarget.nvmelib import NvmeTarget
from nvmetarget import nvmelib
#from nvmetarget.nvmelib import NvmeTarget
symbols = dir()
print(symbols)

x = nvmelib.NvmeTarget()
x.subsystem('storage')
x.namespace('1','test1.img','10 MB')
x.namespace('2','test2.img','5 MB')

