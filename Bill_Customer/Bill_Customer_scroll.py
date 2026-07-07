from tkinter import *
import pymsgbox
import time
from PIL import ImageTk,Image

def Bill_Customer():
    global root,imglbg,lbl_imglbg
    root = Tk()
    root.title('Billing')
    root.config(bg='#eaab06')

    imglbg=ImageTk.PhotoImage(Image.open("bg.jpg"))
    lbl_imglbg=Label(root,bg="white",image=imglbg)
    lbl_imglbg.place(x=0,y=0)

    h = root.winfo_screenheight()
    w = root.winfo_screenwidth()
    root.geometry("%dx%d" % (w,h)) #full screen

    import re
    import mysql.connector
        
    localtime=time.localtime(time.time()) #getting the present date and time
    #print(type(localtime[0]),type(localtime[1]),type(localtime[2]))
        
            
    #Sql connection commands
    con=mysql.connector.connect(host='localhost',user='root',passwd='root',database='project')
    mycursor=con.cursor()
    mycursor.execute("SELECT * FROM STOCK")
        
    icode=[]
    iname=[]
    iprice=[]
    istock=[]
    for i in mycursor:
        icode+=[i[0]]
        iname+=[i[1]]
        iprice+=[i[2]]
        istock+=[i[3]]
            

    class AutocompleteEntry(Entry):
        def __init__(self, autocompleteList, *args, **kwargs):

            # Listbox length
            if 'listboxLength' in kwargs:
                self.listboxLength = kwargs['listboxLength']
                del kwargs['listboxLength']
            else:
                self.listboxLength = 8

            # Custom matches function
            if 'matchesFunction' in kwargs:
                self.matchesFunction = kwargs['matchesFunction']
                del kwargs['matchesFunction']
            else:
                def matches(fieldValue, acListEntry):
                    pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
                    return re.match(pattern, acListEntry)
                        
                self.matchesFunction = matches

                
            Entry.__init__(self, *args, **kwargs)
            self.focus()

            self.autocompleteList = autocompleteList
                
            self.var = self["textvariable"]
            if self.var == '':
                self.var = self["textvariable"] = StringVar()

            self.var.trace('w', self.changed)
            self.bind("<Right>", self.selection)
            self.bind("<Up>", self.moveUp)
            self.bind("<Down>", self.moveDown)
                
            self.listboxUp = False

        def changed(self, name, index, mode):
            if self.var.get() == '':
                if self.listboxUp:
                    self.listbox.destroy()
                    self.listboxUp = False
            else:
                words = self.comparison()
                if words:
                    if not self.listboxUp:
                        self.listbox = Listbox(width=self["width"], height=self.listboxLength,font=('Arial',16))
                        self.listbox.bind("<Button-1>", self.selection)
                        self.listbox.bind("<Right>", self.selection)
                        self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                        self.listboxUp = True
                        
                    self.listbox.delete(0, END)
                    for w in words:
                        self.listbox.insert(END,w)
                else:
                    if self.listboxUp:
                        self.listbox.destroy()
                        self.listboxUp = False
                
        def selection(self, event):
            if self.listboxUp:
                self.var.set(self.listbox.get(ACTIVE))
                self.listbox.destroy()
                self.listboxUp = False
                self.icursor(END)

        def moveUp(self, event):
            if self.listboxUp:
                if self.listbox.curselection() == ():
                    index = '0'
                else:
                    index = self.listbox.curselection()[0]
                        
                if index != '0':                
                    self.listbox.selection_clear(first=index)
                    index = str(int(index) - 1)
                        
                    self.listbox.see(index) # Scroll!
                    self.listbox.selection_set(first=index)
                    self.listbox.activate(index)

        def moveDown(self, event):
            if self.listboxUp:
                if self.listbox.curselection() == ():
                    index = '0'
                else:
                    index = self.listbox.curselection()[0]
                        
                if index != END:                        
                    self.listbox.selection_clear(first=index)
                    index = str(int(index) + 1)
                        
                    self.listbox.see(index) # Scroll!
                    self.listbox.selection_set(first=index)
                    self.listbox.activate(index) 

        def comparison(self):
            return [ w for w in self.autocompleteList if self.matchesFunction(self.var.get(), w) ]
            
    autocompleteList = iname
    def matches(fieldValue, acListEntry):
        pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
        return re.match(pattern, acListEntry)
        
    global n,amt,update,store
    n=0
    amt=0
    update=[]
    store=[]
    
    def add():
        if(lno==1 and e1.get() in iname and e2.get()!='' and int(e2.get())<=istock[iname.index(e1.get())]):
            class MultipleScrollingListbox(Tk):

                def __init__(self):
                    global root

                    #the shared scrollbar
                    scrollbar = Scrollbar(root, orient='vertical')

                    #note that yscrollcommand is set to a custom method for each listbox
                    list1 = Listbox(root, yscrollcommand=self.yscroll1)
                    list1.pack(fill='y', side='left')

                    list2 = Listbox(root, yscrollcommand=self.yscroll2)
                    list2.pack(expand=1, fill='both', side='left')

                    scrollbar.config(command=self.yview)
                    scrollbar.pack(side='right', fill='y')

                    #fill the listboxes with stuff
                    list1.insert('end', 'sakthi')
                    list2.insert('end', 'vel')

                def yscroll1(self, *args):
                    if self.list2.yview() != self.list1.yview():
                        self.list2.yview_moveto(args[0])
                    self.scrollbar.set(*args)

                def yscroll2(self, *args):
                    if self.list1.yview() != self.list2.yview():
                        self.list1.yview_moveto(args[0])
                    self.scrollbar.set(*args)

                def yview(self, *args):
                    self.list1.yview(*args)
                    self.list2.yview(*args)


            if __name__ == "__main__":
                root = MultipleScrollingListbox()
                root.mainloop()

        elif(lno!=1 and e1.get() in iname and e2.get()!='' and int(e2.get())<=istock[iname.index(e1.get())]):
            global amt,update,pr,store
            z=iname.index(e1.get())
            am=iprice[z]*int(e2.get())
            mylist.insert(END,str(icode[z])+str(iname[z])+str(iprice[z])+str(e2.get())+str(am))
            n+=1
            '''lbl3=Label(root,bg='#eaab06',font=('Arial',16),text="%d"%(icode[z]))
            lbl3.place(x=110,y=270+(n*28))
                
            lbl4=Label(root,bg='#eaab06',font=('Arial',16),text="%s"%(iname[z]))
            lbl4.place(x=380,y=270+(n*28))

            lbl5=Label(root,bg='#eaab06',font=('Arial',16),text="%d"%(iprice[z]))
            lbl5.place(x=707,y=270+(n*28))

            lbl6=Label(root,bg='#eaab06',font=('Arial',16),text="%s"%(e2.get()))
            lbl6.place(x=1020,y=270+(n*28))

            lbl7=Label(root,bg='#eaab06',font=('Arial',16),text="%d"%(iprice[z]*int(e2.get())))
            lbl7.place(x=1312,y=270+(n*28))'''
            
            pr=iprice[z]*int(e2.get())
            amt+=pr
            update+=[[istock[z] - int(e2.get()),iname[z]]]
            store+=[[iname[z],int(e2.get())]]    
                            
            e1.delete(0,100)
            e2.delete(0,100)

        elif(e1.get()==''):
            pymsgbox.alert('Please Enter the "Item Name"','Error')
            e2.delete(0,100)
            e2.delete(0,100)
                
        elif(e1.get() not in iname):
            pymsgbox.alert('Please Enter the "Existing Item Name"','Error')
            e1.delete(0,100)
            e2.delete(0,100)

        elif(e2.get()==''):
            pymsgbox.alert('Please Enter the "Quantity"','Error')
            e2.delete(0,100)

        else:
            pymsgbox.alert('Please Enter a "Proper Quantity"','Error')
            e2.delete(0,100)

    def undo():
        global n,pr,amt
        if(n!=0 and b1["state"]!="disabled"):
            update.pop(len(update)-1)
                              
            lbl3=Label(root,bg='#eaab06',font=('Arial',16),text='',width=24)
            lbl3.place(x=110,y=270+(n*28))
                    
            lbl4=Label(root,bg='#eaab06',font=('Arial',16),text='',width=24)
            lbl4.place(x=380,y=270+(n*28))

            lbl5=Label(root,bg='#eaab06',font=('Arial',16),text='',width=24)
            lbl5.place(x=707,y=270+(n*28))

            lbl6=Label(root,bg='#eaab06',font=('Arial',16),text='',width=24)
            lbl6.place(x=1020,y=270+(n*28))

            lbl7=Label(root,bg='#eaab06',font=('Arial',16),text='',width=24)
            lbl7.place(x=1312,y=270+(n*28))
                
            n-=1
            amt-=pr

        elif(b1["state"]=="disabled"):
            top = Toplevel()
            top.geometry("500x300")
            top.config(bg='#eaab06')
            lbltl=Label(top,text="Do you want to cancel the bill?",bg='#eaab06',font=('Arial',16))
            lbltl.place(x=100,y=50)
            btl1=Button(top,text="Yes,I'm sure!",font=('Arial',16),bg='#eaab06',command=root.destroy)
            btl1.place(x=125,y=150)
            btl2=Button(top,text="No!",font=('Arial',16),bg='#eaab06',command=top.destroy)
            btl2.place(x=325,y=150)
            
                
        else:
            root.destroy()

    def check_mem():
        global n,amt,mem_phno,mem_name
        mycursor.execute("SELECT * FROM MEMBERSHIP")
        mem_id=[]
        mem_name=[]
        mem_phno=[]
        mem_exp=[]
        for i in mycursor:
            mem_id+=[i[0]]
            mem_name+=[i[1]]
            mem_phno+=[i[2]]
            mem_exp+=[i[3]]
            #                                    expiry date of member                            current date
        try:
            if(int(eno.get()) in mem_phno and str(mem_exp[mem_phno.index(int(eno.get()))])>=("%d-%d-%d"%(localtime[0],localtime[1],localtime[2]))):
                lblid=Label(root,text="Member ID: %d"%(mem_id[mem_phno.index(int(eno.get()))]),bg='#eaab06',font=('Arial',16))
                lblid.place(x=50,y=275+((n+3)*28))

                lblname=Label(root,text="Hello %s"%(mem_name[mem_phno.index(int(eno.get()))]),bg='#eaab06',font=('Arial',16)).place(x=50,y=275+((n+4)*28))
                    
                lbld=Label(root,text="Discount:                                      2%                                              ",font=('Arial',16),bg='#eaab06')
                lbld.place(x=1000,y=275+((n+3)*28))
                lblfamt=Label(root,text="Final Amount",font=('Arial',16),bg='#eaab06')
                lblfamt.place(x=1000,y=275+((n+4)*28))
                amt-=amt*0.02
                lblfamt1=Label(root,text="%d"%(amt),font=('Arial',16),bg='#eaab06')
                lblfamt1.place(x=1312,y=275+((n+4)*28))
                n+=2
                ok1()
            elif(int(eno.get()) in mem_phno and str(mem_exp[mem_phno.index(int(eno.get()))])<("%d-%d-%d"%(localtime[0],localtime[1],localtime[2]))):
                def renew():
                    top1.destroy()
                    new_year=localtime[0]+1
                    mycursor.execute("UPDATE MEMBERSHIP SET EXP_DATE = '%d-%d-%d' WHERE PHONE_NUMBER = '%s'"%(new_year,localtime[1],localtime[2],eno.get()))
                    con.commit()
                    check_mem()

                def No_renew():
                    top1.destroy()
                    ok1()
                        
                top1=Toplevel()
                top1.geometry("600x300")
                lbl_ext=Label(top1,text="MEMBERSHIP EXPIRED\nWould you like to RENEW your MEMBERSHIP",height=5,font=('Arial',16)).place(x=100,y=50)
                b_ext_s=Button(top1,text="Yes",command=renew,font=('Arial',16)).place(x=175,y=170)
                b_ext_n=Button(top1,text="No",command=No_renew,font=('Arial',16)).place(x=375,y=170)
            else:
                global e_cname,name_cus
                def cus_name():
                    global e_cname,name_cus
                    name_cus=e_cname.get()
                    lbl_hello=Label(root,text="Hello %s"%(e_cname.get()),bg='#eaab06',font=('Arial',16))
                    lbl_hello.place(x=50,y=275+((n+4)*28))
                    ok1()
                    lbl_cname.destroy()
                    e_cname.destroy()
                lbl_cname=Label(root,text="Enter Customer's Name:",bg='#eaab06',font=('Arial',16))
                lbl_cname.place(x=50,y=275+((n+4)*28))
                e_cname=Entry(root,width=20,font=('Arial',16))
                e_cname.place(x=300,y=275+((n+4)*28))
                root.bind("<Return>", lambda e: cus_name())
        except ValueError:
            pymsgbox.alert("Enter the Customer Phone Number 'properly'","Error")
                

    def ok():           
        global eno,pa
        b1["state"] = "disabled"
        b2["state"] = "disabled"

        lbl=Label(root,text="_"*115,bg='#eaab06',font=('Arial',16))
        lbl.place(x=50,y=265+((n+1)*28))
        lblamt1=Label(root,text="Total Amount",bg='#eaab06',font=('Arial',16))
        lblamt1.place(x=1000,y=275+((n+2)*28))
        lblamt2=Label(root,text="%d"%(amt),bg='#eaab06',font=('Arial',16))
        lblamt2.place(x=1312,y=275+((n+2)*28))
        lblphno=Label(root,text="Customer Phone Number:  ",font=('Arial',16),bg='#eaab06')
        lblphno.place(x=50,y=275+((n+2)*28))
        eno=Entry(root,width=20,font=('Arial',16))
        eno.place(x=300,y=275+((n+2)*28))
        pa=275+((n+2)*28)
        root.bind('<Return>', lambda e: check_mem())
            

    def ok1():
        global ecusamt
        lblcusamt=Label(root,text="Amount paid by customer",bg='#eaab06',font=('Arial',16))
        lblcusamt.place(x=1000,y=275+((n+3)*28))
        ecusamt=Entry(root,width=10,font=('Arial',16))
        ecusamt.place(x=1300,y=275+((n+3)*28))
        root.bind('<Return>', lambda e: finish_bill())

    def bill_store():
        date="%d-%d-%d"%(localtime[0],localtime[1],localtime[2])
        import pickle
        with open(r"bill_details.dat","rb") as fp:
            dict_bill=pickle.load(fp)
            if(int(eno.get()) in mem_phno):
                a=mem_name[mem_phno.index(int(eno.get()))]
            else:
                a=name_cus
            if(date not in dict_bill):
                dict_bill[date]={bill_no:[eno.get(),a.title(),store,amt,int(ecusamt.get())]}
            else:
                dict_bill[date][bill_no]=[eno.get(),a.title(),store,amt,int(ecusamt.get())]
        with open(r"bill_details.dat","wb") as fp:
            pickle.dump(dict_bill,fp)
        ecusamt.destroy()
                    
                    
    def billno():
        global bill_no
        with open(r"bill_no.txt","r") as fp:
            bill_no=int(fp.read())
            nb=bill_no+1
        with open(r"bill_no.txt","w") as fp:
            fp.write(str(nb))
        lbl_bno1=Label(root,text="Bill no:",bg='#eaab06',font=('Arial',16)).place(x=50,y=200)
        lbl_bno2=Label(root,text="%d"%(bill_no),bg='#eaab06',font=('Arial',16)).place(x=150,y=200)
            
    def finish_bill():
        global pa
        try:
            if(ecusamt.get()=='' or int(ecusamt.get())<amt):
                pymsgbox.alert('Enter the "Customer Amount Properly"','Error')
                ecusamt.delete(0,100)
            else:
                lblcusamt1=Label(root,text=ecusamt.get(),width=11,bg='#eaab06',font=('Arial',16))
                lblcusamt1.place(x=1270,y=275+((n+3)*28))
                lblbal=Label(root,text="Amount to be returned",bg='#eaab06',font=('Arial',16))
                lblbal.place(x=1000,y=275+((n+4)*28))
                lblbal=Label(root,text="%d"%(int(ecusamt.get())-amt),bg='#eaab06',font=('Arial',16))
                lblbal.place(x=1315,y=275+((n+4)*28))
                billno()
                bill_store()
                lbl_phno=Label(root,text="%s"%(eno.get()),font=('Arial',16),bg='#eaab06')
                lbl_phno.place(x=300,y=pa)
                eno.destroy()
                b_end=Button(root,text="Close",bg='#eaab06',font=('Arial',16),command=root.destroy).place(x=1315,y=275+((n+5)*28))
                root.bind("<End>", lambda e: root.destroy())
                root.after(15000,root.destroy)
            for i in update:
                mycursor.execute("UPDATE STOCK SET AVAILABLE_STOCK = %d WHERE ITEM_NAME = '%s'"%(i[0],i[1]))
                con.commit()
        except ValueError:
            pymsgbox.alert('Customer Amount should be in "numbers/digits"','Error')

                         
    #tkinter rootdow

    lbl=Label(root,text="_"*115,bg='#eaab06',font=('Arial',16))
    lbl.place(x=50,y=270)
    lbl0=Label(root,text="_"*115,bg='#eaab06',font=('Arial',16))
    lbl0.place(x=50,y=220)
        
    lbl1=Label(root,bg='#eaab06',font=('Arial',16),text="Enter the Item Name",width=20,anchor="w")
    lbl1.place(x=200,y=100)

    lbl2=Label(root,bg='#eaab06',font=('Arial',16),text="Enter the Quantity",width=20,anchor="w")
    lbl2.place(x=200,y=150)

    lbl3=Label(root,bg='#eaab06',font=('Arial',16),text="Item Code",anchor="w")
    lbl3.place(x=100,y=250)

    lbl4=Label(root,bg='#eaab06',font=('Arial',16),text="Item Name",anchor="w")
    lbl4.place(x=400,y=250)

    lbl5=Label(root,bg='#eaab06',font=('Arial',16),text="Price",anchor="w")
    lbl5.place(x=700,y=250)

    lbl6=Label(root,bg='#eaab06',font=('Arial',16),text="Quantity",anchor="w")
    lbl6.place(x=1000,y=250)

    lbl7=Label(root,bg='#eaab06',font=('Arial',16),text="Amount",anchor="w")
    lbl7.place(x=1300,y=250)
            
    e1 = AutocompleteEntry(autocompleteList, root,listboxLength=6, width=20, matchesFunction=matches,font=('Arial',16))
    e1.place(x=410,y=107)
    e2=Entry(root,width=20,font=('Arial',16))
    e2.place(x=410,y=157)    
        
    b1=Button(root,bg='#eaab06',font=('Arial',16),text="ADD",command=add)
    b1.place(x=450,y=192)
    b2=Button(root,bg='#eaab06',font=('Arial',16),text="BILL",command=ok)
    b2.place(x=550,y=192)
    root.bind('<Escape>',lambda e: undo())
    root.bind('<Return>', lambda e: add())
    root.bind('<Shift-Return>', lambda e: ok())
    lno=1
    '''scrollbar = Scrollbar(root)
    scrollbar.pack( side = RIGHT, fill = Y )
    scrollbar1 = Scrollbar(root)
    scrollbar1.pack( side = RIGHT, fill = Y )
    mylist = Listbox(root,bd=-2,bg='#eaab06',font=('Arial',16), yscrollcommand = scrollbar.set )
    mylist.place(x=100,y=300)
    mylist1 = Listbox(root,bd=-2,bg='#eaab06',font=('Arial',16), yscrollcommand = scrollbar1.set )
    mylist1.place(x=300,y=300)
    scrollbar.config( command = mylist.yview )
    scrollbar1.config( command = mylist1.yview )
    mylist.config(height=3,width=11)
    mylist1.config(height=3,width=11)
    for q in range(0,50):
        mylist.insert(END,q)
        mylist1.insert(END,q)'''
    
    root.mainloop()
Bill_Customer()
