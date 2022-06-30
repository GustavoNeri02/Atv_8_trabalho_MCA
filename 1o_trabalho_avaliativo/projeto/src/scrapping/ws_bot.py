from numpy import DataSource
from selenium import webdriver
from selenium.webdriver.common.by import By

from scrapping.info_graph import InfoGraph

from .user_system import ArticleContent, FigContent, FormMenuContent, MenuContent, MenuSystem
# import tabula
from .data_source import DataExtractor, DataFormer
from . import Constants as const

import os
import re
import pandas as pd
import numpy as np



class WsBot(webdriver.Edge):
    def __init__(self, driver_path=const.DRIVER_PATH):
        # print(driver_path)
        self.driver_path = driver_path
        os.environ['PATH'] += self.driver_path

        super(WsBot, self).__init__()

        self.__df = DataFormer(
                    columns=const.SCRAPPING_PAGE_COLUMNS, 
                    data_file_name=const.SCRAPPING_PAGE_NAME, 
                    path=const.SCRAPPING_DATA_PATH, 
                    limit_to_record=5
                )
        self.__ds = DataExtractor()
        
        self.__found_articles = 0
        self.__filtered_articles = 0

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
    
    def __count_found_article(self, count:int=1):
        self.__found_articles += count
        
    def __count_filtered_article(self, count:int=1):
        self.__filtered_articles += count

    # Rotina basica de execução do bot:
    #   -> objetivo - percorrer os editais da página FAPEG e registrar os arquivos pdf
    #        encontrados e seus dados pertinentes de cada edital.
    #   -> proxima etapa - fazer uma análise semantica no conjunto dos dados registrados 
    #       (sobre os editais) e encontrar métricas sobre esses dados
    def extract_articles(self):
        self.get(const.URL_HOME)

        # acessar cada pagina de editais da pagina me contexto
        # obtem lista de páginas e acessa uma por uma
        while (True):
            # opera os artigos na página atual
            self.__in_page()

            # gerencia navegação para um próximo indice de paginação, se houver
            ref_next_page = self.__ref_next_page_in_pagination()

            # navega para a proxima pagina, se não finaliza a navegação entre paginações
            if ref_next_page is not None:
                print(f'going to {ref_next_page.text}')
                ref_next_page.click()
            else:
                # finished all routines
                self.__df.up_save()
                
                print('no more next page lists')
                break

    def __in_page(self):
        # obtem lista de elementos de artigos / editais no contexto de página principal
        articles = self.find_elements(By.XPATH, '//div[@id="content"]/article')

        # percorrer a interação sobre os diferentes artigos de edital da página encontrados
        for article in articles:
            # obtem referencia de link para a pagina do edital
            article_page = article.find_element(By.XPATH, './/a')
            article_url = article_page.get_attribute('href')
            article_title = article_page.text

            print(article_title)

            # acessa em uma nova janela
            self.execute_script(f"window.open('{article_url}', 'new tab')")
            self.switch_to.window(self.window_handles[1])

            # localiza e gerencia os arquivos encontrados
            self.__in_article(page_title=article_title, page_url=article_url)

            # retorna a janela primaria
            self.close()
            self.switch_to.window(self.window_handles[0])

    # Encontra arquivos do formato pdf na pagina e registra sua operação \
    #   (os dados pertinentes ao acesso aos arquivos)
    def __in_article(self, page_title: str, page_url: str):
        # obtem lista de elementos para arquivos na pagina (p)
        file_elements = self.find_elements(By.XPATH, '//div[@class="pf-content"]/p')
        # print(len(file_elements))

        # busca nos elementos de arquivo os arquivos do formato pdf e suas informações relativas
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

                self.__sinc_arquivo(page_title=page_title, file_name=link_element.text, page_url=page_url, file_url=link_value)

        print(f'pdf files in page: {len(ref_files)}')

    # navega para a proxima pagina do indice de paginação - se houver.
    def __ref_next_page_in_pagination(self):
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
    def __sinc_arquivo(self, page_title: str, file_name: str, page_url: str, file_url: str):
        self.__df.sinch_data([page_title, file_name, page_url, file_url])
        
        self.__count_found_article()

        # deprecated!
        #self.__df.loc[len(self.__df.index)] = [page_title, file_name, page_url, file_url]
        #self.__save_df_to_excel_file(self.__df, './data', 0)

    # deprecated!
    # salva contexto atual do arquivo
    #def __save_df_to_excel_file(self, df: pd.DataFrame, file_path, index):
    #    df.to_excel(f'{file_path}.xlsx', index=index)
    
    def get_str(self):
        return self.__df.get_str()
    
    def get_path_scrapping_data(self):
        return const.SCRAPPING_PAGE_PATH + const.SCRAPPING_PAGE_NAME
    
    def get_path_filtering_data(self):
        return const.FILTERING_PAGE_PATH + const.FILTERING_PAGE_NAME
    
    
    def filtering_data(self, open_path:str):
        c = self.__ds.filtering_data(open_path)
        
        self.__count_filtered_article(c)
        
    def extracting_data(self, open_path):
        self.__ds.extracting_data(open_path)

    def __regex(self, pattern: str, entry: str):
        return re.search(pattern, entry)
        
    
    # rotinas de formação de 'contents' for 'menu sistem' 
    #
    def form_articles(self) -> list():
        try:
            filtered_data = pd.read_csv(self.get_path_filtering_data())
            print(filtered_data.info())
        except:
            print('.exception -\t can\'t open a data frame: in menu sistem')
            return list()
        
        acontents = list()
        for iteration in range(0, filtered_data.index.size):
            item = filtered_data.iloc[iteration]
            print(item)
            
            pattern = '^.*(Chamada Pública).*(([nN]º)?( )?[0-9]{2}\/[0-9]{4})'
            entry = item.loc[const.SCRAPPING_REFERENCE_COLUMNS[0]]
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
            
            link = item.loc[const.SCRAPPING_REFERENCE_COLUMNS[3]]
            page = item.loc[const.SCRAPPING_REFERENCE_COLUMNS[2]]
            path = None
            
            acontent = ArticleContent(num=num, title=title, link=link, page=page, path_to=path)
            try:
                path = const.EXTRACTING_DATA_CRONOGRAM_PATH + '_' + str(iteration)
                print(path)
                cronogram = pd.read_excel(path + '/' + const.EXTRACTING_DATA_CRONOGRAM_NAME)
                print(cronogram.head())
                #print(cronogram)
                acontent.set_cronogram(cronogram)
            except: 
                print('.exception - \topenning the frame - menu sistem')
                
            acontents.append(acontent)   
            
        return acontents
    
    # grafico de pizza - a relação de artigos (páginas de edital) encontrados para artigos filtrados 
    def form_graph01(self) -> list():
        scrapping_data = pd.read_csv(const.SCRAPPING_PAGE_PATH + const.SCRAPPING_PAGE_NAME)
        print(scrapping_data.info())    
        
        filtered_data = pd.read_csv(const.FILTERING_PAGE_PATH + const.FILTERING_PAGE_NAME)
        print(filtered_data.info())
        
        igs = list()
        ig = InfoGraph()
        ig.set_title('serching articles - scrapping x filtering')
        
        x_values = [scrapping_data.index.size, filtered_data.index.size]
        y_values = ['scrapping', 'filtering']
        explode = [0.02, 0.02]
        
        ig.pie(x_values, y_values, explode)
        ig.save()
        igs.append(FigContent(ig, ig.title))
        igs[0].presentation()()
        
        return igs
        
    # gráfico de histograma - a relação da quantida de artigos para a data de publicação
    def form_graph02(self) -> list():
        filtered_data = pd.read_csv(const.FILTERING_PAGE_PATH + const.FILTERING_PAGE_NAME)
        #print(filtered_data.info())
        
        cronograms = list()
        relative = const.EXTRACTING_DATA_CRONOGRAM_PATH
        for iteration in range(0, filtered_data.index.size):
            try:
                path = relative + '_' + str(iteration)
                cronogram = pd.read_excel(path + '/' + const.EXTRACTING_DATA_CRONOGRAM_NAME)
                
                cronograms.append(cronogram)
            except: 
                cronograms.append(None)
                
        search_date_for = [['lançamento'], ['submissão', 'inscrições', 'inscrição'], ['resultado']]
        search_lancamento = search_date_for[0]
        search_submissao = search_date_for[1]
        search_resultado = search_date_for[2]
        
        regex = lambda pattern, entry: re.findall(pattern, entry)
        date_pattern_first = r'([0-9]{2}\/[0-9]{2}\/[0-9]{4}).*$' 
        date_pattern_last = r'^.*([0-9]{2}\/[0-9]{2}\/[0-9]{4})' 


        cronograms_dates = list()

        size_i = len(cronograms)
        for i in range(0, size_i):
            lancamento_date = np.nan
            submissao_date = np.nan
            resultado_date = np.nan
            last_date = np.nan
            
            cronogram = pd.DataFrame(cronograms[i])
            if cronogram is None : 
                cronograms_dates.append([lancamento_date, submissao_date, resultado_date, last_date])
                continue
            
            #print(cronogram.head())
            #print(cronogram.info())
            
            size_j = cronogram.index.size
            for j in range(0, size_j):
                row = str(cronogram.loc[j, 'atividade']).lower()
                
                if lancamento_date is np.nan and list(map(row.__contains__, search_lancamento)).__contains__(True):
                    # print(row)
                
                    # pegar as datas
                    date_data = str(cronogram.loc[j, 'data']).lower()
                    match = regex(date_pattern_first, date_data)
                    if len(match) > 0 : lancamento_date = match[0]
                    
                    # print(lancamento_date)
                    
                if submissao_date is np.nan and list(map(row.__contains__, search_submissao)).__contains__(True):
                    # print(row)
                    
                    # pegar as datas
                    date_data = str(cronogram.loc[j, 'data']).lower()
                    match = regex(date_pattern_last, date_data)
                    if len(match) > 0: submissao_date = match[0]
                    
                    # print(submissao_date)
                    
                if resultado_date is np.nan and list(map(row.__contains__, search_resultado)).__contains__(True):
                    # print(row)
                    
                    # pegar as datas
                    date_data = str(cronogram.loc[j, 'data']).lower()
                    match = regex(date_pattern_first, date_data)
                    if len(match) > 0 : resultado_date = match[0]
                    
                    # print(resultado_date)
                    
                if j == (size_j - 1):
                    # print(row)
                    
                    # pegar as datas
                    date_data = str(cronogram.loc[j, 'data']).lower()
                    match = regex(date_pattern_last, date_data)
                    if len(match) > 0 : last_date = match[0]
                    
                    # print(last_date)
            
            cronograms_dates.append([str(lancamento_date), str(submissao_date), str(resultado_date), str(last_date)])
    
        columns = ['lancamento', 'submissao', 'resultado', 'last']
        df_cronograms_dates = pd.DataFrame(data=cronograms_dates, columns=columns)
        #df_cronograms_dates[:] = df_cronograms_dates[:].apply(pd.strftime('%d-%m-%Y'))
        df_cronograms_dates = df_cronograms_dates.astype(np.datetime64)
        df_cronograms_dates.to_csv(const.EXTRACTING_DATA_PATH + 'cronograms_dates.csv', index = 0)

        igs = list()
        ig = InfoGraph()
        ig.set_title('count dates - publicacao date')
        ig.hist(df_cronograms_dates.loc[:, 'lancamento'])
        ig.save()
        igs.append(FigContent(ig, ig.title))
        igs[0].presentation()()
        
        ig = InfoGraph()
        ig.set_title('count dates - submissao date')
        ig.hist(df_cronograms_dates.loc[:,'submissao'])
        ig.save()
        igs.append(FigContent(ig, ig.title))
        igs[1].presentation()()
        
        ig = InfoGraph()
        ig.set_title('count dates - resultado date')
        ig.hist(df_cronograms_dates.loc[:, 'resultado'])
        ig.save()
        igs.append(FigContent(ig, ig.title))
        igs[2].presentation()()
        
        ig = InfoGraph()
        ig.set_title('count dates - last date')
        ig.hist(df_cronograms_dates.loc[:,'last'])
        ig.save()
        igs.append(FigContent(ig, ig.title))
        igs[3].presentation()()
         
        return igs
    
    # gráfico de histograma - a relação da quantida de artigos para a data de resultados
    def form_graph03(self) -> list():
        pass
    
    def form_mcontent(self, arg:FormMenuContent) -> list():
        return arg.run()
    
    def routine_form_menu_content(self, args:list()):
        msystem = MenuSystem()
        
        for arg in args:
            mcontents = self.form_mcontent(arg)
            #print(mcontents)
            
            for mcontent in mcontents:  
                msystem.insert_item(mcontent)
            
        msystem.sync_items()
        return msystem    
    

    def form_menu_system(self, path):
        try:
            filtered_data = pd.read_csv(path)
            print(filtered_data.info())
        except:
            print('.exception -\t can\'t open a data frame: in menu sistem')
            return None
            
        msystem = MenuSystem()
        count = 0
        for iteration in range(0, filtered_data.index.size):
            item = filtered_data.iloc[iteration]
            print(item)
            
            pattern = '^.*(Chamada Pública).*(([nN]º)?( )?[0-9]{2}\/[0-9]{4})'
            entry = item.loc[const.SCRAPPING_REFERENCE_COLUMNS[0]]
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
            
            link = item.loc[const.SCRAPPING_REFERENCE_COLUMNS[3]]
            page = item.loc[const.SCRAPPING_REFERENCE_COLUMNS[2]]
            path = None
            
            acontent = ArticleContent(num=num, title=title, link=link, page=page, path_to=path)
            try:
                path = const.EXTRACTING_DATA_CRONOGRAM_PATH + '_' + str(iteration)
                print(path)
                cronogram = pd.read_excel(path + '/' + const.EXTRACTING_DATA_CRONOGRAM_NAME)
                print(cronogram.head())
                #print(cronogram)
                acontent.set_cronogram(cronogram)
            except: 
                print('.exception - \topenning the frame - menu sistem')
            
            msystem.insert_item(acontent)
        
        # trying graficos
        #print(count)
        ig = InfoGraph()
        ig.set_title('serching articles - bot process')
        ig.pie([280, 34], ['found', 'filtered'], [0.02, 0.02])
        ig.save()
        
        fcontent = FigContent(ig,'serching articles - bot process')
        msystem.insert_item(fcontent)
        
        msystem.sync_items()
        
        print(self.__found_articles)
        print(self.__filtered_articles)
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

'''
    gerencia a operação de um data-frame (pandas) - criar e, inserir  e salvar (simultaneamente)
'''
'''
class DataFormer():
    def __init__(self, columns:list(), data_file_name:str, path:str=const.SCRAPPING_DATA_PATH, limit_to_record:int=5):
        self.__columns = columns
        self.__data_file_name = data_file_name
        self.__path = path
        
        self.__df = pd.DataFrame(columns=self.__columns)
        
        self.__limit_to_record = limit_to_record
        self.__unrecordered_iteration = 0
        self.__iteration = 0
       
        
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
        to_path = self.__path+self.__data_file_name
        self.__df.to_csv(to_path, index=0)
        self.__reset_iteration_recorder()
        
    def sinch_data(self, data_format:list()):
        try:
            # inserir dados
            self.__df.loc[len(self.__df.index)] = data_format
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
    df = DataFormer(['firstname', 'lastname'], 'data_teste.csv')
    df.sinch_data(['Angel', 'rodrigues'])
    df.sinch_data(['Kalliny', 'Ester'])
    
    data = df.get_form()
    print(data.head())
    
    df.up_save()
'''