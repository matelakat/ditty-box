from fabric.api import run, sudo, put, get
import StringIO


def _passwd_entry_for(username):
    passwds = run('cat /etc/passwd')
    for line in passwds.split():
        if line.startswith(username):
            return line

def _user_exists(username):
    return bool(_passwd_entry_for(username))


def _get_home_directory(username):
    return _passwd_entry_for(username).split(':')[5]


def _set_authorized_keys(username, pubkey):
    home = _get_home_directory(username)

    sudo('test -d %s' % home)
    sshdir = '%s/.ssh' % home
    authorized_keys = '%s/authorized_keys' % sshdir

    sudo('mkdir -p %s' % sshdir)
    put(pubkey, authorized_keys, use_sudo=True)
    sudo('chown -R %s:%s %s' % (username, username, sshdir))
    sudo('chmod 0700 %s' % sshdir)
    sudo('chmod 0600 %s' % authorized_keys)


def _get_contents_of(filename):
    f = StringIO.StringIO()
    get(filename, f)
    return f.getvalue()


def _add_user_to_allow_users(sshd_config, username):
    lines = []
    for line in sshd_config.split('\n'):
        new_line = line
        if line.startswith('AllowUsers'):
            users = line.strip().split()[1:]
            if username not in users:
                users.append(username)
            new_line = 'AllowUsers ' + ' '.join(users)

        lines.append(new_line)

    return '\n'.join(lines)


def _allow_user(username):
    filename = '/etc/ssh/sshd_config'
    sshd_config = _get_contents_of(filename)
    new_config = _add_user_to_allow_users(sshd_config, username)
    new_sshd_config = StringIO.StringIO(new_config)
    put(new_sshd_config, filename, use_sudo=True)
    sudo('service ssh restart')


def _enable_rsync(username):
    rule = "%s ALL = NOPASSWD: /usr/bin/rsync\n" % username
    remote_rule_filename = '/etc/sudoers.d/rsync_%s' % username

    temp_filename = run('mktemp')
    local_rule_file = StringIO.StringIO(rule)
    put(local_rule_file, temp_filename, use_sudo=True)

    sudo('chown root:root %s' % temp_filename)
    sudo('chmod 0440 %s' % temp_filename)
    sudo('mv %s %s' % (temp_filename, remote_rule_filename))


def _assert_installed(package_name):
    sudo('apt-get install -qy %s' % package_name)


def _setup_backup_user(username, pubkey):
    if not _user_exists(username):
        sudo('useradd -m -r %s' % username)
    _set_authorized_keys(username, pubkey)
    _allow_user(username)
    _enable_rsync(username)
    _assert_installed('rsync')


def ping():
    sudo('ls -la')


def setup_backup():
    _setup_backup_user('remotebackup', 'backup/backupkey.pub')
