import pandas as pd

class QueriesGenerator:
    def __init__(self, file_name):
        self.file_name = file_name
    
    def __get_query_lines(self):
        return open(self.file_name).read().split('\n')
        
    def number_of_queries(self):
        queries = self.__get_query_lines()
        return len(list(filter(lambda x:x.startswith('--'), queries)))
    
    def specific_query(self, query_num):
        queries = self.__get_query_lines()
        queries = list(filter(lambda x:len(x)!=0, queries))
        queries = list(map(lambda x:x.replace('\t',''), queries))
        queries = pd.DataFrame(queries, columns=['rows'])
        
        ind = queries[queries["rows"].str.slice(stop=2)=='--'].index
        ind = pd.DataFrame(ind, columns=["positions"], index=range(1,len(ind)+1))
        
        if query_num<len(ind):
            specific_query = queries[ind.loc[query_num, "positions"]+1:ind.loc[query_num+1,"positions"]]
        elif query_num==len(ind):
            specific_query = queries[ind.loc[query_num, "positions"]+1:]
        else:
            raise ValueError('Invalid query number')
        
        return ' '.join(list(specific_query.rows))