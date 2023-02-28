from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import Screen
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from kivymd.uix.datatables import MDDataTable
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivymd.uix.screen import MDScreen
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
import psycopg2
import pandas as pd
import datetime
import numpy as np
import sqlite3
import random
import bcrypt
import re

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import hvac

# Button:
# 			text: "Next Screen"
# 			font_size: 32
# 			on_release: 
# 				app.root.current = "main"
# 				root.manager.transition.direction = "left"

# Authentication
client = hvac.Client(
    url='http://65.1.135.73:8200',
    token='tdc-token',
)

read_response = client.secrets.kv.read_secret_version(path='postgresdb')

POSTGRES_CREDIANTIALS = [[
        '15.206.171.33', 
        f"{read_response['data']['data']['dbname']}", 
        f"{read_response['data']['data']['dbusername']}", 
        f"{read_response['data']['data']['dbpassword']}"
]]

class SettingScreen(MDScreen):
   
    pass

class AboutScreen(MDScreen):
    
    pass

class LoginScreen(MDScreen):
    def logger(self):
        if len(self.ids.username.text) == 0 and len(self.ids.userpassword.text) == 0:
            self.dialog = MDDialog(
				    title = "Enter valid username or password !!!",
				    text = "Please recheck .......",
				    buttons =[
					MDFlatButton(
						text="OK", text_color=self.theme_cls.primary_color, on_release = self.closedialog
						),
					
					],
				    )
            self.dialog.open()
        else:
            conn = None
            try:
                # connect to the PostgreSQL server
                print('Connecting to the PostgreSQL database...')
                for f in POSTGRES_CREDIANTIALS:
                    conn = psycopg2.connect(
                                            host= f[0],
                                            database= f[1],
                                            user= f[2],
                                            password= f[3]
                                                )
                cur = conn.cursor()
                cur.execute(f"SELECT password = crypt('{self.ids.userpassword.text}', password) from emplogin where user_name = '{self.ids.username.text}'")
                checkemployee = cur.fetchone()
                if checkemployee[0]:
                    self.ids.userpassword.text = ''
                    self.dialog = MDDialog(
                            title = "welcome",
                            text = f"Logged in....... {self.ids.username.text}",
                            buttons =[
                            MDFlatButton(
                                text="OK", text_color=self.theme_cls.primary_color, on_release = self.closedialog                            ),
                            
                            ],
                            )
                        
                    self.manager.current = 'main'
                    self.manager.transition.direction = 'left'
                    self.dialog.open()
                else:
                    self.dialog = MDDialog(
                        title = "User Name or password incorrect!!!",
                        text = "Please recheck .......",
                        buttons =[
                        MDFlatButton(
                            text="OK", text_color=self.theme_cls.primary_color, on_release = self.closedialog
                            ),
                        
                        ],
                        )
                    self.dialog.open()

                conn.commit()

                    # close the communication with the PostgreSQL
                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                if conn is not None:
                    conn.close()
                print('Database connection closed.')
            print(self.ids.username.text)
            print('success')
            print(self.ids.userpassword.text)
    def closedialog(self, obj):
        self.dialog.dismiss()
                    

class MainScreen(MDScreen):
    def setupdf(self):
        conn = None
        try:
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            for f in POSTGRES_CREDIANTIALS:
                conn = psycopg2.connect(
                                        host= f[0],
                                        database= f[1],
                                        user= f[2],
                                        password= f[3]
                                            )
            #conn = sqlite3.connect("test.db")
                # create a cursor
            cur = conn.cursor()
                
                # display the PostgreSQL database server version
            cur.execute("SELECT * FROM product")
            product_values = cur.fetchall()
            #print(product_values)
            cur.execute("SELECT * FROM discount")
            discounted = cur.fetchall()
            #print(discounted)
            self.df = pd.DataFrame(product_values,columns =['product_id','product_name','description','stock','price','category','supplier_id','stock_threshold'])
            #print(df)
            df1 = pd.DataFrame(discounted,columns=["promotionid","startdate","enddate","productid","percentage"])

            self.joineddf = self.df.join(df1.set_index('productid'),on='product_id')
            self.joineddf['enddates'] = pd.to_datetime(self.joineddf['enddate']).dt.date
            self.joineddf['startdates'] = pd.to_datetime(self.joineddf['startdate']).dt.date
            today = datetime.datetime.today()
            self.joineddf.loc[(datetime.date(today.year,today.month,today.day) >= self.joineddf.startdates) & (datetime.date(today.year,today.month,today.day)<= self.joineddf.enddates), 'percentages'] = self.joineddf["percentage"]
            self.joineddf['percentages'] = self.joineddf['percentages'].fillna(0)
            print(self.joineddf)
            self.dfw = pd.DataFrame(columns =["ProductName","Price","Category"
            ,"Quantity","Discount","DiscountedPrice","TotalPrice"])
            print(self.dfw)
            #print(df)
            #print(product_values)
            conn.commit()

                # close the communication with the PostgreSQL
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')
    def tables(self):
        
        self.data_tables = MDDataTable(
            size_hint=(0.4, 0.4),
            use_pagination = True,
            #check = True,
            pos_hint= {'center_x': 0.5,'center_y':0.75},
            pagination_menu_height = '240dp',
            
            #pos_hint={'center_x':0.5,'center_y':0.5},
            # name column, width column
            column_data=[
                ("Category", dp(20)),
                ("Product Name", dp(60)),
                ("Price", dp(20)),
                
            ],
        )
        self.data_tablestest = MDDataTable(
            size_hint= (0.75,0.4) ,
            use_pagination = True,
            pos_hint= {'center_x': 0.6,'center_y':0.3},
            pagination_menu_height = '240dp',
            #check = True,
            #pos_hint={'center_x':0.5,'center_y':0.5},
            # name column, width column ["Product_Name","Price", "Category","Quantity","Discount","DiscountedPrice","TotalPrice"]
            column_data=[
                ("Product Name", dp(60)),
                ("Price", dp(20)),
                ("Category", dp(20)),
                ("Quantity", dp(20)),
                ("Discount", dp(20)),
                ("DiscountedPrice", dp(30)),
                ("TotalPrice", dp(20)),
                
            ],
        )
        self.data_tablestest.bind(on_row_press=self.on_row_press)
        self.add_widget(self.data_tables)
        self.add_widget(self.data_tablestest)

        #self.data_tables.open()
    
    

    def on_row_press(self, instance_table,instance_row):
        print("selected row data ",instance_row)
        #start_index, end_index = instance_row.instance_table.recycle_data[instance_row.index]["range"]
        #print(current_row)
        #self.data_tablestest.remove_row(current_row)
    #     print(end_index)
    # # loop over selected row items
    #     for i in range(start_index, end_index):
    #         print(row.table.recycle_data[i]["text"])
    def on_enter(self):
        self.setupdf()
        self.tables()
        
        self.ids.search.focus = True
    
    def askqty(self):
        self.dialog = MDDialog(
                size_hint_x = None,
                size_hint_y=None,
				height=40,
                
                width=150,
                
                type = "custom",
                content_cls = Content(),
				
                #on_open = self.dialog.content_cls.ids.qty.focus = True
				)
        if self.ids.search.text == '' or len(self.data_tables.row_data) == 0 or self.data_tables.row_data[0][1][0] == 'alert-circle' or self.data_tables.row_data[0][1][2] in self.dfw.values:
            self.ids.search.text = ''
            self.ids.search.focus = True
        else:
            self.dialog.open()
        
# Click Cancel Button

    def close_dialog(self, obj):
		# Close alert box
        self.dialog.dismiss()
	
	# Click the Neat Button
    def getqty(self):
		# Close alert box
        self.dialog.dismiss()
		# Change label text
        self.getrecord(self.dialog.content_cls.ids.qty.text)
        self.ids.search.text = ''
        self.ids.search.focus = True

    def getrecord(self, quantity):

        print('User quantity', quantity)
        print('fetched data', self.data_tables.row_data[0][1][0])
        if len(quantity) >=1 :
            self.toadd = []
            self.toadd.extend([self.data_tables.row_data[0][1][2], self.data_tables.row_data[0][2], self.data_tables.row_data[0][0]])
            
            disc = self.joineddf['percentages'][self.joineddf['product_name'] == self.data_tables.row_data[0][1][2]].to_string(index=False)
            print('discount',disc)
            getdis = f"0.{disc if int(disc) >= 10 else '0'+disc}"
            #print("getdis:",float(getdis))
            dis = int(self.data_tables.row_data[0][2]) - (float(getdis)*int(self.data_tables.row_data[0][2]))
            print("discountprice",dis)
            #getqty()
            
            #print("quantity",qty1.get())
            totalprice = round(dis) * int(quantity)
            #print("totalprice",totalprice)
            #getl = [f for f in treev.item(item,'values')]
            #print(getl)
            self.toadd.extend([quantity,f"{disc}%",dis,totalprice])
            #toadd.extend([treev.item(item,'values'),])
            print(self.toadd)
            #self.dfw.loc[len(self.dfw)] = self.toadd
            # for drows in self.data_tablestest.row_data:
            #     self.data_tablestest.remove_row(drows)
            # for row in self.dfw.values.tolist():
            if self.data_tables.row_data[0][1][0] == "checkbox-marked-circle" or self.data_tables.row_data[0][1][0] == "alert":
                self.adddata()
            print()
            totallist = []
            # totallist.clear()
            # #print(int(treev.item(item,'values')[1]))
            for child in self.data_tablestest.row_data:
                totallist.append(child[6])
            self.ids.showtotal.text = str(sum(totallist))
            print(sum(totallist))
                # self.data_tablestest.add_row(self.toadd)

            

            
            
        
    def adddata(self):
        adddict = {"ProductName":self.toadd[0],"Price":self.toadd[1],"Category":self.toadd[2],"Quantity":self.toadd[3],"Discount":self.toadd[4],"DiscountedPrice":self.toadd[5],"TotalPrice":self.toadd[6]}
        
        self.dfw = self.dfw.append(adddict, ignore_index = True)
        print("after added", self.dfw)
        # print("row data",self.data_tablestest.row_data)
        while len(self.data_tablestest.row_data) >= 1:
            self.data_tablestest.remove_row(self.data_tablestest.row_data[-1])
        for row in self.dfw.values.tolist():
            self.data_tablestest.add_row(row)

        # for drows in self.data_tablestest.row_data:
        #     print(drows)
            #self.data_tablestest.remove_row(drows)

        # for rows in self.data_tablestest.row_data:
        #     print(rows)
        #     self.data_tablestest.remove_row(rows)
        # # 
        # 
        # for rows in self.data_tablestest.row_data:
        #     print(rows)
            #self.data_tablestest.remove_row(rows)
        
        # 
        #     print("test")
        #     self.data_tablestest.remove_row(self.data_tablestest.row_data[0])

        
        #     totallist.append(tree_add.item(child)["values"][6])
        #     print(totallist)
        #     print(sum(totallist))
        #     totalentry.config(state="normal")
        #     totalentry.delete(0,'end')
        #     totalentry.insert(0,sum(totallist))
        #     totalentry.config(state="readonly")
    def dddd(self, value):
        print('have:', value, len(value))
        # for drows in self.data_tables.row_data:
        #     self.data_tables.remove_row(drows)
        while len(self.data_tables.row_data) >= 1:
            self.data_tables.remove_row(self.data_tables.row_data[-1])
        for row in self.df[[value in x.lower() for x in self.df['product_name']]][["product_name","price","category","stock","stock_threshold"]].values.tolist():
            if int(row[3]) == 0:
                self.data_tables.add_row((row[2],("alert-circle", [1, 0, 0, 1],row[0]), row[1]))
            elif int(row[3]) <= int(row[4]):
                self.data_tables.add_row((row[2],("alert", [255 / 256, 165 / 256, 0, 1], row[0]),row[1]))
            else:
                self.data_tables.add_row((row[2],("checkbox-marked-circle",[39 / 256, 174 / 256, 96 / 256, 1], row[0]),row[1]))
                #
    
    def searchdelete(self,value):
        # rowlist = []
        # totallist = []
        # for rows in self.data_tablestest.row_data:
        #     rowlist.append(rows)

        while len(self.data_tablestest.row_data) >= 1:
            self.data_tablestest.remove_row(self.data_tablestest.row_data[-1])
        
        
        for row in self.dfw.values.tolist():
            if value in row[0].lower():
                self.data_tablestest.add_row(row)
               # self.data_tablestest.remove_row(rows)
        # for child in self.data_tablestest.row_data:
        #      totallist.append(child[6])
        # self.ids.showtotal.text = str(sum(totallist))
                
        
        def deselect_rows(*args):
            self.data_tablestest.table_data.select_all("normal")
        checked = []

        # for data in self.data_tablestest.get_row_checks():
        #     checked.append(data)
        
        # for data in checked:
        #     self.data_tablestest.remove_row(data)
        # 
        # totallist.clear()
        # #print(int(treev.item(item,'values')[1]))
        # for child in self.data_tablestest.row_data:
        #     totallist.append(child[6])
        # self.ids.showtotal.text = str(sum(totallist))
        #     #print(data)

        #Clock.schedule_once(deselect_rows)
    
    def deleterows(self):
        self.updateqtydialog = MDDialog(
                size_hint_x = None,
                size_hint_y=None,
				height=40,
                
                width=150,
                
                type = "custom",
                content_cls = UpdateQty(),
				
                #on_open = self.dialog.content_cls.ids.qty.focus = True
				)
        if len(self.data_tablestest.row_data) >=1:
            self.updateqtydialog.open()
        else:
            pass
    def getqtyupdate(self):
        qty = self.updateqtydialog.content_cls.ids.updateqty.text
        if  qty == '':
            self.updateqtydialog.dismiss()
            index = self.dfw[self.dfw['ProductName'] == self.data_tablestest.row_data[0][0]].index
            self.dfw.drop(index, inplace = True)
            print("after dropped",self.dfw)
            while len(self.data_tablestest.row_data) >= 1:
                self.data_tablestest.remove_row(self.data_tablestest.row_data[-1])
            for row in self.dfw.values.tolist():
                self.data_tablestest.add_row(row)
            #print(self.data_tablestest.row_data[0])
            totallist = []
            # # totallist.clear()
            # # #print(int(treev.item(item,'values')[1]))
            for child in self.data_tablestest.row_data:
                totallist.append(child[6])
            self.ids.showtotal.text = str(sum(totallist))
            #self.data_tablestest.remove_row(self.data_tablestest.row_data[0])  
            self.ids.deletesearch.text = ''
            self.ids.deletesearch.focus = True
            print("deleted")
        else:
            print("before update", self.dfw)
            updaterow = self.data_tablestest.row_data[0]
            discountpercent = self.dfw.loc[(self.dfw.ProductName == updaterow[0]), 'Discount'].values.astype(str)
            discount =''
            price = self.dfw.loc[(self.dfw.ProductName == updaterow[0]), 'Price'].values.astype(str)
            if len(discountpercent[0].split('%')[0]) == 1:
                discount = f"0.0{discountpercent[0].split('%')[0]}"
            else:
                discount = f"0.{discountpercent[0].split('%')[0]}"
            
            discountprice = int(price) - (float(discount) * int(price))

            totalprice = int(discountprice) * int(qty)
            print(discountprice, totalprice, qty)
            for check in [updaterow[0]]:
                print(check)
                self.dfw.loc[(self.dfw.ProductName == check), 'Quantity'] = qty
                self.dfw.loc[(self.dfw.ProductName == check), 'DiscountedPrice'] = discountprice
                self.dfw.loc[(self.dfw.ProductName == check), 'TotalPrice'] = totalprice
            
            # print(self.dfw.loc[(self.dfw.ProductName == updaterow[0]), 'Discount'].values.astype(str))
            # print(self.dfw.loc[(self.dfw.ProductName == updaterow[0]), 'Price'])
            # self.dfw.loc[(self.dfw.ProductName == updaterow[0]), 'Quantity'] = qty
            self.updateqtydialog.dismiss()

            self.ids.deletesearch.text = ''
            self.ids.deletesearch.focus = True
            while len(self.data_tablestest.row_data) >= 1:
                self.data_tablestest.remove_row(self.data_tablestest.row_data[-1])
            for row in self.dfw.values.tolist():
                self.data_tablestest.add_row(row)
            totallist = []
            # # totallist.clear()
            # # #print(int(treev.item(item,'values')[1]))
            for child in self.data_tablestest.row_data:
                totallist.append(child[6])
            self.ids.showtotal.text = str(sum(totallist))
            self.ids.deletesearch.text = ''
            self.ids.deletesearch.focus = True
            # self.data_tablestest.update_row(
            # self.data_tablestest.row_data[0],  # old row data
            # [updaterow[0], updaterow[1], updaterow[2], qty, updaterow[4], updaterow[5], updaterow[6]])
            # print('updated')
          

    def sale(self):
        self.saledialog = MDDialog(
            height=300,
            width=650,
            size_hint_x= None,
            size_hint_y= None,
            type = "custom",
            content_cls = Salecontent(),
            buttons =[
                MDFlatButton(
                    text="CANCEL", text_color=self.theme_cls.primary_color, on_release = self.saledclose
                    ),
            ]
            )
        self.saledialog.content_cls.ids.cuscheck.focus = True
        self.saledialog.open()

    def customercheck(self, value):
        for f in POSTGRES_CREDIANTIALS:
            conn = psycopg2.connect(
                                    host= f[0],
                                    database= f[1],
                                    user= f[2],
                                    password= f[3]
                                        )
        # create a cursor
        cur = conn.cursor()
        #print(type(value))
        t = 't'
        if value.isdigit():
            cur.execute(f""" select *  from (SELECT customer_id,check_customer = crypt(CAST ({value} AS VARCHAR),check_customer) as "check" from customer) as ss where "check" """)
            checkcustomer = cur.fetchall()
        else:
            cur.execute(f"""select *  from (SELECT customer_id,check_customer = crypt('{value}',check_customer) 
            as "check" from customer) as ss where 
            "check"
            """)
            checkcustomer = cur.fetchall()
        print(checkcustomer)
        if len(checkcustomer) == 0:
            self.saledialog.content_cls.ids.fabadd.disabled = False
            self.saledialog.content_cls.ids.showicon.icon = "close-circle"
            self.saledialog.content_cls.ids.showicon.icon_color = "#ff0000"

        else:
            self.saledialog.content_cls.ids.fabadd.disabled = True
            self.saledialog.content_cls.ids.showicon.icon = "check-decagram"
            self.saledialog.content_cls.ids.showicon.icon_color = "#00ff00"
        # if value.isdigit():
        #     cur.execute("select phone_no from customer")
        #     phonenumber = cur.fetchall()
        #     print(phonenumber)
        #     if len(phonenumber) == 0:
        #         self.saledialog.content_cls.ids.fabadd.disabled = False
        #         self.saledialog.content_cls.ids.showicon.icon = "close-circle"
        #         self.saledialog.content_cls.ids.showicon.icon_color = "#ff0000"
        #     else:

        #         for no in phonenumber:
        #             if re.search(r"\|\|(.*)\|\|", no[0]) == None:
        #                 pass
        #             else:
                        
        #                 #
        #                 gethash = re.search(r"\|\|(.*)\|\|", no[0]).group(1).encode('utf-8')
        #                 print(gethash)
        #                 #createhash = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
        #                 #print(gethash, value.encode('utf-8'))
        #                 if bcrypt.checkpw(value.encode('utf-8'), gethash):
        #                     self.saledialog.content_cls.ids.fabadd.disabled = True
        #                     self.saledialog.content_cls.ids.showicon.icon = "check-decagram"
        #                     self.saledialog.content_cls.ids.showicon.icon_color = "#00ff00"
        #                     break
        #                 else:
        #                     self.saledialog.content_cls.ids.fabadd.disabled = False
        #                     self.saledialog.content_cls.ids.showicon.icon = "close-circle"
        #                     self.saledialog.content_cls.ids.showicon.icon_color = "#ff0000"

        #             # print(re.search(r"\|\|(.*)\|\|", no[0]).group(1))
        #     # if len(check) == 0:
        #     #     
        #     # else:
        #     #     
        # else:
        #     cur.execute("select customer_mail from customer")
        #     email = cur.fetchall()
        #     if len(email) == 0:
        #         self.saledialog.content_cls.ids.fabadd.disabled = False
        #         self.saledialog.content_cls.ids.showicon.icon = "close-circle"
        #         self.saledialog.content_cls.ids.showicon.icon_color = "#ff0000"
        #     else:

        #         for mail in email:
        #             if re.search(r"\|\|(.*)\|\|", mail[0]) == None:
        #                 pass
        #             else:
                        
        #                 #
        #                 gethash = re.search(r"\|\|(.*)\|\|", mail[0]).group(1).encode('utf-8')
        #                 print(gethash)
        #                 #createhash = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
        #                 #print(gethash, value.encode('utf-8'))
        #                 if bcrypt.checkpw(value.encode('utf-8'), gethash):
        #                     self.saledialog.content_cls.ids.fabadd.disabled = True
        #                     self.saledialog.content_cls.ids.showicon.icon = "check-decagram"
        #                     self.saledialog.content_cls.ids.showicon.icon_color = "#00ff00"
        #                     break
        #                 else:
        #                     self.saledialog.content_cls.ids.fabadd.disabled = False
        #                     self.saledialog.content_cls.ids.showicon.icon = "close-circle"
        #                     self.saledialog.content_cls.ids.showicon.icon_color = "#ff0000"

            #. if len(check) == 0:
            #     self.saledialog.content_cls.ids.fabadd.disabled = False
            #     self.saledialog.content_cls.ids.showicon.icon = "close-circle"
            #     self.saledialog.content_cls.ids.showicon.icon_color = "#ff0000"
            # else:
            #     self.saledialog.content_cls.ids.fabadd.disabled = True
            #     self.saledialog.content_cls.ids.showicon.icon = "check-decagram"
            #     self.saledialog.content_cls.ids.showicon.icon_color = "#00ff00"
        conn.commit()
        cur.close()
        conn.close()
           

        
    def newcust(self):
        self.newcustdialog = MDDialog(
            height= 300,
            size_hint_x = None,
            width=300,
            size_hint_y=None,
            type = "custom",
            content_cls = Newcustomeradd(),
        )
        checked_details = self.saledialog.content_cls.ids.cuscheck.text
        if checked_details.isdigit():
            self.newcustdialog.content_cls.ids.custphonenumber.text = checked_details
        else:
            self.newcustdialog.content_cls.ids.custemail.text = checked_details
        self.newcustdialog.open()
    
    def newcustadd(self, value):
        print()
        print(value)
    
    def addcustomer(self):
        
        cn = self.newcustdialog.content_cls.ids.custname.text
        cpn = self.newcustdialog.content_cls.ids.custphonenumber.text
        cm = self.newcustdialog.content_cls.ids.custemail.text
        ca = self.newcustdialog.content_cls.ids.custaddress.text
        # def EncryptText(TextToBeEncrypted):
        #     Shifter = random.randint(-10, 11)
        #     EncryptedData = ''
        #     for x in range(abs(Shifter)):
        #         RandomAscii = random.randint(10,500)
        #         print(chr(RandomAscii))
        #         if RandomAscii == ord("'") or RandomAscii == ord('"'):
        #             print("found")
        #             pass
        #         else:
        #             EncryptedData = EncryptedData + chr(RandomAscii)
        #     for Index in range(len(TextToBeEncrypted)):
        #         if Index % 2 == 0:
        #             EncryptedChar = chr(ord(TextToBeEncrypted[Index]) + Shifter) 
        #             EncryptedData = EncryptedData + EncryptedChar
        #         else:
        #             EncryptedChar = chr(ord(TextToBeEncrypted[Index]) - Shifter)
        #             EncryptedData = EncryptedData + EncryptedChar
        #     for x in range(abs(Shifter)):
        #         RandomAscii = random.randint(10,500)
        #         print(chr(RandomAscii))
        #         if RandomAscii == ord("'") or RandomAscii == ord('"'):
        #             pass
        #         else:
        #             EncryptedData = EncryptedData + chr(RandomAscii)
        #     text = TextToBeEncrypted.encode('utf-8')
        #     hashed = bcrypt.hashpw(text, bcrypt.gensalt()) 
        #     EncryptedData = f"||{hashed.decode()}||{EncryptedData}({str(Shifter)})"
        #     # EncryptedData = EncryptedData+'('+str(Shifter)+")"
        #     return EncryptedData

        if len(cn and cpn and cm and ca) >= 1:
            print(read_response['data']['data']['dbpkey'])
            for f in POSTGRES_CREDIANTIALS:
                conn = psycopg2.connect(
                                    host= f[0],
                                    database= f[1],
                                    user= f[2],
                                    password= f[3]
                                        )
            # create a cursor
            cur = conn.cursor()
            cur.execute(f"""INSERT INTO customer (customer_id, customer_name, phone_no, address, customer_mail, check_customer)
                                VALUES
                                    (
                                        concat('CUS', nextval('customer_id_seq')),
                                        '{cn}',
                                        pgp_pub_encrypt ('{cpn}',dearmor('{read_response['data']['data']['dbpkey']}')),
                                        pgp_pub_encrypt ('{ca}', dearmor('{read_response['data']['data']['dbpkey']}')),
                                        pgp_pub_encrypt ('{cm}', dearmor('{read_response['data']['data']['dbpkey']}')),
                                        crypt('{self.saledialog.content_cls.ids.cuscheck.text}', gen_salt('bf'))
                                        )""")

            conn.commit()
            cur.close()
            conn.close()

#             e_cn = EncryptText(cn)
#             e_cpn = EncryptText(cpn)
#             e_cm = EncryptText(cm)
#             e_ca = EncryptText(ca)

#             for f in POSTGRES_CREDIANTIALS:
#                 conn = psycopg2.connect(
#                                     host= f[0],
#                                     database= f[1],
#                                     user= f[2],
#                                     password= f[3]
#                                         )
#             # create a cursor
#             cur = conn.cursor()
#             print(e_ca)
#             print(e_cm)
#             print(e_cn)
#             print(e_cpn)

#             cur.execute(f"""INSERT INTO customer (customer_id, customer_name, phone_no, address, customer_mail)
# VALUES
# 	(
# 		'steven',
# 		pgp_pub_encrypt (
# 			'steven@gmail.com',
# 			dearmor ( '-----BEGIN PGP PUBLIC KEY BLOCK-----
# 				this is where you paste your public key
# 				-----END PGP PUBLIC KEY BLOCK-----
# 			' )),
# 		pgp_pub_encrypt (
# 			'4114423232323332',
# 			dearmor ( '-----BEGIN PGP PUBLIC KEY BLOCK-----
# 				this is where you paste your public key
# 			-----END PGP PUBLIC KEY BLOCK-----
# 	' )))""")

#             cur.execute(f"""INSERT INTO 
#                     customer(customer_id, customer_name, phone_no, address, customer_mail)
#                             VALUES
#                         (concat('CUS', nextval('customer_id_seq')),'{e_cn}','{e_cpn}','{e_ca}','{e_cm}')""")
#             conn.commit()
#             cur.close()
#             conn.close()
            self.newcustdialog.dismiss()
        


    def saledclose(self, obj):
        self.saledialog.dismiss()

    def invoicecreation(self):
        # -*- coding: utf-8 -*-
        """
        Created on Thu Feb 23 15:56:34 2023

        @author: ANSHIT
        """

        from fpdf import FPDF
        for f in POSTGRES_CREDIANTIALS:
                conn = psycopg2.connect(
                                        host= f[0],
                                        database= f[1],
                                        user= f[2],
                                        password= f[3]
                                            )
            # create a cursor
        cur = conn.cursor()
        if self.saledialog.content_cls.ids.cuscheck.text.isdigit():
            cur.execute(f'select *  from (SELECT customer_name,check_customer = crypt(CAST ({self.saledialog.content_cls.ids.cuscheck.text} AS VARCHAR),check_customer) as "check" from customer) as ss where "check"')
            cusid = cur.fetchall()
        else:
            cur.execute(f""" select *  from (SELECT customer_name,check_customer = crypt('{self.saledialog.content_cls.ids.cuscheck.text}',check_customer) as "check" from customer) as ss where "check" """)
            cusid = cur.fetchall()
        cur.execute("select concat('INV',currval('salesamount_id_seq'))")
        curinv = cur.fetchall()
        print('customerid',cusid[0][0])
        CustomerName = cusid[0][0]
        ConatctNumber = self.saledialog.content_cls.ids.cuscheck.text
        Address = '-'
        InvoiceNumber = curive[0]
        InvoiceDate = str(datetime.datetime.now())
        itemslist = []
        pdflist = []
        i = 0
        for row in self.data_tablestest.row_data:
            
            i = i+1
            itemslist.append([i,row[3],row[6],proid[0]])

        for items in itemslist:
            pdflist.append({"description": f"Pr {items[0]}", "quantity": f"{items[1]}", "price": f"{items[2]}", "Product Name": f"{items[3]}"})


        # Items = [
        #     {"description": "Item 1", "quantity": 2, "price": 10.0, "Product Name": "PRD123"},
        #     {"description": "Item 2", "quantity": 1, "price": 20.0, "Product Code": "PRD123"},
        #     {"description": "Item 3", "quantity": 3, "price": 5.0, "Product Code": "PRD123"},
        # ]

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", size=25, style = 'B')

        pdf.cell(100, 10, txt="Invoice", align="L")
        pdf.cell(40, 10, txt="\t", align="L")

        pdf.set_font("Arial", size=12)

        pdf.cell(50, 10, txt=f"Invoice Number: {InvoiceNumber}", ln=1, align="R")
        pdf.cell(190, 10, txt=f"Invoice Date: {InvoiceDate}", ln=1, align="R")

        pdf.line(10, 30, 200, 30)
        pdf.set_font("Arial", size=15, style = 'B')

        pdf.cell(200, 10, txt=f"Billing Information", ln=1, align="L")

        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt=f"Customer Name: {CustomerName}", ln=0.5, align="L")
        pdf.cell(200, 10, txt=f"Contact Number: {ConatctNumber}", ln=0.5, align="L")
        pdf.cell(200, 10, txt=f"Address: {Address}", ln=0.5, align="L")
        pdf.cell(200, 10, txt="", ln=1)

        pdf.cell(50, 10, txt="Product Code", border=1)
        pdf.cell(50, 10, txt="Product Name", border=1)
        pdf.cell(30, 10, txt="Quantity", border=1)
        pdf.cell(30, 10, txt="Price", border=1)
        pdf.cell(30, 10, txt="Total", border=1)
        pdf.cell(10, 10, txt="", ln=1)

        total_price = 0

        for item in pdflist:
            pdf.cell(50, 10, txt=Item["Product Name"], border=1)
            pdf.cell(50, 10, txt=Item["description"], border=1)
            pdf.cell(30, 10, txt=str(Item["quantity"]), border=1)
            pdf.cell(30, 10, txt=str(Item["price"]), border=1)
            total = Item["quantity"] * Item["price"]
            total_price += total
            pdf.cell(30, 10, txt=str(total), border=1)
            pdf.cell(10, 10, txt="", ln=1)

        pdf.cell(110, 10, txt="")
        pdf.cell(30, 10, txt="")
        pdf.cell(200, 10, txt="", ln=1)

        pdf.set_font("Arial", size=15, style ='B')

        pdf.cell(30, 10, txt="")
        pdf.cell(30, 10, txt="")
        pdf.cell(30, 10, txt="")
        pdf.cell(30, 10, txt="")
        pdf.cell(30, 10, txt="Total:", align = 'R')
        pdf.cell(30, 10, txt=str(total_price), align = 'L')

        pdf.output("invoice.pdf")
        conn.commit()
        cur.close()
        conn.close()

    def salescomplete(self):
        if self.saledialog.content_cls.ids.camount.text == '' or self.saledialog.content_cls.ids.cuscheck.text == '' or self.saledialog.content_cls.ids.showicon.icon == "close-circle" or len(self.data_tablestest.row_data) == 0:
            pass
        else:

            for f in POSTGRES_CREDIANTIALS:
                conn = psycopg2.connect(
                                        host= f[0],
                                        database= f[1],
                                        user= f[2],
                                        password= f[3]
                                            )
            # create a cursor
            cur = conn.cursor()
            prlist = []
            for products in self.data_tablestest.row_data:
                cur.execute(f"select product_id from product where product_name = '{products[0]}'")
                prlist.append([cur.fetchone()[0]])

            print(prlist)
            # ids = ''
            # for pr,qt in prlist:
            #     ids = f"{ids}{{'{pr}','{qt}'}},"

            # ids = '{'+ids+'}'
            # print(ids)
            print(self.saledialog.content_cls.ids.tamount.text)
            print(self.saledialog.content_cls.ids.camount.text)
            print(self.saledialog.content_cls.ids.sbalance.text)
            if self.saledialog.content_cls.ids.cuscheck.text.isdigit():
                cur.execute(f'select *  from (SELECT customer_id,check_customer = crypt(CAST ({self.saledialog.content_cls.ids.cuscheck.text} AS VARCHAR),check_customer) as "check" from customer) as ss where "check"')
                cusid = cur.fetchall()
            else:
                cur.execute(f""" select *  from (SELECT customer_id,check_customer = crypt('{self.saledialog.content_cls.ids.cuscheck.text}',check_customer) as "check" from customer) as ss where "check" """)
                cusid = cur.fetchall()
            print('customerid',cusid[0][0])

            
            cur.execute(f"""INSERT INTO 
            SALESINVOICE(salesinvoice_id, total_amount, amount_taken, change)
                VALUES
            (concat('SAI', nextval('salesamount_id_seq')),'{self.saledialog.content_cls.ids.tamount.text}','{self.saledialog.content_cls.ids.camount.text}','{self.saledialog.content_cls.ids.sbalance.text}')""")
            
            cur.execute("SELECT currval('salesamount_id_seq')")
            cursalesinvoiceid = cur.fetchone()
            cur.execute(f"select employee_id from emplogin where user_name = '{self.manager.get_screen('Login').ids.username.text}'")
            empid= cur.fetchone()

            cur.execute("SELECT nextval('sales_id_seq')")
            cursalesid = cur.fetchone()

            curdate = datetime.datetime.now()

            for pid in prlist:
                cur.execute(f"""INSERT INTO 
            SALES(sales_id, salesinvoice_id, employee_id, product_ids, date, customer_id)
                VALUES
            (concat('SA', '{cursalesid[0]}'),'SAI{cursalesinvoiceid[0]}','{empid[0]}','{pid[0]}','{str(curdate)}','{cusid[0][0]}')""")
            
            for row in self.data_tablestest.row_data:
                cur.execute(f"select product_id from product where product_name = '{row[0]}'")
                proid = cur.fetchone()
                print(proid[0])
                cur.execute(f"select stock from product where product_id = '{proid[0]}'")
                stocks = cur.fetchone()
                print(stocks)
                cur.execute(f"update product set stock = '{int(stocks[0]) - int(row[3])}' where product_id = '{proid[0]}'")

            conn.commit()

            self.setupdf()
                # ps = cur.fetchone()
            # cur.execute(f"select employee_id from emplogin where user_name = '{self.manager.get_screen('Login').ids.username.text}'")
            # empid= cur.fetchone()
            print('employeeid',empid[0])
            print(self.saledialog.content_cls.ids.cuscheck.text)
            if self.saledialog.content_cls.ids.cuscheck.text.isdigit():
                pass
            else:
                fromaddr = "dummyaccforpython3@gmail.com"
                toaddr = f"{self.saledialog.content_cls.ids.cuscheck.text}"

                # instance of MIMEMultipart
                msg = MIMEMultipart()

                # storing the senders email address
                msg['From'] = fromaddr

                # storing the receivers email address
                msg['To'] = toaddr

                # storing the subject
                msg['Subject'] = "Test message"

                # string to store the body of the mail
                body = "Just Testing dummy"

                # attach the body with the msg instance
                msg.attach(MIMEText(body, 'plain'))

                # open the file to be sent
                filename = "1-insert-supplier.csv"
                attachment = open("/home/prakash/kivysales/1-insert-supplier.csv", "rb")

                # instance of MIMEBase and named as p
                p = MIMEBase('application', 'octet-stream')

                # To change the payload into encoded form
                p.set_payload((attachment).read())

                # encode into base64
                encoders.encode_base64(p)

                p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

                # attach the instance 'p' to instance 'msg'
                msg.attach(p)

                # creates SMTP session
                s = smtplib.SMTP('smtp.gmail.com', 587)

                # start TLS for security
                s.starttls()

                # Authentication
                s.login(fromaddr, "emljyehsiaztaylt")

                # Converts the Multipart msg into a string
                text = msg.as_string()

                # sending the mail
                s.sendmail(fromaddr, toaddr, text)

                # terminating the session
                s.quit()

            cur.execute("select product_id, supplier_id from product where stock <= cast(stock_threshold as integer)")
            alle = cur.fetchall()
            print(alle)
            cj = ''
            getproductemail = {}
            if len(alle) == 0:
                pass
            else:
                for a in alle:
                    print(a)
                    # print(a[0])
                    cur.execute(f""" select product_name from product where product_id = '{a[0]}' """)
                    prname = cur.fetchall()
                    cur.execute(f""" select email from supplier where supplier_id ='{a[1]}' """)
                    supemail = cur.fetchall()
                    cj = f"{cj} {prname[0][0]},"
                    getproductemail[f"{supemail[0][0]}"] = cj
                    
                for key,value in getproductemail.items():

                    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                        # instance of MIMEMultipart
                        msg = MIMEMultipart()

                        # storing the senders email address
                        msg['From'] = "Sales app"

                        # storing the receivers email address
                        msg['To'] = key

                        # storing the subject
                        msg['Subject'] = "Stocks are getting low"

                        # string to store the body of the mail
                        body = f""" Hello the following stocks are getting low : {value} """

                        # attach the body with the msg instance
                        msg.attach(MIMEText(body, 'plain'))
                        # start TLS for security
                        smtp.starttls()
                        
                        # Authentication
                        smtp.login("dummyaccforpython3@gmail.com", "emljyehsiaztaylt")
                        
                        text = msg.as_string()
                        # sending the mail
                        smtp.sendmail("dummyaccforpython3@gmail.com", key, text)

            while len(self.data_tablestest.row_data) >= 1:
                self.data_tablestest.remove_row(self.data_tablestest.row_data[-1])

            self.dfw = self.dfw.iloc[0:0]

            # for row in self.data_tablestest.row_data:
            #     self.data_tablestest.remove_row(row)
            
            self.ids.search.text = ''
            self.ids.search.focus = True
            self.ids.showtotal.text = '0'
            self.saledialog.dismiss()
            
            
            cur.close()
            conn.close()
            self.success = MDDialog(
				    title = "Transaction succussfull",
				    buttons =[
					MDFlatButton(
						text="OK", text_color=self.theme_cls.primary_color, on_release = self.close_dialog
						),
					
					],
				    )
            self.success.open()

    def closedialog(self):
        self.success.dismiss()

    def bamount(self, value):
        if value == '':
            self.saledialog.content_cls.ids.sbalance.text = '0'
        else:
            self.saledialog.content_cls.ids.sbalance.text = str( int(value) - int(self.saledialog.content_cls.ids.tamount.text))
#class WindowManager(ScreenManager):
#	pass

class Newcustomeradd(BoxLayout):
    pass
class Salecontent(BoxLayout):
    pass
class Content(BoxLayout):
    pass

class UpdateQty(BoxLayout):
    pass

class DemoApp(MDApp):


    def popupclose(self, obj):
        self.dialog.dismiss()    
    

        # conn = None
        # try:
        #     # connect to the PostgreSQL server
        #     #print('Connecting to the PostgreSQL database...')
        #     conn = psycopg2.connect(
        #         host="43.205.140.2",
        #         database="postgres",
        #         user="admin",
        #         password="admin")
        #     # create a cursor
        #     cur = conn.cursor()
        #     cur.execute(f"SELECT User_Name FROM EMPLOGIN WHERE User_Name = '{self.root.get_screen('Login').ids.username.text}'")
        #     dbun = cur.fetchone()
        #     print(dbun)
        #     #dbun = None
        #     if dbun == None:
        #         self.dialog = MDDialog(
		# 		    title = "User Name or password incorrect!!!",
		# 		    text = "Please recheck username and password.......",
		# 		    buttons =[
		# 			MDFlatButton(
		# 				text="CANCEL", text_color=self.theme_cls.primary_color, on_release = self.popupclose
		# 				),
					
		# 			],
		# 		    )
        #         self.dialog.open()

        #     else:
        #         self.dialog = MDDialog(
		# 		    title = "welcome",
		# 		    text = f"Logged in....... {self.root.ids.username.text}",
		# 		    buttons =[
		# 			MDFlatButton(
		# 				text="CANCEL", text_color=self.theme_cls.primary_color, on_release = self.popupclose
		# 				),
					
		# 			],
		# 		    )
        #         self.sm.current = 'main'
        #         self.dialog.open()
                
        #         #cur.close()
        # except (Exception, psycopg2.DatabaseError) as error:
        #     print(error)
        # finally:
        #     if conn is not None:

        #         conn.close()

    


    def build(self):
        Builder.load_file("salesapp.kv")
        self.theme_cls.primary_palette="Orange"
        self.theme_cls.theme_style = "Light"
        self.sm = ScreenManager()
        
        self.sm.add_widget(LoginScreen())
        self.sm.add_widget(MainScreen())
        self.sm.add_widget(SettingScreen())
        self.sm.add_widget(AboutScreen())
       
        return self.sm

    def themeswitch(self, checkbox, value):

        if value:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"
        #screen = Screen()

        # username = MDTextField(
        #     pos_hint={'center_x': 0.5, 'center_y': 0.5},
        #     size_hint_x=None, width=200)

        #kv = Builder.load_string(kv_helper)
        
        #screen.add_widget(logincard)
        
    
    


    

if __name__=="__main__":
    DemoApp().run()