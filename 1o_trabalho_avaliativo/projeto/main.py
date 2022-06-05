from scrapping.ws_bot import WsBot
from scrapping.enum_by import EnumBy as by
from scrapping.user_system import MenuSystem
import sys

split_presentation = '\n*******************************************************\n'

bot = WsBot()

print('(1) yes (0) no')
entry = int(input('.extract from page? '))
if entry == '1':
    bot.extract_in_page()
    bot.filtering_data('./keeping/data.xlsx')
    bot.extract_data('./filtered_data.xlsx')

# Menu context
si = bot.form_menu_system('./filtered_data.xlsx') 

while True:
    print(split_presentation)
    print('Menu Contents:')
    for content in si.to_string():
        print(content)
    
    entry = int(input('> tipe a content: '))
    if entry == -1:
        break
    
    info = si.info_content(entry)
    if info is not None:
        print(split_presentation)
        print(info)
    else: print(f'exception - can not find content ({entry})')

    input('> tipe to get to the menu')

print('finish it...')
bot.__exit__()