set -eux

BDEVICE=/dev/sdb
HNAME="guestmachine"
USERNAME="matelakat"
PASSWORD="somepass"

# Partition the disk
fdisk -c -u "$BDEVICE" << EOF
o
n
p
1

+4G
t
83
n
p
2


t
2
82
wq
EOF

# Ask kernel to re-load partitions
partprobe "$BDEVICE"

# Create filesystems
mkfs.ext3 "${BDEVICE}1"
mkswap "${BDEVICE}2"
sync

# Mount new filesystem
mkdir -p /mnt/ubuntu
mount "${BDEVICE}1" /mnt/ubuntu

# Perform debootstrap
RUNLEVEL=1 debootstrap \
     --arch=amd64 \
     --components=main,universe \
     --include=openssh-server,language-pack-en,linux-image-virtual,grub-pc,wget,make,gcc,linux-libc-dev,libc6-dev,python-dev,libpcre3-dev,libpq-dev,postgresql,ntp,python-virtualenv,python-pip,python-pkg-resources,python-setuptools \
     precise \
     /mnt/ubuntu \
     http://hu.archive.ubuntu.com/ubuntu/

# Configure networking
tee /mnt/ubuntu/etc/network/interfaces << EOF
auto lo
iface lo inet loopback
auto eth0
iface eth0 inet dhcp
EOF

# Configure NTP
tee /mnt/ubuntu/etc/ntp.conf << EOF
# Some things from default ubuntu install
driftfile /var/lib/ntp/ntp.drift
statistics loopstats peerstats clockstats
filegen loopstats file loopstats type day enable
filegen peerstats file peerstats type day enable
filegen clockstats file clockstats type day enable
restrict -4 default kod notrap nomodify nopeer noquery
restrict -6 default kod notrap nomodify nopeer noquery
restrict 127.0.0.1
restrict ::1

# ntp servers
server 0.hu.pool.ntp.org
server 1.hu.pool.ntp.org
server 2.hu.pool.ntp.org
server 3.hu.pool.ntp.org
EOF

# Configure SSH
sed -ie 's/#PasswordAuthentication yes/PasswordAuthentication no/g' /mnt/ubuntu/etc/ssh/sshd_config

# Configure hostname
echo "$HNAME" > /mnt/ubuntu/etc/hostname

# Configure hosts file, so that hostname could be resolved
sed -i "1 s/\$/ $HNAME/" /mnt/ubuntu/etc/hosts

# Configure fstab
tee /mnt/ubuntu/etc/fstab << EOF
proc /proc proc nodev,noexec,nosuid 0 0
UUID=$(blkid -s UUID ${BDEVICE}1 -o value) / ext3 errors=remount-ro 0 1
UUID=$(blkid -s UUID ${BDEVICE}2 -o value) none swap sw 0 0
EOF

# Install bootloader
mount --bind /dev /mnt/ubuntu/dev
mount --bind /proc /mnt/ubuntu/proc
mount --bind /sys /mnt/ubuntu/sys

LANG=C chroot /mnt/ubuntu /bin/bash -c \
    "grub-install /dev/sdb"

LANG=C chroot /mnt/ubuntu /bin/bash -c \
    "update-grub"

umount /mnt/ubuntu/sys
umount /mnt/ubuntu/proc
umount /mnt/ubuntu/dev

# Setup accounts
## Setup a real user account
LANG=C chroot /mnt/ubuntu /bin/bash -c \
    "DEBIAN_FRONTEND=noninteractive \
    adduser --disabled-password --quiet $USERNAME --gecos $USERNAME"

### Configure password
echo "$USERNAME:$PASSWORD" | LANG=C chroot /mnt/ubuntu chpasswd

### Configure ssh keys
LANG=C chroot /mnt/ubuntu /bin/bash -c \
    "mkdir /home/$USERNAME/.ssh && \
    cat - > /home/$USERNAME/.ssh/authorized_keys && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh && \
    chmod 0700 /home/$USERNAME/.ssh && \
    chmod 0600 /home/$USERNAME/.ssh/authorized_keys" << EOF
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC2wb6NF3vXcQdQz+zHVkQ4vsvlPzm9rQMPZcjnavn3VZPUu6tBcmvIYvj1PHVTIR+zqhvNPunC21WZ8h8ACQlTwzr8mD+rjJtYYmyVSMwJl2Nvr3L5jP/aKqGPvLm8YGsYTJG2vXOWPBlZx+/BX6evcTE/FZ7YruoLHy2A7EJ6SLmT2yVlrfsCwNwPv2UEGIDnR2SfmuUkqZ6TufHaSBGtC/LuBkdoTT9HOlICNitrnExiOGL70/16A1reO0z7Nx3OuegmZx3C6rZzuPr7/M4NjCmMHermCmKVaMJBJIV1W3hOFYGseYVXstyAhmVP0ecWLlQ7JIF+WJy7zJYgguQB matelakat@devserver
EOF

### Enable passwordless sudo
echo "$USERNAME ALL = (ALL) ALL" | tee "/mnt/ubuntu/etc/sudoers.d/allow_$USERNAME"
chmod 0440 "/mnt/ubuntu/etc/sudoers.d/allow_$USERNAME"

### Enable ssh access
tee -a /mnt/ubuntu/etc/ssh/sshd_config << EOF
AllowUsers $USERNAME
EOF

## Setup service account
LANG=C chroot /mnt/ubuntu /bin/bash -c \
    "DEBIAN_FRONTEND=noninteractive \
    adduser --system psrv"

while mount | grep "/mnt/ubuntu";
do
    umount /mnt/ubuntu | true
    sleep 1
done
