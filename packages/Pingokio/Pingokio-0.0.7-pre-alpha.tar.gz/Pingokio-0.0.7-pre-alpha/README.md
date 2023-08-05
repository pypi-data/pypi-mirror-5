pingokio
--------
You site uptime statistic collector


STATUS
--------
In-development


INSTALLATION
--------
pip install pingokio  
pingokio syncdb --all  
pingokio migrate --fake  


USAGE
--------
pingokio runserver 0.0.0.0:8000  
pingokio celeryd -B  
(You should run both command in different terminals.)  
Now you can access configuration interface by address http://127.0.0.1:8000/  
