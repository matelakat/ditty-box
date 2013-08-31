ditty-box
=========

Some fabric tasks and other utilities

## ESXi disk toggler

If you have a controller vm, you can attach-detach the guest VM's only disk to
it with:

    python esxi-toggle-disk.py <ESXI HOST> <PASSWORD> <GUEST VM> <CONTROLER VM>
