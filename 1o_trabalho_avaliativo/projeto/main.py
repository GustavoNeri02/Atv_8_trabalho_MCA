from scrapping.ws_bot import WsBot
from scrapping.enum_by import EnumBy as by

bot = WsBot()

#bot.extract_in_page()
#bot.filtering_data('./keeping/data.xlsx')
bot.extract_data('./filtered_data.xlsx')
    
print(input('finish it'))
bot.__exit__()