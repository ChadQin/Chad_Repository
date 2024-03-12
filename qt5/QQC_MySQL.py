import pymysql

class _QQCMySQL:

    def __init__(self):
        self.db = pymysql.connect(host="127.0.0.1",
                                  user="root",
                                  password="760533763",
                                  db="qqc",
                                  port=3306,
                                  charset='utf8'
                                  )

        self.cursor = self.db.cursor()

    def mysql_create_database(self,name):

        try:
            self.cursor.execute("CREATE database {}".format(name))
        except Exception as e:
            print(e)

    def mysql_show_databases(self):

        self.databases = []
        self.data = self.cursor.execute("SHOW DATABASES;")
        self.db.commit()
        for database in self.cursor:
            self.databases.append(database)
        return self.databases

    def mysql_show_tables(self):
        self.tables = []
        self.cursor.execute("SHOW TABLES")
        for table in self.cursor:
            self.tables.append(table)
        return self.tables

    def mysql_delete_table(self,table):
        self.cursor.execute("DROP TABLE {}".format(table))

    def mysql_show_column_header(self, table):
        self.cursor.execute("SELECT " + "*"  + " FROM {}".format(table))

        des = self.cursor.description
        self.column_header = ",".join([item[0] for item in des])
        self.column_header = self.column_header.split(',')
        return self.column_header

    def mysql_query(self, database):

        self.sql = """
            select * from {};
            """.format(database)

        self.cursor.execute(self.sql)
        self.content = self.cursor.fetchall()
        return self.content

    def mysql_insert(self, table_name, value):
        # str_columns = ','.join(columns)
        str_value = ','.join(value)
        try:
            self.cursor.execute("insert into {} values ({})".format(table_name, str_value))
        except Exception as e:
            print(e)
        self.db.commit()
        return self.cursor.rowcount

    def mysql_update(self, condition,condition_content,value_condition,value):
        self.cursor.execute("UPDATE student SET {} = '{}' where {} = '{}'".format(value_condition, value, condition, condition_content))
        self.db.commit()
        return self.cursor.rowcount

    def mysql_delete(self, table, condition, value):
        self.cursor.execute("DELETE FROM {} WHERE {} = '{}'".format(table, condition, value))
        self.db.commit()

    def mysql_modify_column_format(self, table, column, format):
        self.cursor.execute("ALTER TABLE {} MODIFY COLUMN {} {}".format(table, column, format))

    def mysql_test_sql(self, sentence):
        a= self.cursor.execute('{}'.format(sentence))
        return a

    def mysql_close(self):
        self.cursor.close()
        self.db.close()

