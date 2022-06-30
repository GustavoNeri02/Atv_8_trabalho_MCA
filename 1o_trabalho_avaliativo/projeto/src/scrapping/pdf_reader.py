import tabula as tb
import pandas as pd
import numpy as np

'''
    Extrair elementos (tabelas e corpo de texto) de arquivos do formato pdf.
'''

class PdfReader(object):
    def __init__(self):
        pass

    def extract_tables(self, file_path)->list():
        dfs = tb.read_pdf(file_path, pages="all")

        # vincula informações aos elementos
        plus_dfs = list()
        for iterador in dfs:
            info = [len(iterador), type(iterador)]

            plus_dfs.append([iterador, info])

        return plus_dfs


if __name__ == '__main__':
    def extract_data(open_path):
        reader = PdfReader()
        stracted_data = pd.read_excel(open_path)

        for i in range(0, 1):
            elementos_df = reader.extract_tables(stracted_data.loc[i][2])

            for elemento_df in elementos_df:
                print(f'info: {elemento_df[1]}')
                print(f'dataframe: {elemento_df[0].head()}')
                elemento_df[0].to_csv('csv_teste.csv')

    extract_data('./filtered_data.xlsx')

