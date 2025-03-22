nvme discover --transport=tcp --traddr=192.168.1.51  --trsvcid=4420
modprobe nvme-tcp
nvme connect -t tcp -a 192.168.1.51 -s 4420 -n storage
nvme list



