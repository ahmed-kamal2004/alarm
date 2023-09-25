from tkinter import Tk,Label,Entry,Button,Frame,END,ttk,Listbox
import tkinter as tk
from psycopg2.extras import RealDictCursor
import psycopg2
from typing import List
import threading
import datetime
import os
from pathlib import Path
import threading
import time
from functools import partial


################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################

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
        Label(self.root,text=self.msg,font=("Arial", self.font_size),wraplength=400).pack()
        if self.time != 0:
            self.root.after(self.time*1000,self.root.destroy)
        self.root.mainloop()


################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################



class GetDataModel:
    # to get the data from the user and return it

    def __init__(self,title,font_size,one_time=True):
        self.root = Tk()
        self.root.title(title)
        self.root.geometry("750x300")
        self.font_size = font_size
        self.entries = {}
        self.data = []
        self.one_time = one_time



    def run(self):
        self.fill()
        self.buttons()
        self.clear()
        self.root.mainloop()

    def fill(self):
        pass
    
    def buttons(self):
        style = ttk.Style()
        style.configure('Custom.TButton', 
                foreground='black',  # Text color
                background='#4CAF50',  # Background color
                font=('Helvetica', 10, 'bold'),  # Font settings
                padding=10)  # Padding
        button_frame = Frame(self.root,padx=10,pady=10)
        button_frame.pack()

        add_button = ttk.Button(button_frame, text= "Send"if self.one_time else "Add", command=self.add,style='Custom.TButton')
        add_button.grid(row=0, column=1)
        exit_button = ttk.Button(button_frame, text="Exit", command=self.root.destroy,style='Custom.TButton')
        exit_button.grid(row=0, column=2)
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear,style='Custom.TButton')
        clear_button.grid(row=0, column=3)

    
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
        label = Label(self.root,text="Added ! ")
        label.after(1000,label.destroy)
        label.pack()
        return  

    def clear(self):
        for key,value in self.entries.items():
            value.delete(0,tk.END)
    
    def destroy(self):
        self.root.destroy()
        return 


################################################################################################################################################################


class GetDatabaseData(GetDataModel):
    def __init__(self,title,font_size,one_time=True):
        super().__init__(title,font_size,one_time)


    def fill(self):
        ## DataBase
        Label(self.root,text="database"+ " : ",font=self.font_size).pack()
        self.entries["database"] = Entry(self.root)
        self.entries["database"].pack()

        ## User

        Label(self.root,text="user"+ " : ",font=self.font_size).pack()
        self.entries["user"] = Entry(self.root)
        self.entries["user"].pack()

        ## Password

        Label(self.root,text="password"+ " : ",font=self.font_size).pack()
        self.entries["password"] = Entry(self.root)
        self.entries["password"].pack()
        
        Label(self.root,text=" ",font=self.font_size).pack()


################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################



class MainProgram:
    def __init__(self):

        self.connected=False
        ## Establishing the database
        try:
            file = open("connection.txt", "r+")
        except:
            file = open("connection.txt", "w+")
            file.writelines("False")
            file.seek(0)

        finally:


            path = os.getcwd()
            # print(path)
            lista = file.readlines()
            if not lista:

                file.close()
                os.remove(path+r"\\connection.txt")
                pg = PageMSG(msg="Reconnect Please",time=0,title="Reconnection Request",font_size=20)
                pg.show()
                pass

            elif lista[0] == "False" or lista[0] == "True\n":


                if lista[0] == "False":
                    mn = GetDatabaseData("Get Database Data",12,one_time=True)
                    mn.run()
                    self.database = globals()["data"][-1]["database"]
                    self.user =  globals()["data"][-1]["user"]
                    self.password =  globals()["data"][-1]["password"]
                    del globals()["data"]
                elif lista[0] == "True\n":
                    self.database = lista[1].removesuffix('\n')
                    self.user = lista[2].removesuffix('\n')
                    self.password = lista[3]




                try:
                    self.conn = psycopg2.connect(host='localhost',
                                            database=self.database,
                                            user=self.user,
                                            password=self.password,
                                            cursor_factory=RealDictCursor)
                    self.cursor = self.conn.cursor()
                    self.conn.commit()
                except Exception as e:
                    error_msg = PageMSG(str(e),0,"Sorry!, Error Message",font_size=25)
                    error_msg.show()
                    self.connected = False
                    file.seek(0)
                    file.truncate(0)
                    file.write("False")
                    file.seek(0)
                    file.close()
                else:
                    confirm_msg = PageMSG("Connected !",1,"Good Database Connection Message",font_size=25)
                    confirm_msg.show()
                    self.connected = True

                    self.root = Tk()
                    self.root.title("Welcome, Alarm App !!")
                    self.root.geometry("1020x600")
                    self.hour,self.minute,self.second = 0,0,0
                    self.remainTime = 0
                    self.remainTimeLabel = Label(self.root,font=25)
                    self.first_time = datetime.datetime.now()
                    self.list_data={}
                    self.lista = Listbox(self.root,xscrollcommand=True,width=50,height=10,font=15)
                    self.entries ={}
                    self.thread = None
                    self.make_alram = True
                    self.time_diff=None
                    self.button_close = None
                    self.flag= True
                    self.cursor.execute("""CREATE TABLE IF NOT EXISTS alarm (
                                        id SERIAL PRIMARY KEY,
                                        hour INTEGER NOT NULL,
                                        minute INTEGER NOT NULL,
                                        day INTEGER NOT NULL,
                                        month INTEGER NOT NULL,
                                        year INTEGER NOT NULL
                    );""")
                    self.conn.commit()
                    file.seek(0)
                    file.truncate(0)
                    file.write("True"+'\n')
                    file.write(str(self.database)+'\n')
                    file.write(str(self.user)+'\n')
                    file.write(str(self.password))
                    file.seek(0)
                    file.close()


            else:
                file.close()
                os.remove(path+r"\\connection.txt")
                pg = PageMSG(msg="Reconnect Please",time=0,title="Reconnection Request",font_size=20)
                pg.show()
                pass


    def run(self):
        if self.connected:

            self.fill()
            self.populate()
            ## For threading and Calc the remaining ti
            ##
            self.buttons()
            self.root.mainloop()
    
    def fill(self):
        self.lista.pack()
        self.remainTimeLabel.pack()
        return

    def buttons(self):
        

        ######################################################
        Main_Frame = Frame(self.root,padx=10,pady=10,width = 1020,height=150)
        Main_Frame.pack()
        ### Frame one 
        style = ttk.Style()
        style.configure('Custom.TButton', 
                foreground='black',  # Text color
                background='#4CAF50',  # Background color
                font=('Helvetica', 10, 'bold'),  # Font settings
                padding=20)  # Padding

        button_frame = Frame(Main_Frame,padx=10,pady=30)
        button_frame.grid(row = 0,column=0)

        add_button = ttk.Button(button_frame, text="Add", command=self.add,style='Custom.TButton',padding=5)
        add_button.grid(row=0, column=0)
        exit_button = ttk.Button(button_frame, text="Exit", command=self.root.destroy,style='Custom.TButton',padding=5)
        exit_button.grid(row=1, column=0)
        clear_button = ttk.Button(button_frame, text="Delete", command=self.remove,style='Custom.TButton',padding=5)
        clear_button.grid(row=2, column=0)
        
        ########################################################################
        ## Frame 2


        data_frame = Frame(Main_Frame,padx=10,pady=10)
        data_frame.grid(row=0,column=5)

                        ## Hour
        Label(data_frame,text="Hour"+ " : ",font=5).grid(row=1,column=1)
        self.entries["Hour"] = tk.Spinbox(data_frame, from_=0, to=23, width=5)
        self.entries["Hour"].grid(row=1,column=4)
        ## Minute
        Label(data_frame,text="Minute"+ " : ",font=5).grid(row=2,column=1)
        self.entries["Minute"] = tk.Spinbox(data_frame, from_=0, to=59, width=5)
        self.entries["Minute"].grid(row=2,column=4)

        ### 
        month = datetime.date.today().month
        day = datetime.date.today().day
        year = datetime.date.today().year
        ## Day
        Label(data_frame,text="Day"+ " : ",font=5).grid(row=3,column=1)
        self.entries["Day"] = tk.Spinbox(data_frame, from_=1, to=31 if month in (1, 3, 5, 7, 8, 10, 12) else 28 if month == 2 else 30, width=5)
        self.entries["Day"].grid(row=3,column=4)
        ## Month
        Label(data_frame,text="Month"+ " : ",font=5).grid(row=4,column=1)
        self.entries["Month"] = tk.Spinbox(data_frame, from_=1, to=12, width=5)
        self.entries["Month"].grid(row=4,column=4)
        ## Year
        Label(data_frame,text="Year"+ " : ",font=5).grid(row=5 ,column=1)
        self.entries["Year"] = tk.Spinbox(data_frame, from_=year, to=year+1, width=5)
        self.entries["Year"].grid(row=5,column=4)
        #####################
        Label(data_frame,text=" ",font=5).grid(row=6,column=4)


        ########################################################################

        return

    def add(self):
        data = {}
        for key,value in self.entries.items():
            data[key] = value.get().strip()

        # if "data" in globals().keys(): ### if the user clicked on exit without sending any data
        #     for i in range(len(globals()["data"])):
        hour = data["Hour"]
        minute = data["Minute"]
        day = data["Day"]
        month = data["Month"]
        year = data["Year"]
        # print("A&A")
        # print("in")
        # print(hour,minute,day,month,year,"            ",datetime.datetime.now())
        if datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute)) > datetime.datetime.now():
            self.cursor.execute(f"INSERT INTO alarm (hour, minute, day, month, year) VALUES({int(hour)},{int(minute)},{int(day)},{int(month)},{int(year)});")
            # print(self.cursor.fetchall())
            self.conn.commit()
            label = Label(self.root,text="Added ! ")
            label.after(1000,label.destroy)
            label.pack()
            # print("inseide")
        # print("out")
        self.populate()
        return

    def remove(self):
        for index in self.lista.curselection():
            self.cursor.execute(f"DELETE FROM alarm WHERE id = {self.list_data[index]}")
            self.conn.commit()
        self.populate()
        pass

    def populate(self):
        if self.connected:
            try:
                self.lista.delete(0,END)
            except:
                pass
            self.cursor.execute("SELECT * FROM alarm ORDER BY year ASC,month ASC,day ASC,hour ASC,minute ASC;")
            data = self.cursor.fetchall()
            index = 0
            for row in data:
                self.lista.insert(tk.END,f"         {str(row['hour']).zfill(2)}:{str(row['minute']).zfill(2)}"+"""
                                                """+f"{str(row['day']).zfill(2)}/{str(row['month']).zfill(2)}/{row['year']}")
                self.list_data[index] = row['id']
                index += 1

            ## Get First Alarm
            try:
                self.cursor.execute(f"SELECT * FROM alarm WHERE id = {self.list_data[0]}")
                first_element = self.cursor.fetchall()
                self.first_time = datetime.datetime(year=int(first_element[0]['year']),
                                                    month=int(first_element[0]['month']),
                                                    day=int(first_element[0]['day']),
                                                    hour=int(first_element[0]['hour']),
                                                    minute=int(first_element[0]['minute']),
                                                    second=0)
                # print(1)
                self.make_alram=True
                # print(self.time_diff,"   : ",self.first_time)

                now = datetime.datetime.now().replace(second=59-int(self.second),microsecond=0)
                self.time_diff = self.first_time - now
                # print(self.time_diff,"   : ",self.first_time)
                # print(2)    
                if self.thread:
                    self.flag=False
                    self.thread.join()
                    self.thread = None
                self.flag =True
                self.thread = threading.Thread(target = self.clock)           
                self.thread.start()

                # print("Number of active threads:", threading.active_count())
            except Exception as e:
                # print(e)
                self.first_time=datetime.datetime.now()
                self.time_diff = datetime.timedelta(seconds=0)
                self.update(0,0,0)
                self.make_alram =False
        return


    def update_label(self,hours,minutes,seconds):
            self.remainTimeLabel.config(text=f"Remaining Time: {str(int(hours)).zfill(2)} :  {str(int(minutes)).zfill(2)} : {str(int(seconds)).zfill(2)}")

    def clock(self):
        # print(self.time_diff)
        # print(3)
        self.thread_time=None
        if self.time_diff:
            while self.flag and self.time_diff.total_seconds() > 0:
                # print("Number of active threads:", threading.active_count())
                print(self.time_diff.total_seconds())
                self.time_diff -= datetime.timedelta(seconds=1)
                # print(4,"Hi")
                self.minute = (self.time_diff.total_seconds() % 3600) //60 
                self.hour = self.time_diff.total_seconds() // 3600
                self.second = self.time_diff.total_seconds() % 60 
                #self.thread = threading.Thread(target=self.update, args=(self.hour,self.minute,self.second))
                self.update(self.hour,self.minute,self.second)
                #self.thread.start()  
                # print(int(self.hour), int(self.minute), int(self.second))       
                event = threading.Event()
                event.wait(1)
                if event.is_set():
                    break
            if self.make_alram and self.flag:
                    # print(5)
                    self.cursor.execute(f"DELETE FROM alarm WHERE id = {self.list_data[0]}")
                    self.conn.commit()
                    self.thread_time = threading.Thread(target=self.alarm)
                    self.thread_time.start()
        # print(7)




    def alarm(self):
        label = Label(text="Alarm!",font=25)
        label.pack()

        self.button_close = Button(text="Close", command=partial(self.deletion, label),width=50,height=10,background="white")
        self.button_close.pack()

    def update(self, hours, minutes, seconds):
        self.remainTimeLabel.after(0, self.update_label, hours, minutes, seconds)


    def deletion(self,label):
        label.destroy()
        self.button_close.destroy()
        # print("Before")
        self.populate()
        # print("After")



################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################




if __name__ == "__main__":
    mn = MainProgram()
    mn.run()

    
    
    
