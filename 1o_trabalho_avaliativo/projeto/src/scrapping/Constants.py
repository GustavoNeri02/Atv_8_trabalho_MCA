DRIVER_PATH = './msedgedriver.exe'

URL_HOME = 'http://www.fapeg.go.gov.br/categoria/editais/'

SCRAPPING_DATA_PATH = '../data/'
SCRAPPING_REFERENCE_COLUMNS = ['page_title', 'file_name', 'page_url', 'file_url']
SCRAPPING_REFERENCE_FILE = 3

SCRAPPING_PAGE_NAME = 'scrapping_data.csv'
SCRAPPING_PAGE_PATH = SCRAPPING_DATA_PATH
SCRAPPING_PAGE_COLUMNS = SCRAPPING_REFERENCE_COLUMNS

FILTERING_PAGE_NAME = 'filtering_data.csv'
FILTERING_PAGE_PATH = SCRAPPING_DATA_PATH
FILTERING_PAGE_COLUMNS = SCRAPPING_PAGE_COLUMNS

EXTRACTING_DATA_CRONOGRAM_NAME = 'extracting_data.xlsx'
EXTRACTING_DATA_PATH = SCRAPPING_DATA_PATH
EXTRACTING_DATA_CRONOGRAM_PATH = SCRAPPING_DATA_PATH + 'cronogram' 

FIGURE_DATA_PATH = SCRAPPING_DATA_PATH + '/figures/' 
