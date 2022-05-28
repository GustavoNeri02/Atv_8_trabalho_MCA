from selenium import webdriver
from selenium.webdriver.common.by import By
# import tabula
from .pdf_reader import PdfReader

import Constants as const

import os
import pandas as pd


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
        static_elements = pagination_element.find_elements(By.XPATH, './/span') \
 \
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

    # require_one = [fase, evento, atividade] and require_exact = [data]
    def filtering_frame(self, frame: pd.DataFrame):
        valid = False
        if frame.columns.__str__().lower().__contains__(("atividade" or "fase" or "evento") and "data"):
            valid = True

        if frame.index.size > 0 and not valid :
            if frame.iloc[0].to_string().lower().__contains__(("atividade" or "fase" or "evento") and "data"):
                valid = True

        return valid

    def normalising_frame(self, frame: pd.DataFrame):
        pass

    def extract_data(self, open_path):
        reader = PdfReader()
        filtered_data = pd.read_excel(open_path)

        length = 3  # len(filtered_data.index)
        for iter_pdf in range(0, length):
            elementos_df = reader.extract_tables(filtered_data.loc[iter_pdf][2])

            # create directory
            path = f'.\\scrapping\\csv_teste\\{iter_pdf}'
            try:
                os.mkdir(path)
            except: pass

            count_df = 0
            for elemento_df in elementos_df:
                print(f'info: {elemento_df[1]}')
                print(f'dataframe: {elemento_df[0].head()}')

                # save file in the correspondent directory
                if self.filtering_frame(elemento_df[0]):
                    elemento_df[0].to_csv(f'{path}\\{count_df}.csv')

                count_df += 1
