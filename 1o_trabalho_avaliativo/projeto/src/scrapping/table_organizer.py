import pandas as pd
import numpy as np
import re

class TableOrganizer():
    def __init__(self):
        pass
    
    def concatenate(self, table01: pd.DataFrame, table02: pd.DataFrame):
        return pd.DataFrame(np.concatenate((table01, table02), axis=0), columns=[table01.columns])

    def calc_ignition_iteraction(self, row: pd.Series) -> int:
        # calcular numero de iterações correspondentes da linha - referencia de iteração
    
        if row[1] is np.NAN:
            return 1
        else:
            return 0
        
    def calc_ignition_forming_row(self, row: pd.Series) -> int:    
        return row[1] is np.NAN
    
    def calc_ignition_func(self, row: pd.Series) -> str:
        if row[1] is np.NAN:
            return 'sum' 
        else:
            return  'sub'
        
    def regex(self, pattern: str, entry: str) -> list():
        return re.findall(pattern, entry)
    
    # percorrer linhas - recursão sobre cada linha da tabela arbitrária
    # normalizar contexto real das linhas
    # table não pode ser um dataframe vazio
    def normalize_table_rows(self, table : pd.DataFrame, iteration: int) -> dict():
        # obtenção dos dados no contexto da iteração atual
        row = table.iloc[iteration]
        
        print(type(row))
        print(row)
        
        # quebra profundidade da recursão (último elemento de iteração)
        if iteration >= (table.index.size - 1): 
            # avaliar linha para calcular a iteração antecedente
            return {'ref_iteration': self.calc_ignition_iteraction(row),
                    'forming_row': self.calc_ignition_forming_row(row),
                    'func': self.calc_ignition_func(row),
                    #'rows': [row]
                    'form_row':[[iteration]]
                    }
        
        # busca profunda
        #iteration += 1
        norm_row = self.normalize_table_rows(table, iteration+1)
        
        # ref_iteraction = norm_row['ref_iteraction']
        
        # normalização - contexto formador de linha
        if not norm_row['forming_row']:
            # before next, need to validade context to new row (func turn and ):
            if row[0] is np.NAN and row[1] is not np.NAN:
                norm_row['form_row'][-1].append(iteration)
                norm_row['forming_row'] = True
                norm_row['ref_iteration'] += 1
                norm_row['func'] = 'sub'
            else:
                norm_row['form_row'].append([iteration]) # bindin rows to a normal context row
                
                norm_row['ref_iteration'] = self.calc_ignition_iteraction(row)
                norm_row['func'] = self.calc_ignition_func(row)
                
                if norm_row['func'] == 'sum':
                    norm_row['forming_row'] = True 
                else:
                    match = self.regex(pattern='((0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/(\d{2}?\d{2}))', entry=row[-1])
                    
                    if len(match) <= 0:
                        # has no data? it's not a row, try merge other arbitrary row
                        norm_row['forming_row'] = True 
                # else : norm_row['forming_row'] = False 
            
            return norm_row;
        
        else: # norm_row['forming_row'] == True
            norm_row['form_row'][-1].append(iteration)
            
            # cria dependencia em referencia de iteração
            if row[1] is np.NAN:
                if norm_row['func'] == 'sum':
                    norm_row['ref_iteration'] += 1
                else: # norm_row['func'] == 'sub'
                    if norm_row['ref_iteration'] > 0:
                        norm_row['ref_iteration'] -= 1
                    
                    if norm_row['ref_iteration'] == 0:
                        norm_row['forming_row'] = False
            else:
                norm_row['func'] = 'sub'
                
                if norm_row['ref_iteration'] == 0:
                        norm_row['forming_row'] = False
                
            return norm_row

    def model_rows_to_df(self, table: pd.DataFrame, form_row: list(), columns: list()):
        rows = list()
        
        #size = len(model_rows['form_row'])
        for i in form_row[::-1]:
            #normal_table.loc[i, columns] = model_rows['form_row']
            
            atividade = ''
            data = ''
            for e in i[::-1]:
                print(e)
                context = [table.loc[e, columns]]
                
                print(context)
                for t1, t2 in context:
                    if t1 is not np.NAN:
                        atividade += t1 + ' '
                    if t2 is not np.NAN:
                        data += t2 + ' '
                
            print(atividade)
            print(data)
            rows.append([atividade, data])
            
        print(rows)    
        return pd.DataFrame(data=rows, columns=['atividade', 'data']) 
    
    def normalize_table_data(self, table: pd.DataFrame, resolve_columns:bool=False) -> pd.DataFrame:
        norm_table = table.dropna(axis='columns', how='all')
        norm_table = pd.DataFrame(norm_table.dropna(axis='rows', how='all'))
        
        print(type(norm_table))
        
        if resolve_columns:
            norm_table.columns = norm_table.loc[0]
            norm_table = norm_table.drop(index=0)
            norm_table = norm_table.reset_index(drop=True)
            
        return norm_table
        
if __name__ == '__main__':
    def test(table):
        aux_index = 0
        in_column = False
        for column in list(table.columns):
            print(column)
            
            if str(column).lower().__contains__('atividade'):
                in_column = True
                break
                
            aux_index += 1
        
        if not in_column:
            aux_index = 0
            
        print(table.columns[aux_index:])
    
    
    to = TableOrganizer()
    
    path_to_root = '.\\'
    dir = path_to_root + 'scrapping\csv_teste\\'
    
    path_file = {
    'path':[(dir+'0\\')],
    'file':[['0.csv', '1.csv']]
    }
    
    index_dir = 0
    index_file = 0
    read_file = path_file['path'][index_dir] + path_file['file'][index_dir][index_file]
    print(read_file)
    
    table01 = pd.read_csv(read_file, index_col=0)
    
    index_file = 1
    read_file = path_file['path'][index_dir] + path_file['file'][index_dir][index_file]
    print(read_file)
    
    table02 = pd.read_csv(read_file, index_col=0)
    
    table = to.concatenate(table01, table02)

    table = to.normalize_table_data(table, resolve_columns=False)

    model_rows = to.normalize_table_rows(table.loc[:, table.columns[1:]], 0)
    
    normal_table = to.model_rows_to_df(table=table, form_row=model_rows['form_row'], columns=list(table.columns[1:]))
    
    
    # other table
    path_file = {
    'path':[(dir+'1\\')],
    'file':[['1.csv']]
    }
    
    index_dir = 0
    index_file = 0
    read_file = path_file['path'][index_dir] + path_file['file'][index_dir][index_file]
    print(read_file)
    
    table03 = pd.read_csv(read_file, index_col=0)
    
    print('\n\n')
    test(table03)
    print(table03.loc[:, table03.columns[1:]])
    print(table03.columns[1:])
    
    table03 = to.normalize_table_data(table03.loc[:, table03.columns[1:]], True)
    
    model_rows02 = to.normalize_table_rows(table03.loc[:, table03.columns], 0)
    
    normal_table02 = to.model_rows_to_df(table=table03, form_row=model_rows02['form_row'], columns=list(table03.columns))
    
    
    
    # other table
    path_file = {
    'path':[(dir+'2\\')],
    'file':[['0.csv']]
    }
    
    index_dir = 0
    index_file = 0
    read_file = path_file['path'][index_dir] + path_file['file'][index_dir][index_file]
    print(read_file)
    
    table04 = pd.read_csv(read_file, index_col=0)
    
    table04 = to.normalize_table_data(table04, False)
    
    model_rows03 = to.normalize_table_rows(table04.loc[:, table04.columns], 0)
    
    normal_table03 = to.model_rows_to_df(table=table04, form_row=model_rows03['form_row'], columns=list(table04.columns))
    
    
