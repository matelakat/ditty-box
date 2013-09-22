set -eux

BDEVICE=/dev/sdb

# Mount filesystem
mkdir -p /mnt/ubuntu
mount "${BDEVICE}1" /mnt/ubuntu

cat > /mnt/ubuntu/root/install.sh << EOF
echo "this is stdout"
echo "this is stderr" >&2
EOF

cat > /mnt/ubuntu/etc/init/test.conf << EOF
start on runlevel [2345]

task

script
    echo "install started" >> /root/install.log
    /bin/bash /root/install.sh </dev/null >/root/install.stdout 2>/root/install.stderr
    halt -p
    echo "install finished" >> /root/install.log
end script
EOF

while mount | grep "/mnt/ubuntu"; do
    umount /mnt/ubuntu | true
    sleep 1
done
