ditty-box
=========

Useful utilities for system administration

## Install

    python setup.py install

## ESXi Scripts

 - List vms: `esxi-list-vms`
 - Toggle disk: `esxi-toggle-disk`

## Other

Unplug disk from ESXi guest:

    echo "1" > /sys/block/sdb/device/delete

Plug to ESXi guest:

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
