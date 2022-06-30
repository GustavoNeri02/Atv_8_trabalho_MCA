from .pdf_reader import PdfReader
from .table_organizer import TableOrganizer
from . import Constants as const
from . import util

import os
import pandas as pd

class DataExtractor(object):
    def __init__(self):
        pass
    

    def filtering_data(self, open_path:str):
        # manipula operações sobre a cópia dos dados 
        #  * deep -> uma nova instancia independente dos dados
        data_source = pd.read_csv(open_path)
        # criando o dataframe com filtragem de dados
        filter_dataframe = DataFormer(
            columns=const.FILTERING_PAGE_COLUMNS,
            data_file_name=const.FILTERING_PAGE_NAME,
            path=const.FILTERING_PAGE_PATH,
            limit_to_record=10,
            save_method='csv'
            )
        #pd.DataFrame(columns=data_source.columns)

        # infos
        # print(data_source.to_string())
        # print(data_source.info())

        # indentificando os filtros
        page_contex_filter_name = 'Chamada Pública'
        link_presentation_filter_name = 'Chamada Pública'

        # [undefined:index,'page_context', 'link_presentation', 'link_value']
        size = data_source.index.size
        for i in range(0, size):
            linha = data_source.iloc[i]
            #print(type(linha))
            
            if page_contex_filter_name in linha[0] and link_presentation_filter_name in linha[1]:
                # dados de cada linha do df
                print(linha.array)
                filter_dataframe.sinch_data(linha.array)

        filter_dataframe.up_save()
        #self.__save_df_to_excel_file(filter_dataframe, './filtered_data', 0)
        # print(filter_dataframe.to_string())
        print(f'filtered {filter_dataframe.get_size()} from {data_source.index.size}')
        
        print(filter_dataframe.get_form().info())
        
        return filter_dataframe.get_size()
    

    def __find_context_columns(self, table:pd.DataFrame) -> list():
        self.require_one = ['atividade']
        self.require_strict = ['data']
        context_columns = [0, 0]
        
        columns = table.columns.__str__().lower()
        has_require_one = list(map(columns.__contains__, self.require_one))
        require_strict = list(map(columns.__contains__, self.require_strict))
        
        if not has_require_one.__contains__(True):
            first_line = table.iloc[0].to_string().lower()
            has_require_one = list(map(first_line.__contains__, self.require_one))
            context_columns[0] = 1
            
        if not require_strict.__contains__(True):
            first_line = table.iloc[0].to_string().lower()    
            require_strict = list(map(first_line.__contains__, self.require_strict))
            context_columns[1] = 1
        
        return context_columns

    # Verifica se o data frame (a tabela) corresponde a uma tabela de "cronograma".
    #   É necessário encontrar algumas correspondencias de coluna: 
    #   > require_one of {fase, evento, atividade} and require_exact extrict {data}.
    #   É necessário determinar quais corespondencias foram encontradas.
    def __filtering_frame(self, frame: pd.DataFrame):
        valid = False
        if frame.columns.__str__().lower().__contains__(("atividade") and "data"):
            valid = True

        if frame.index.size > 0 and not valid :
           if frame.iloc[0].to_string().lower().__contains__(("atividade") and "data"):
                valid = True

        return valid
    

    def __resolve_header_line(self, frame:pd.DataFrame()):
        # soluçào supervisória, para a generalização do problema
        aux_index = 0
        in_column = False
        for column in list(frame.columns):
            #print(column)
            
            # !!!! contexto de validação reduzido
            if str(column).lower().__contains__('atividade'):
                in_column = True
                break
            
            aux_index += 1
        
        if not in_column:
            aux_index = 0

    def __normalising_frame(self, tables: list()):
        to = TableOrganizer()
        
        resolve_columns = False
        # realizar merge se mais de um frame da tabela
        table = tables[0]
        if len(tables) > 1:
            for context_table in tables[1:]:
                context_columns = self.__find_context_columns(table)
                
                if context_columns == [1, 1]:
                    resolve_columns = True
                
                context_table = to.normalize_table_data(context_table, resolve_columns)
                table = to.concatenate(table, context_table)
                
                resolve_columns = False
        else:
            context_columns = self.__find_context_columns(table)
            
            if context_columns == [1, 1]: # ! cenário limitado
                resolve_columns = True
            
            table = to.normalize_table_data(table, resolve_columns)
            
        model_rows = to.normalize_table_rows(table.loc[:, table.columns], 0)
        
        return to.model_rows_to_df(table=table, form_row=model_rows['form_row'], columns=list(table.columns))
        

    def extracting_data(self, open_path):
        reader = PdfReader()
        #filtered_data = pd.read_excel(open_path) 
        filtered_data = pd.read_csv(const.FILTERING_PAGE_PATH+const.FILTERING_PAGE_NAME) # const.FILTERING_PAGE_PATH+const.FILTERING_PAGE_NAME

        size = len(filtered_data.index)
        #print(f'size: {size}')
        for iter_pdf in range(0, size):
            #print('trying to extract pages')
            data_source = reader.extract_tables(
                filtered_data.loc[iter_pdf][const.SCRAPPING_REFERENCE_FILE])
            
            # create directory
            path = const.EXTRACTING_DATA_CRONOGRAM_PATH + '_' + str(iter_pdf)
            if not util.resolve_sys_path(path):
                return Exception(f'can\'t create directory {path}') 

            count_df = 0
            list_tables = list()
            for frame in data_source:
                print(f'dataframe: {frame[0].head()}')

                print('after filtering frame - to save csv')
                # save file in the correspondent directory
                # in_frame = self.filtering_frame(elemento_df[0])
                if self.__filtering_frame(frame[0]):
                    print('filtering frame')
                    #print(f'info: {frame[1]}')
                    #print(in_frame)
                    frame[0].to_csv(f'{path}/{count_df}.csv')
                    #frame[0].to_excel(f'{path}\\{count_df}.xlsx')
                    
                    in_line = self.__resolve_header_line(frame[0])
                        
                    #print(elemento_df[0].columns[aux_index:])
                    #print(elemento_df[0].loc[:, elemento_df[0].columns[aux_index:]])
                    list_tables.append(frame[0].loc[:, frame[0].columns[in_line:]])
                
                    count_df += 1
                
            # executa rotina de normalização dos dados
            # fica pra depois. Tabom...
            if len(list_tables) > 0:
                print('saving excel')
                try:
                    #print(list_tables)
                    normal_table = self.__normalising_frame(list_tables) # rotina de normalização
                    
                    normal_table.to_excel(f'{path}/{const.EXTRACTING_DATA_CRONOGRAM_NAME}', index=0)
                    #normal_table.to_excel(f'{path}\\normal_table.xlsx')
                except:
                    print('.exception - \tcan\'t save normal table - extracting data')
        
                
class DataFormer(object):
    def __init__(self, columns:list(), data_file_name:str, path:str=const.SCRAPPING_DATA_PATH, limit_to_record:int=5, save_method:str='csv'):
        self.__columns = columns
        self.__data_file_name = data_file_name
        self.__path = path
        
        self.__df = pd.DataFrame(columns=self.__columns)
        
        self.__limit_to_record = limit_to_record
        self.__unrecordered_iteration = 0
        self.__iteration = 0
       
        self.__save_method = None
        if save_method == 'excel':
            self.__save_method = self.__df.to_excel
        else: 
            self.__save_method = self.__df.to_csv
        
    def __sum_iteration(self):
        self.__unrecordered_iteration += 1
        self.__iteration += 1
        
    def __check_iteration(self):
        return self.__unrecordered_iteration >= self.__limit_to_record
    
    def __resolve_breaked_iteration(self):
        self.__iteration = self.__iteration - self.__unrecordered_iteration
        
    def __reset_iteration_recorder(self):
        self.__unrecordered_iteration = 0
        
    def __save_data(self):
        to_path = self.__path + self.__data_file_name
        #self.__save_method(to_path, index=0)
        self.__df.to_csv(to_path, index=0)
        self.__reset_iteration_recorder()
        
    def sinch_data(self, data_format:list()):
        try:
            # inserir dados
            #print(self.__df.loc[len(self.__df.index)])
            self.__df.loc[self.__df.index.size] = data_format
            #print(self.__df.loc[len(self.__df.index-1)])
            self.__sum_iteration()
            
        except:
            # resolve referencia de iteração salva
            self.__resolve_breaked_iteration()
            
            # apresenta erro
            print(f'.exception -/t making data entrance ({self.__data_file_name}): \
                  kept {self.__iteration}/ lost {self.__unrecordered_iteration}')
            
            # reseta iterator local limitado e finaliza função
            self.__reset_iteration_recorder()
            return
        
        if self.__check_iteration():
            # sincronizar data frame (salvar alterações realizadas)
            self.__save_data()

    def get_form(self)->pd.DataFrame():
        return  self.__df
        
    def up_save(self):
        #if self.__unrecordered_iteration > 0:
        self.__save_data()
            
    def get_str(self)->str():
        aux = (self.__iteration-self.__unrecordered_iteration)
        return f'to {self.__data_file_name}: \
                  kept {aux} / unsaved {self.__unrecordered_iteration}'
                  
    def get_size(self)->int():
        return self.__iteration
        
        
if __name__ == '__main__':
    df = DataFormer(['firstname', 'lastname'], 'data_teste.csv', './')
    df.sinch_data(['Angel', 'Rodrigues'])
    df.sinch_data(['KKK', 'S2'])
    
    data = df.get_form()
    print(data.head())
    
    df.up_save()