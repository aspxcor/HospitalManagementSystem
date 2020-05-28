DIALECT = 'mysql'
DRIVER = 'mysqlconnector'
USERNAME = 'root'
# PASSWORD = '123456789Aa'
# HOST = '119.3.234.133'    #这是云服务器公网IP，现在这个公网IP已经释放，所以此版本代码中仍然连接本地数据库
PASSWORD = '123456'
HOST = '127.0.0.1'  #连接本地服务器
PORT = '3306'
DATABASE = 'hospital'
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT,
                                                                       DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = True
SECRET_KEY = "random string"