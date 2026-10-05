

from database.interface import Restore
from database.interface import Backup

from ..config import 
class postgres(Backup,Restore):
    
    def __init__(self,host,port,user,password,dbname):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.conn = None