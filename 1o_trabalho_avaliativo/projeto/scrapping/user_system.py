#import dataclasses
import pandas as pd

class MenuContent():
    def __init__(self, num, title, link, path_to):
        self.__ref_context = -1
        self.__num= num
        self.__title = title
        self.__cronogram = None
        self.__link = link
        self.__path = path_to
        
    def set_cronogram(self, cronogram):
        self.__cronogram = cronogram
        
    def __set_ref_context(self, index: int):
        self.__ref_context = index
    
    @property        
    def ref_context(self):
        return int(self.__ref_context)  
    
    @property        
    def num(self):
        return str(self.__num)  
    
    @property        
    def title(self):
        return str(self.__title)  
    
    @property        
    def cronograma(self):
        return pd.DataFrame(self.__cronogram)  
    
    @property        
    def link(self):
        return str(self.__link)  
    
    @property        
    def path(self):
        return str(self.__path) 

    
class MenuSystem():
    def __init__(self):
        self.__context_menu = list()
        
    def insert_item(self, item:MenuContent): 
        self.__context_menu.append(item)
        
    def sync_items(self):
        i = 0
        for item in self.__context_menu:
            item._MenuContent__set_ref_context(i)
            
            print(item)
            
            i+=1
    
    def __presentation(self, content:MenuContent) -> str:
        #cronograma = content.cronogram
        
        #if cronograma is None:
        #    cronograma = 'None' 
        
        return f'num.: {content.num}\ntitle: {content.title}\nlink: {content.link}\ncronograma: \n{content.cronograma}\n'
            
    def info_content(self, ref_context:int) -> str:
        for item in self.__context_menu:
            if item.ref_context == ref_context:
                return self.__presentation(item)
            
        return None
    
    def to_string(self) -> list():
        menu_contents = list()
        for content in self.__context_menu:
            menu_contents.append(
                    f'({content.ref_context}) - {content.num} : {content.title}'
                )
            
        return  menu_contents
        

if __name__ == '__main__':
    msystem = MenuSystem()
    
    mcontents = list()
    for i in range(0, 5):
        mcontents.append(MenuContent(f'num{i}', f'title{i}', f'link{i}', f'path{i}'))
        mcontents[i].set_cronogram(pd.DataFrame())
        
        msystem.insert_item(mcontents[i])

    msystem.sync_items()
    for present in msystem.to_string():
        print(present)
    
    
    