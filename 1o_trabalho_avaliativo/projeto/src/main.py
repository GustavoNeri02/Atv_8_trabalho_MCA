from re import L
from scrapping.ws_bot import WsBot
from scrapping.user_system import FormMenuContent, MenuSystem
import sys
import Constants as const

def entry_presentation(message:str, type):
    while True:
        try:
            return type(input(message)) 
        except:
            continue
    

bot = WsBot()
bot.minimize_window()

print('(1) yes (0) no')
entry = entry_presentation('.extract from page? ', int)

# extrair dados da página (?), filtrar os dados encontrados, extrair informações 
if entry == 1:
    bot.maximize_window()
    #try:
    #    bot.extract_articles() # ok
    #except:
    #    print(bot.get_str())
            
    #bot.filtering_data(bot.get_path_scrapping_data()) # ok
    bot.extracting_data(bot.get_path_filtering_data()) # ok?  

bot.minimize_window()

# Menu context
#si = bot.form_menu_system(bot.get_path_filtering_data())
args = [
    FormMenuContent(bot.form_articles),
    FormMenuContent(bot.form_graph01),
    FormMenuContent(bot.form_graph02)
    ]
si = bot.routine_form_menu_content(args)

if si is not None:
    while True:
        print(const.SPLIT_PRESENTATION)
        print('Menu Contents:')
        for content in si.to_string():
            print(content)
        
        try:
            entry = entry_presentation('> tipe a content: ', int)
        except: 
            continue
        if entry == -1:
            break
        
        info = si.info_content(entry)
        if info is not None:
            print(const.SPLIT_PRESENTATION)
            print(info)
        else: print(f'exception - can not find content ({entry})')

        input('> tipe to get to the menu')

print('finishing it...')
bot.__exit__()