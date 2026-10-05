from abc import ABC,abstractmethod
from config.settings import DatabaseConfig

class DatabaseAdapter(ABC):

    def __init__(self,config:DatabaseConfig=None):
        self.config=config
        if(self.config and isinstance(self.config,DatabaseConfig)):
            self.__setup()
        else:
            raise ValueError("Invalid database configuration")
        
    def __setup(self):
        pass

    @abstractmethod
    def test_connection(self,*args,**kwargs):
        """test the connection to the database"""
        pass
    @abstractmethod
    def dump_full_data(self,*args,**kwargs):
        """dump the schema of the database"""
        pass
    @abstractmethod
    def dump_incremental_data(self,*args,**kwargs):
        """dump the schema of the database"""
        pass
    @abstractmethod
    def dump_differential_data(self,*args,**kwargs):
        """dump the schema of the database"""
        pass
    @abstractmethod
    def restore_backup(self,*args,**k   wargs):
        """restore the schema of the database"""
        pass
    @abstractmethod
    def get_db_info(self,*args,**kwargs):
        """get the schema of the database"""
        pass
    

