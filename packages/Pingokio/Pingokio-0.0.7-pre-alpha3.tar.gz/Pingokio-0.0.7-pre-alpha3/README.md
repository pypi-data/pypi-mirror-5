pingokio
--------
Pingokio is a server that collect you sites uptime statistic by sending post or get requests periodically.


STATUS
--------
In-development


INSTALLATION
--------
pip install pingokio  
pingokio init
pingokio syncdb --all  
pingokio migrate --fake  


USAGE
--------
pingokio runserver 0.0.0.0:8000  
pingokio celeryd -B  
(You should run both command in different terminals.)  
Now you can access configuration interface by address http://127.0.0.1:8000/  
