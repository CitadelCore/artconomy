#!/bin/bash
source /home/dev/.bashrc
#apt-get install node npm
#npm run build
su dev
/usr/bin/python3.8 -m pip install -r requirements.txt
if [[ ! -d node_modules ]]
   then
   cp -a /root/node_modules /app/
fi
./manage.py migrate
npm run serve &
./manage.py collectstatic -v0 --noinput
./manage.py tg_bot &
exec "$@"
