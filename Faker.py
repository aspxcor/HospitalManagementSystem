# 本程序是Faker库为MIMIC数据库生成患者姓名所用的代码
import pymysql
from faker import Faker
#使用的是mysql5.5
conn=pymysql.connect(host="localhost",port=3306,user="root",password="123456",db="hospital",charset="utf8")
cursor=conn.cursor()
#这里给出表结构，如果使用已存在的表，可以不创建表。
fake=Faker("zh-CN")
for i in range(1952):
    sql="""update patients set name= '%s' where id = """ %(fake.name(),) + str(i) 
    cursor.execute(sql)

conn.commit()
cursor.close()
conn.close()