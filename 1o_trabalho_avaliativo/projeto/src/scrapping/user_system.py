#import dataclasses
import pandas as pd
from abc import abstractmethod, abstractproperty
import numpy as np

from .info_graph import InfoGraph

class FormMenuContent():
    def __init__(self, arg):
        self.__arg = arg
        
    def run(self) -> list():
        return self.__arg()

class MenuContent():
    def __init__(self):
        self.__ref_content = -1
        
    def set_ref_context(self, index: int):
        self.__ref_content = index
    
    @property        
    def ref_content(self)->int():
        return self.__ref_content
    
    @abstractproperty
    def type(self):
        pass
    
    @abstractmethod
    def presentation(self):
        pass
    
    @abstractmethod
    def resume(self):
        pass
    
class FigContent(MenuContent):
    def __init__(self, fig:InfoGraph(), title:str='undefined'):
        super().__init__()
        
        self.__fig = fig
        self.__title = title
        
        self.__type = 'fig'
        
    @property        
    def fig(self)->InfoGraph():
        return self.__fig
    
    @property        
    def title(self):
        return self.__title  
    
    @property
    def type(self):
        return self.__type
    
    def presentation(self)->...:
        return self.__fig.show

    def resume(self):
        return f'({self.type}) fig: \t{self.title}'

class ArticleContent(MenuContent):
    def __init__(self, num, title, link, page, path_to):
        super().__init__()
        
        self.__num= num
        self.__title = title
        self.__cronogram = None
        self.__link = link
        self.__page = page
        
        self.__type = 'article'
        
    def set_cronogram(self, cronogram):
        self.__cronogram = cronogram
        
    @property        
    def num(self):
        return self.__num
    
    @property        
    def title(self):
        return self.__title
    
    @property        
    def cronograma(self):
        return self.__cronogram
    
    @property        
    def link(self):
        return self.__link
    
    @property
    def page(self):
        return self.__page
    
    @property
    def type(self):
        return self.__type
    
    def run_presentation(self):
        print(f'num.: {self.num}\ntitle: {self.title}\nlink: {self.link}\ncronograma: \n{self.cronograma}\npage: {self.page}\n')
    
    def presentation(self):
        return self.run_presentation

    def resume(self):
        return f'({self.type}) {self.num} :\t{self.title}'
    
class MenuSystem():
    def __init__(self):
        self.__context_menu = list()
        
    def insert_item(self, item:MenuContent): 
        self.__context_menu.append(item)
        
    def sync_items(self):
        i = 0
        for item in self.__context_menu:
            item.set_ref_context(i)
            
            #print(item)
            
            i+=1
            
    def info_content(self, ref_context:int):
        for item in self.__context_menu:
            if item.ref_content == ref_context:
                return item.presentation()()
            
        return None
    
    def to_string(self) -> list():
        menu_contents = list()
        for content in self.__context_menu:
            menu_contents.append(
                    f'({content.ref_content}) -\t {content.resume()}'
                )
            
        return  menu_contents
        

if __name__ == '__main__':
    msystem = MenuSystem()
    
    mcontents = list()
    for i in range(0, 5):
        mcontents.append(ArticleContent(f'num{i}', f'title{i}', f'link{i}', f'page{i}', f'path{i}'))
        mcontents[i].set_cronogram(pd.DataFrame(columns=['kkk', 's2']))
        
        msystem.insert_item(mcontents[i])

    msystem.sync_items()
    for present in msystem.to_string():
        print(present)
    
    for i in range(0, 5):
        print(msystem.info_content(i))   
    
    
    
    