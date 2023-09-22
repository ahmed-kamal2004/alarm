from tkinter import Tk,Label,Entry,Button,Frame,END,ttk
import tkinter as tk
from psycopg2.extras import RealDictCursor
import psycopg2
from typing import List
# from pydantic import BaseModel



# ###################################################
#             ## Pydantic Models for ReturnedData

# class DataBaseConnectionModel(BaseModel):
#     database:str
#     user:str
#     password:str

#     class Config:
#         from_attribute = True


# class NewDataModel(BaseModel):


#     class Config:
#         from_attribute = True


# ###################################################


class PageMSG:

    def __init__(self,msg,time,title,font_size):
        self.msg = msg
        self.time = time
        self.title = title
        self.root = Tk()
        self.root.title(self.title)
        self.font_size = font_size

    def show(self):

        self.root.geometry("650x250")
        label = Label(self.root,text=self.msg,font=("Arial", self.font_size),wraplength=400).pack()
        if self.time != 0:
            self.root.after(self.time*1000,self.root.destroy)
        self.root.mainloop()




class GetDataPage:
    # to get the data from the user and return it

    def __init__(self,title,lista:List[str],font_size,one_time):
        self.size = len(lista)
        self.root = Tk()
        self.root.title(title)
        self.root.geometry("750x300")
        self.font_size = font_size
        self.lista = lista
        self.entries = {}
        self.data = []
        self.one_time = one_time



    def run(self):
        for i in range(self.size):
            Label(self.root,text=self.lista[i]+ " : ",font=self.font_size).pack()
            self.entries[self.lista[i]] = Entry(self.root)
            self.entries[self.lista[i]].pack()
        
        Label(self.root,text=" ",font=self.font_size).pack()
        
        style = ttk.Style()
        style.configure('Custom.TButton', 
                foreground='black',  # Text color
                background='#4CAF50',  # Background color
                font=('Helvetica', 10, 'bold'),  # Font settings
                padding=20)  # Padding

        button_frame = Frame(self.root)
        button_frame.pack()

        add_button = ttk.Button(button_frame, text= "Send"if self.one_time else "Add", command=self.add,style='Custom.TButton')
        add_button.grid(row=0, column=1)
        exit_button = ttk.Button(button_frame, text="Exit", command=self.root.destroy,style='Custom.TButton')
        exit_button.grid(row=0, column=2)
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear,style='Custom.TButton')
        clear_button.grid(row=0, column=3)
        self.root.mainloop()


    
    def add(self):
        data ={}
        for key,value in self.entries.items():
            data[key] = value.get().strip()
        self.data.append(data)
        globals()["data"] = self.data  
        self.clear()
        if self.one_time:
            self.destroy()
        return  

    def clear(self):
        for key,value in self.entries.items():
            value.delete(0,tk.END)
    
    def destroy(self):
        self.root.destroy()

class MainProgram:
    def __init__(self):


        ## Establishing the database


        lista = ["database","user","password"]
        mn = GetDataPage("Get Database Data",lista,12,one_time=True)
        mn.run()
        self.database = globals()["data"][-1]["database"]
        self.user =  globals()["data"][-1]["user"]
        self.password =  globals()["data"][-1]["password"]
        del globals()["data"]


        try:
            self.conn = psycopg2.connect(host='localhost',
                                    database=self.database,
                                    user=self.user,
                                    password=self.password,
                                    cursor_factory=RealDictCursor)
            self.cursor = self.conn.cursor()

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS to_do_list(
                           id SERIAL PRIMARY KEY,
                           title character varying(1000) NOT NULL,
                           content character varying(3000) NOT NULL,
                           time TIMESTAMP NOT NULL,
                           day INTEGER NOT NULL,
                           year INTEGER NOT NULL
            );""")
            self.conn.commit()

        except Exception as e:
            error_msg = PageMSG(str(e),0,"Sorry!, Error Message",font_size=25)
            error_msg.show()
            self.connected = False
        else:
            confirm_msg = PageMSG("Well Done !",1,"Good Database Connection Message",font_size=25)
            confirm_msg.show()
            self.connected = True

    # Data I have : self.connected,self.conn,self.cursor


    def mainCycle(self):
        pass



if __name__ == "__main__":
    # lista = ["Name","year","Link"]
    # mn = GetDataPage("Add New Task",lista,12)
    # mn.run()
    # print(globals()["data"])
    # del globals()["data"]
    # print(globals()["data"])
    mn = MainProgram()
    
    
    
