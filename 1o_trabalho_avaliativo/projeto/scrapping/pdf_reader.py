import tabula as tb
import pandas as pd
import numpy as np

'''
    Extrair elementos (tabelas e corpo de texto) de arquivos do formato pdf.
'''


class PdfReader(object):
    def __init__(self):
        pass

    def extract_tables(self, file_path):
        dfs = tb.read_pdf(file_path, pages="all")

        # vincula incormações aos elementos
        plus_dfs = list()
        for iterador in dfs:
            info = [len(iterador), type(iterador)]

            plus_dfs.append([iterador, info])

        return plus_dfs


if __name__ == '__main__':
    reader = PdfReader()

    file_path = 'http://www.fapeg.go.gov.br/wp-content/uploads/2018/01/CP_01_2018_PARTICIPACAO.pdf'
    dfs = reader.extract_tables(file_path)

    for element in dfs:
        print(element[1])
        print(element[0].head())
