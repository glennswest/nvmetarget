rm /etc/nvmetarget.json
rm /sys/kernel/config/nvmet/ports/1/subsystems/storage
rmdir /sys/kernel/config/nvmet/ports/1
rmdir /sys/kernel/config/nvmet/subsystems/storage/namespaces/*
rmdir /sys/kernel/config/nvmet/subsystems/*
