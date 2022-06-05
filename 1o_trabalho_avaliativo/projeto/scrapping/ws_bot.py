from code import interact
from selenium import webdriver
from selenium.webdriver.common.by import By

from scrapping.user_system import MenuContent, MenuSystem
# import tabula
from .pdf_reader import PdfReader
from .table_organizer import TableOrganizer
import Constants as const

import os
import pandas as pd
import re


class WsBot(webdriver.Edge):
    def __init__(self, driver_path=const.DRIVER_PATH):
        # print(driver_path)
        self.driver_path = driver_path
        os.environ['PATH'] += self.driver_path

        super(WsBot, self).__init__()

        self.__df = pd.DataFrame(columns=['page_context', 'link_presentation', 'link_value'])

    def __exit__(self):
        self.close()
        self.quit()

    def get_there(self, url: str):
        self.maximize_window()
        self.get(url)

    def get_to(self, by: By, value: str, context=None):
        if context is None:
            context = self

        element = context.find_element(by=by, value=value)
        element.click()

    def send_to(self, by: By, value: str, keys: str):
        element = self.find_element(by=by, value=value)
        element.send_keys(keys)

    # Rotina basica de execução do bot:
    #   -> objetivo - percorrer os editais da página FAPEG e registrar os arquivos pdf
    #        encontrados e seus dados pertinentes de cada edital.
    #   -> proxima etapa - fazer uma análise semantica no conjunto dos dados registrados 
    #       (sobre os editais) e encontrar métricas sobre esses dados

    def extract_in_page(self):
        self.get(const.URL_HOME)

        # acessar cada pagina de editais da pagina me contexto
        # obtem lista de páginas e acessa uma por uma
        while (True):
            # opera os artigos na página atual
            self.__in_page()

            # gerencia navegação para um próximo indice de paginação, se houver
            next_page = self.__next_page_in_pagination()

            # navega para a proxima pagina, se não finaliza a navegação entre paginações
            if next_page is not None:
                print(f'going to {next_page.text}')
                next_page.click()

            else:
                # finished all routines
                print('no more next list pages')
                break

    def __in_page(self):
        # obtem lista de elementos de artigos / editais no contexto de página principal
        articles = self.find_elements(By.XPATH, '//div[@id="content"]/article')

        # percorrer a interação sobre os diferentes artigos de edital da página encontrados
        for article in articles:
            # obtem referencia de link para a pagina do edital
            page = article.find_element(By.XPATH, './/a')
            link = page.get_attribute('href')
            page_text = page.text

            print(page_text)

            # acessa em uma nova janela
            self.execute_script(f"window.open('{link}', 'new tab')")
            self.switch_to.window(self.window_handles[1])

            # localiza e gerencia os arquivos encontrados
            self.__in_article(name_page=page_text)

            # retorna a janela primaria
            self.close()
            self.switch_to.window(self.window_handles[0])

    # Encontra arquivos do formato pdf na pagina e registra sua operação \
    #   (os dados pertinentes ao acesso aos arquivos)
    def __in_article(self, name_page: str):
        # obtem lista de elementos para arquivos na pagina (p)
        file_elements = self.find_elements(By.XPATH, '//div[@class="pf-content"]/p')
        # print(len(file_elements))

        # busca nos elementos de arquivo os arquivos do forma pdf e suas informações pertinentes
        ref_files = list()  # registra rotina de log
        for file_element in file_elements:
            try:
                # elemento do com referencia do link de um arquivo (a)
                link_element = file_element.find_element(By.XPATH, './/a')

            except:
                # print('not a file')
                continue  # not a file

            # obtem valor do link (href), se for pdf, adiciona ao conjunto dos dados 
            link_value = link_element.get_attribute('href')
            # print(link_value)
            if str(link_value.split('.')[-1]).lower() == 'pdf':
                ref_files.append(link_value)

                self.__sinc_arquivo(name_page, link_element.text, link_value)

        print(f'pdf files in page: {len(ref_files)}')

    # navega para a proxima pagina do indice de paginação - se houver.
    def __next_page_in_pagination(self):
        # obtem elemento de paginaçao e guarda referencia de elementos estáticos em paginação (span)
        pagination_element = self.find_element(By.XPATH, '//div[@class="pagination"]')
        static_elements = pagination_element.find_elements(By.XPATH, './/span') 
 
            # busca em elementos estáticos de paginação (span), pela referencia do indice
        #   da pagina em contexto (atual)
        ref_context = -1
        for page in static_elements:
            ref_text = page.text

            # são dois tipos de valores que podem ser encontrados, entre, geralmente, 
            #   no maximo 3 elementos estáticos na paginação, '…' ou <int-em-formato-de-texto>.
            if ref_text != '…':  # obs: '…' diferente de '...'
                ref_context = int(ref_text)
                break

        # obtem referencia para os elementos de link (a) em paginação
        pagination_links = pagination_element.find_elements(By.XPATH, './/a')

        # percorre as referencias de link em paginação, e retorna o elemento do link
        #   que corresponde a próxima página - acordo a referência de página atual
        for page in pagination_links:
            try:
                # os valores do texto nos links, costumam ser <int-em-formato-de-texto>
                # - basta converter
                value = int(page.text)

            except:
                # print('not a number')
                continue

            # confere referecia para a proxima pagina
            if value == (ref_context + 1):
                return page
                # print(value)

        # não existe práxima página nas referências de paginação 
        return None

    # gerencia links de arquivo e seus textos de apresentação em uma tabela da finalidade
    def __sinc_arquivo(self, page_context: str, link_presentation: str, link_value: str):
        self.__df.loc[len(self.__df.index)] = [page_context, link_presentation, link_value]

        self.__save_df_to_excel_file(self.__df, './data', 0)

    # salva contexto atual do arquivo
    def __save_df_to_excel_file(self, df: pd.DataFrame, file_path, index):
        df.to_excel(f'{file_path}.xlsx', index=index)

    def filtering_data(self, open_path: str = None):
        if open_path is not None:
            self.__df = pd.read_excel(open_path, index_col=0)

        # manipula operações sobre a cópia dos dados 
        #  * deep -> uma nova instancia independente dos dados
        data_source = self.__df.copy(deep=True)
        # criando o dataframe com filtragem de dados
        filter_dataframe = pd.DataFrame(columns=['page_context', 'link_presentation', 'link_value'])

        # infos
        # print(data_source.to_string())
        # print(data_source.info())

        # indentificando os filtros
        page_contex_filter_name = 'Chamada Pública'
        link_presentation_filter_name = 'Chamada Pública'

        # [undefined:index,'page_context', 'link_presentation', 'link_value']
        for i in range(0, data_source.index.size):
            linha = data_source.iloc[i]
            if page_contex_filter_name in linha[0] and link_presentation_filter_name in linha[1]:
                # dados de cada linha do df
                filter_dataframe.loc[filter_dataframe.index.size] = linha

        self.__save_df_to_excel_file(filter_dataframe, './filtered_data', 0)
        # print(filter_dataframe.to_string())
        print(f'filtered {filter_dataframe.index.size} from {data_source.index.size}')

    # Berifica se o data frame (a tabela) corresponde a uma tabela de "cronograma".
    #   É necessário encontrar algumas correspondencias de coluna: 
    #   > require_one of {fase, evento, atividade} and require_exact extrict {data}.
    #   É necessário determinar quais corespondencias foram encontradas.
    def filtering_frame(self, frame: pd.DataFrame):
        valid = False
        if frame.columns.__str__().lower().__contains__(("atividade") and "data"):
            valid = True

        if frame.index.size > 0 and not valid :
           if frame.iloc[0].to_string().lower().__contains__(("atividade") and "data"):
                valid = True

        return valid

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


    def normalising_frame(self, tables: list()):
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
        

    def extract_data(self, open_path):
        reader = PdfReader()
        filtered_data = pd.read_excel(open_path)

        length = len(filtered_data.index)
        for iter_pdf in range(0, length):
            elementos_df = reader.extract_tables(filtered_data.loc[iter_pdf][2])

            # create directory
            path = f'.\\scrapping\\csv_teste\\{iter_pdf}'
            try:
                os.mkdir(path)
            except: pass

            count_df = 0
            list_tables = list()
            for elemento_df in elementos_df:
                #print(f'info: {elemento_df[1]}')
                #print(f'dataframe: {elemento_df[0].head()}')

                # save file in the correspondent directory
                # in_frame = self.filtering_frame(elemento_df[0])
                if self.filtering_frame(elemento_df[0]):
                    #print(in_frame)
                    elemento_df[0].to_csv(f'{path}\\{count_df}.csv')
                    elemento_df[0].to_excel(f'{path}\\{count_df}.xlsx')
                    
                    # soluçào supervisória, para a generalização do problema
                    aux_index = 0
                    in_column = False
                    for column in list(elemento_df[0].columns):
                        print(column)
                        
                        if str(column).lower().__contains__('atividade'):
                            in_column = True
                            break
                            
                        aux_index += 1
                    
                    if not in_column:
                        aux_index = 0
                        
                    #print(elemento_df[0].columns[aux_index:])
                    #print(elemento_df[0].loc[:, elemento_df[0].columns[aux_index:]])
                    list_tables.append(elemento_df[0].loc[:, elemento_df[0].columns[aux_index:]])
                
                count_df += 1
                
            # executa rotina de normalização dos dados
            # fica pra depois. Tabom...
            if len(list_tables) > 0:
                try:
                    print(list_tables)
                    normal_table = self.normalising_frame(list_tables)
                    normal_table.to_csv(f'{path}\\normal_table.csv')
                    normal_table.to_excel(f'{path}\\normal_table.xlsx')
                except:
                    pass    

    def __regex(self, pattern: str, entry: str):
        return re.search(pattern, entry)

    def form_menu_system(self, path):
        filtered_data = pd.read_excel(path)
        
        msystem = MenuSystem()
        count = 0
        for iteration in range(0, filtered_data.index.size):
            item = filtered_data.iloc[iteration]
            #print(item)
            
            pattern = '^.*(Chamada Pública).*(([nN]º)?( )?[0-9]{2}\/[0-9]{4})'
            entry = item.loc['page_context']
            #print(f'entry = {entry}')
            
            match = self.__regex(pattern, entry)     
            if match is not None:
                num = match.group()
                #print(num)
                
                title = entry[match.span()[1]:]
                #print(title)
            else: num = None
            
            pattern = '–(.*$)'
            match = self.__regex(pattern, entry)     
            if match is not None:
                title = match.group().strip('– ')
                #print(title)
            else: title = None
            
            link = item.loc['link_value']
            path = None
            
            mcontent = MenuContent(num=num,title=title,link=link,path_to=path)
            try:
                table = pd.read_csv(f'./scrapping/csv_teste/{iteration}/normal_table.csv')
                print(table)
                mcontent.set_cronogram(table)
            except: pass
            
            msystem.insert_item(mcontent)
        
        #print(count)
        
        msystem.sync_items()
        return msystem    
                
            
            
        
        '''
        self.require_one = ['atividade', 'fase', 'evento']
        self.require_extrict = ['data']

        #in_column = [0, 0] # nothing at anywahere

        columns = frame.columns.__str__().lower()
        has_require_one = list(map(columns.__contains__, self.require_one))
        #print(has_require_one)

        has_require_extrict = list(map(columns.__contains__, self.require_extrict))
        #print(has_require_extrict)

        # second routine, if to do search in line 0
        if(frame.index.size > 0):
            first_line = frame.iloc[0].to_string().lower()

            if not has_require_one.__contains__(True):
                has_require_one = list(map(first_line.__contains__, self.require_one))
                #print(has_require_one)
            #else: in_column[0] = 1

            if not has_require_extrict.__contains__(True):
                has_require_extrict = list(map(first_line.__contains__, self.require_extrict))
                #print(has_require_extrict)  
            #else: in_column[1] = 1

            return list(has_require_one + has_require_extrict) # [True, True, False, True]
        '''

