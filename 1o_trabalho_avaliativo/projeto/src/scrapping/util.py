import os

def resolve_sys_path(path:str)->str:
    try:
        os.mkdir(path)
        return True
    except: 
        return  False 
    
if __name__ == '__main__':
    print(resolve_sys_path('./new_path_text'))