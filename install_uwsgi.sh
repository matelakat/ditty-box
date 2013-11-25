# 
# Install Script for an uwsgi based application
#
set -eux

DAEMON_NAME=uwsgi
APP_NAME=demoapp

# Refresh package list
apt-get update

# install prerequisites
apt-get -qy install wget make gcc linux-libc-dev libc6-dev python-dev libpcre3-dev python-virtualenv

# Install uwsgi
mkdir /root/tmp
cd /root/tmp
wget -q http://projects.unbit.it/downloads/uwsgi-1.9.15.tar.gz
tar -xzf uwsgi-1.9.15.tar.gz
cd uwsgi-1.9.15
make
mkdir -p /opt/uwsgi
mv uwsgi /opt/uwsgi/
cd ..
rm -rf uwsgi-1.9.15
chown -R root:root /opt/uwsgi
chmod -R g-w,o-w /opt/uwsgi
rm -rf /root/tmp

# Set permissions on uwsgi installation
chown -R root:nogroup /opt/uwsgi/
chmod -R g-w,o-w /opt/uwsgi

adduser --system $DAEMON_NAME

# Create directories for the application
mkdir -p /opt/$APP_NAME/logs
(
    cd /opt/$APP_NAME
    virtualenv --no-site-packages env
)

# Create upstart script for the application
cat > /etc/init/$APP_NAME.conf << EOF
setgid nogroup
setuid $DAEMON_NAME

start on runlevel [2345]
stop on runlevel [016]

chdir /opt/$APP_NAME/

script
    /opt/uwsgi/uwsgi \\
        --master \\
        --socket 0.0.0.0:3031 \\
        --die-on-term \\
        --processes 4 \\
        --virtualenv /opt/$APP_NAME/env \\
        --wsgi-file /opt/$APP_NAME/application.py \\
        --logto /opt/$APP_NAME/logs/uwsgi.log \\
        --stats 127.0.0.1:9191
end script
EOF

# A Hello world application
cat > /opt/$APP_NAME/application.py << EOF
def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return ["Hello World"]
EOF

# Configure logrotate
cat > /etc/logrotate.d/$APP_NAME << EOF
/opt/$APP_NAME/logs/uwsgi.log {
    compress
    size 1M
    copytruncate
    rotate 6
}
EOF

# Set permissions
chown -R root:nogroup /opt/$APP_NAME/
chmod -R g-w,o-w /opt/$APP_NAME/
chown -R $DAEMON_NAME:nogroup /opt/$APP_NAME/logs
chmod -R u+w,g-w,o-w /opt/$APP_NAME/logs

apt-get clean
