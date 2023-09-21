from tkinter import Tk,Label,Entry
from psycopg2.extras import RealDictCursor
import psycopg2

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
    pass

class MainProgram:
    def __init__(self,database,user,password):
        self.database = database
        self.user = user
        self.password = password

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
    mn = MainProgram("fastApi","postgres","9341")
