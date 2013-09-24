set -eux

BDEVICE=/dev/sdb

# Mount filesystem
mkdir -p /mnt/ubuntu
mount "${BDEVICE}1" /mnt/ubuntu

echo "[COLLECTED INFORMATION BEGIN]"
echo "# INSTALL STANDARD OUTPUT"
cat /mnt/ubuntu/root/install.stdout
echo "# INSTALL STANDARD ERROR"
cat /mnt/ubuntu/root/install.stderr
echo "# INSTALL LOG"
cat /mnt/ubuntu/root/install.log
echo "[COLLECTED INFORMATION END]"

rm -f /mnt/ubuntu/etc/init/install.conf
rm -f /mnt/ubuntu/root/data.blob
rm -f /mnt/ubuntu/root/install.stdout
rm -f /mnt/ubuntu/root/install.stderr
rm -f /mnt/ubuntu/root/install.log
rm -f /mnt/ubuntu/root/install.sh

while mount | grep "/mnt/ubuntu"; do
    umount /mnt/ubuntu | true
    sleep 1
done
