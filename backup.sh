#!/bin/bash

set -eux

function backup_host() {
    local ssh_config
    local hostip
    local target_dir
    local previous_backup_dir

    ssh_config="$1"
    hostip="$2"
    target_dir="$3"
    previous_backup_dir="$4"

    local link_dest_param

    mkdir -p "$target_dir"

    if [ -z "$previous_backup_dir" ]; then
        link_dest_param=""
    else
        link_dest_param="--link-dest=$previous_backup_dir"
    fi

    rsync -e "ssh -F $ssh_config" --rsync-path="sudo rsync" \
      -v -r -H -l -g -o -t -D -p --del $link_dest_param \
      --exclude={/dev/*,/proc/*,/sys/*,/tmp/*,/run/*,/mnt/*,/media/*,/lost+found} \
      $hostip:/ "$target_dir"
}

function tunnel_create() {
    local ssh_config

    ssh_config="$1"

    ssh -q -N -f -F "$ssh_config" ssh-gateway
}

function tunnel_delete() {
    tunnel_pid=$(/usr/sbin/lsof -i 4:9797 -Fp | tr -d "p")
    [ ! -z "$tunnel_pid" ]
    kill $tunnel_pid
}

function generate_tunneling_ssh_config() {
    local ssh_gateway
    local identity_file
    local hosts_file
    local gateway_user
    local backup_user
    local hosts
    local ssh_config

    ssh_gateway="$1"
    identity_file="$2"
    hosts_file="$3"
    gateway_user="$4"
    backup_user="$5"
    hosts="$6"
    ssh_config="$7"

cat > "$ssh_config" << EOF
UserKnownHostsFile $hosts_file

# Set to yes for the daemon, ask for interactive
StrictHostKeyChecking yes
# Set to yes for the daemon, no for interactive
BatchMode yes

Host ssh-gateway
Compression no
ExitOnForwardFailure yes
ForwardAgent no
IdentityFile $identity_file
Cipher blowfish
KeepAlive yes
ServerAliveInterval 15
User $gateway_user
DynamicForward localhost:9797
HostName $ssh_gateway


Host $hosts
ProxyCommand nc -x localhost:9797 %h %p
IdentityFile $identity_file
User $backup_user
EOF
}

function backup_hosts() {
    local ssh_config
    local hosts
    local target_dir
    local previous_backup_dir

    ssh_config="$1"
    hosts="$2"
    target_dir="$3"
    previous_backup_dir="$4"

    local previous_backup_param


    for host in $hosts;
    do
        if [ -z "$previous_backup_dir" ]; then
            previous_backup_param=""
        else
            previous_backup_param="$previous_backup_dir/$host"
        fi
        backup_host \
          "$ssh_config" "$host" "$target_dir/$host" "$previous_backup_param"
    done
}

function backup_hosts_through_tunnel() {
    local ssh_gateway
    local identity_file
    local hosts_file
    local gateway_user
    local backup_user
    local ssh_config

    local hosts
    local target_dir
    local previous_backup_dir

    ssh_gateway="$1"
    identity_file="$2"
    hosts_file="$3"
    gateway_user="$4"
    backup_user="$5"
    ssh_config="$6"
    hosts="$7"
    target_dir="$8"
    previous_backup_dir="$9"

    generate_tunneling_ssh_config \
        "$ssh_gateway" "$identity_file" "$hosts_file" \
        "$gateway_user" "$backup_user" "$hosts" "$ssh_config"

    tunnel_create "$ssh_config"

    backup_hosts "$ssh_config" "$hosts" "$target_dir" "$previous_backup_dir"

    tunnel_delete
}
