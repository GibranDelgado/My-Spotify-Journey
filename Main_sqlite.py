import sys
import os

if __name__ ==  '__main__':
    path = os.path.dirname(os.path.abspath('Main_sqlite.py'))+'\\'
    sys.path.insert(0, os.path.join(os.path.dirname(sys.path[0]), f"{path}Scripts"))
    
    import Database_tables_and_queries_creation as DTAQC
    
    db = f'{path}Used_files\\Spotify_analysis.db'
    inputPath = f'{path}Spotify_results\\'
    outputPath = f'{path}Queries_results\\'
    
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
        
    fileName = f'{path}Used_files\\queries.txt'
    
    dbMethods = DTQC.DatabaseMethods(db)
    dbMethods.createDB()
    dbMethods.create_all_tables(inputPath)
    DTAQC.QueriesCreation(db).create_views_files(fileName, outputPath)