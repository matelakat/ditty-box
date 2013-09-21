ditty-box
=========

Some fabric tasks and other utilities

## Install

    python setup.py install

## Scripts

### ESXi related
List your VMs:

    esxi-list-vms --help

## ESXi disk toggler

If you have a controller vm, you can attach-detach the guest VM's only disk to
it with:

    python esxi-toggle-disk.py <ESXI HOST> <PASSWORD> <GUEST VM> <CONTROLER VM>

Unplug:

    echo "1" > /sys/block/sdb/device/delete

Plug:

    echo "- - -" > /sys/class/scsi_host/host2/scan

Build uwsgi:

    wget http://projects.unbit.it/downloads/uwsgi-1.9.15.tar.gz
    tar -xzf uwsgi-1.9.15.tar.gz
    cd uwsgi-1.9.15
    make
    sudo mkdir -p /opt/uwsgi
    sudo mv uwsgi /opt/uwsgi/
    cd ..
    rm -rf uwsgi-1.9.15
    sudo chown -R root:root /opt/uwsgi
    sudo chmod -R g-w,o-w /opt/uwsgi

An example upstart job for `uwsgi`:

    setgid nogroup
    setuid psrv

    start on runlevel [2345]
    stop on runlevel [016]

    chdir /home/psrv/apps/et/root

    script
        /opt/uwsgi/uwsgi --master --die-on-term --ini-paste /home/psrv/apps/et/root/conf/et.ini
    end script
