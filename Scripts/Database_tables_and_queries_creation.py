import pandas as pd
import sqlite3 as sql
import glob
import os
from Getting_specific_query import QueriesGenerator

class DatabaseMethods:
    def __init__(self, databaseName):
        self.databaseName = databaseName
    
    def createDB(self):
        conn = sql.connect(self.databaseName)
        print(f'\n{self.databaseName} database created')
        conn.commit()
        conn.close()
    
    def execute_query(self, conn, query):
        conn = sql.connect(self.databaseName)
        cursor = conn.cursor()
        for row in cursor.execute(query):
            print(row)
        print('')
        conn.close()
    
    def __insert_df_as_table(self, df, tableName):
        dtypes = []
        for i, j in zip(df.columns, df.dtypes):
            if (j=='object' or j=='bool') and i!='startTime':
                dtypes.append('text')
            elif j=='int64':
                dtypes.append('integer')
            elif j=='float64':
                dtypes.append('numeric')
            else:
                dtypes.append('numeric')
        
        structure = pd.DataFrame({'columns': df.columns, 'dtypes': dtypes})
        columns_def = ''
        for k, row in structure.iterrows():
            columns_def += f'{row["columns"]} {row["dtypes"]}'
            if k!= len(structure) - 1:
                columns_def += ',\n' 
                
        sql_query = f"""  
            DROP TABLE IF EXISTS {tableName};\n
            CREATE TABLE {tableName}(
                \n'{columns_def}'   
            );
        """
        
        conn = sql.connect(self.databaseName)
        cursor = conn.cursor()
        cursor.executescript(sql_query)
        df.to_sql(tableName, conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()

    def create_all_tables(self, pathFile):
        ext = '.xlsx'
        excel_files = glob.glob(os.path.join(pathFile, f'*{ext}'))    
        print('')
        for i in excel_files:
            name = f'{i[len(pathFile):len(i)-len(ext)]}'
            self.__insert_df_as_table(pd.read_excel(i), name)
            print(f'{name} table created')
    
class QueriesCreation:
    def __init__(self, databaseName):
        self.databaseName = databaseName
    
    def __generate_df(self, fileName, query):
        conn = sql.connect(self.databaseName)
        df = pd.read_sql_query(query, conn)
        df.to_excel(fileName, index=False)
        conn.close()
    
    def create_views_files(self, file, outputPath):
        print('')
        query = QueriesGenerator(file)
        for i in range(1, query.number_of_queries()+1):
            outFileName = f'{outputPath}query_{i}.xlsx'
            self.__generate_df(outFileName, query.specific_query(i))
            print(f'query_{i} generated!')