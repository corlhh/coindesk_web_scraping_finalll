from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

class Article_database():

    def __init__(self,db_user,db_password,db_name,db_host='localhost',\
                    port=3306,use_unicode=True,charset="utf8"):

        self.db_host = db_host
        self.db_user = db_user
        self.db_password= db_password
        self.db_name = db_name
        self.port = port
        self.use_unicode = use_unicode
        self.charset = charset
        self.database_config = {
            'host':db_host, 
            'user':db_user, 
            'password':db_password,
            'port':port,
            'use_unicode':use_unicode,
            'charset':charset,}

        self.Mysql_instance = self.connect_to_Mysql_and_return_the_instance()
        print ("Connected to the Database successfully.")
        self.db_cursor = self.Mysql_instance.cursor(buffered=True)
        print ("Cursor Created.","Starting to connect the Database ...",sep="\n")
        self.connect_to_database()  # cursor will be set to the database
        print ("Successful connected to database: %s ; %s @ %s"%(self.db_name,self.db_user,self.db_host))
        print ("Initialisation Complete.")

    def __del__ (self):
        self.db_cursor.close()
        self.Mysql_instance.close()
        print ("Destructor invoked: Mysql_instance and db_cursor closed")

    def connect_to_Mysql_and_return_the_instance(self):
        try:
            self.cnx = mysql.connector.connect(**self.database_config)
            
        except mysql.connector.Error as err:
            #handle connection errors
            print ("Error code:", err.errno)        # error number
            print ("SQLSTATE value:", err.sqlstate) # SQLSTATE value
            print ("Error message:", err.msg)       # error message
            print ("Error:", err)                   # errno, sqlstate, msg values
            raise Exception(str(err))  
        else:
            return self.cnx


    def connect_to_database(self):
        try:
            self.Mysql_instance.database = self.db_name #Try to connect to the specified database
        except mysql.connector.Error as err:   #Exception Handling
            if err.errno == errorcode.ER_BAD_DB_ERROR: #If the database  does not exist
                try:
                    print ("Database does not exist. The system will create a new database ...")
                    self.create_new_database()
                    self.Mysql_instance.database = self.db_name
                    self.create_all_tables()
                except:
                    raise
            else:
                raise
        else:
            self.create_all_tables()
        
            
        

    def create_new_database(self):
        try:
            #Create a database
            self.db_cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.db_name))
        except mysql.connector.Error as err: #Exception Handling
            raise Exception("Failed creating database: {}".format(err))
        else:
            print ("Database '{}' created successfully".format(self.db_name), end='\n')
            try:
                self.Mysql_instance.database = self.db_name
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_BAD_DB_ERROR:
                    self.create_new_database(self)
                    self.Mysql_instance.database = self.db_name
                else:
                    print(err)

    def create_all_tables(self):

        self.db_cursor.execute("SET foreign_key_checks=0")
        self.TABLES = {}
        self.TABLES['sources'] = (
            "CREATE TABLE `sources` ("
            "  `id` INT NOT NULL AUTO_INCREMENT,"
            "  `website_name` VARCHAR(45) NULL,"
            "  `website_url` VARCHAR(45) NULL,"
            "  PRIMARY KEY (`id`)"
            ") ENGINE=InnoDB")



        self.TABLES['articles'] = (
            "CREATE TABLE `articles` ("
            "  `article_id` INT NOT NULL AUTO_INCREMENT,"
            "  `source` VARCHAR(45) NULL,"
            "  `title` VARCHAR(200) NULL,"
            "  `written_time` DATETIME NULL,"
            "  `author` VARCHAR(100) NULL,"
            "  `article_url` VARCHAR(500) NOT NULL,"
            "  `content` LONGTEXT NULL,"
            "  `collection_time` DATETIME NULL,"
            "  PRIMARY KEY (`article_id`),"
            "  FOREIGN KEY (`article_id`)"
            "  REFERENCES `sources`(`id`)"
            "  ON DELETE CASCADE"
            ") ENGINE=InnoDB")

        self.create_each_table(self.TABLES)


    def create_each_table(self, DICT_tables):
        
        #self.db_cursor.execute("SET GLOBAL innodb_file_per_table=1")
        #self.db_cursor.execute("SET GLOBAL innodb_file_format=Barracuda")
        
        for table_key in DICT_tables:
            try:
                self.db_cursor.execute(self.TABLES[table_key])
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("Table {} already exists.".format(table_key))
                else:
                    print("Creating Table {} Failed: ".format(table_key), err.msg)
            else:
                print("Table {} Created.".format(table_key))


    def insert_article_into_articles(self, data):
        insertion_format = ("INSERT INTO articles (source, title, written_time, author, article_url, content, collection_time)"
                "VALUES (%s,%s,%s,%s,%s,%s,%s)")
        
        self.db_cursor.execute(insertion_format, data)
        self.Mysql_instance.commit()

    def insert_source_into_sources(self, data):
        insertion_format = ("INSERT INTO sources (website_name, website_url)"
                "VALUES (%s,%s)")
        self.db_cursor.execute(insertion_format, data)
        self.Mysql_instance.commit()

        
    def article_url_exists_in_table(self, data):
        select_format = ("SELECT COUNT(1) FROM articles WHERE article_url = %s")
        self.db_cursor.execute(select_format, (data,))
        return self.db_cursor.fetchone()[0]

    def source_information_exists_in_table(self, data):
        select_format = ("SELECT COUNT(1) FROM sources WHERE website_url = %s")
        self.db_cursor.execute(select_format, (data,))
        return self.db_cursor.fetchone()[0]

