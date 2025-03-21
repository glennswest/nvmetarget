./build.sh
rm /etc/nvmetarget.json
rm /sys/kernel/config/nvmet/ports/1/subsystems/storage
rmdir /sys/kernel/config/nvmet/ports/1
rmdir /sys/kernel/config/nvmet/subsystems/storage/namespaces/*
rmdir /sys/kernel/config/nvmet/subsystems/*
losetup -d /dev/loop0
python tests/test_nvmelib.py 
nvme discover --transport=tcp --traddr=192.168.1.51  --trsvcid=4420


