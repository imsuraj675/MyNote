from tkinter import *
from tkinter.messagebox import _show,askyesnocancel
from tkinter import font,filedialog,ttk
from os import system, startfile
from sys import exit
from sqlite3 import connect

class My_Note(Tk):
    # Variables
    issaved = False
    file_path = 'New Note'
    file_name = 'New Note'
    Bold = Italic = Underline = Wrap = Status = None

    # Initializing all class variables
    def __init__(self):
        super().__init__()

        # Checkbuttons
        self.Bold = IntVar(self)
        self.Italic = IntVar(self)
        self.Underline = IntVar(self)
        self.Wrap = IntVar(self,value=1)
        self.Status = StringVar(self,value='Ready')

        # For Font_Selection
        self.set_font_selector()

        # For Find, Replace
        self.startindex = '1.0'
        self.found=False
        self.exact=False
        self.nocase=True
        self.find_next_press = False

    # Setting Window height,width
    def window_set(self, width, height, minwidth, minheight):
        self.geometry(f'{width}x{height}')
        self.minsize(minwidth, minheight)
        self.iconbitmap('Mynote_img.ico')
        self.title_set()

    # Setting Window Title
    def title_set(self):
        if self.file_path == 'New Note':
            tag = ''
        elif self.issaved:
            tag = '(Saved)'
        else:
            tag = '(Not Saved)'
        self.title(f'MyNote - {self.file_path} {tag}')

    # Function for setting Scrollbar and Text Widget
    def Text_widget_and_scrollbar(self):
        self.pad = Text(self, font=self.main_font, wrap='word',undo=1,selectforeground='black',inactiveselectbackground='grey')
        scrolly = Scrollbar(self.pad,cursor='left_ptr')
        scrollx = Scrollbar(self.pad,orient=HORIZONTAL,cursor='left_ptr')
        self.pad.configure(yscrollcommand=scrolly.set,xscrollcommand=scrollx)

        scrolly.configure(command=self.pad.yview)
        scrollx.configure(command=self.pad.xview)

        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.pack(side=BOTTOM, fill=X)
        self.pad.pack(fill=BOTH,expand=1)
        
        self.scrollers = (scrollx,scrolly)
        f1 = Frame(self,relief=RIDGE)
        f1.pack(side=BOTTOM,fill=X)

        status_widget = Label(f1,text=self.Status.get(), anchor='w')

        status_widget.pack(side=LEFT)

        line = Label(f1,text=f"Line : {self.pad.index(INSERT).split('.')[0]} Char : {self.pad.index(INSERT).split('.')[1]}",anchor='e')
        line.pack(side=RIGHT)
        return status_widget, line

    # Function for opening new a file
    def new_file(self):
        self.destroy()
        startfile('My_Note.py')

    # Function for saving a file
    def save_file(self):
        if not self.issaved and self.file_name=='New Note':
            name = filedialog.asksaveasfile(title='Save File', defaultext='.txt', initialdir='%HOMEDRIVE%%HOMEPATH%', filetypes=[
                ('Text Files', '*.txt'), ('All files', '*.*')])
            if not name == None:
                self.file_path = eval(str(name).split('=')[1].replace(' mode',''))
                self.issaved = True
                with open(self.file_path, 'w') as f:
                    f.write(self.pad.get(1.0, END))
                
                self.file_name = self.file_path.split('/')[-1]
                # Saving data to database
                Db = Database(self.file_name)
                Db.clear()
                for i in self.get_format():
                    Db.Insert_data(i[0],i[1],i[2])
        else:
            self.issaved=True
            with open(self.file_path, 'w') as f:
                f.write(self.pad.get(1.0, END))
                
            # Saving data to database
            Db = Database(self.file_name)
            Db.clear()
            for i in self.get_format():
                Db.Insert_data(i[0],i[1],i[2])

        self.title_set()

    # Function for Sava As 
    def save_as_file(self):
        name = filedialog.asksaveasfile(title='Save As File', defaultext='.txt', initialdir='%HOMEDRIVE%%HOMEPATH%', filetypes=[
            ('Text Files', '*.txt'), ('All files', '*.*')])
        if not name == None:
            file_path = eval(str(name).split('=')[1].replace(' mode',''))
            file_name = file_path.split('/')[-1]
            with open(file_path, 'w') as f:
                f.write(self.pad.get(1.0, END))

            # Saving data to database
            Db = Database(file_name)
            Db.clear()
            for i in self.get_format():
                Db.Insert_data(i[0],i[1],i[2])

    # Function for opening a file
    def open_file(self):
        file = filedialog.askopenfile(
            title="Open File", initialdir='%HOMEDRIVE%%HOMEPATH%', filetypes=[('Text Files', '*.txt'),('Python files','*.py'), ('All files', '*.*')])
        if not file == None:
            file_path = eval(str(file).split('=')[1].replace(' mode',''))
            file_name = file_path.split('/')[-1]
            with open(file_path) as f:
                My_Note_new = My_Note()
                My_Note_new.issaved = True
                My_Note_new.file_path = file_path
                My_Note_new.file_name = file_name

                def set_data():
                    current_bold_font = My_Note_new.main_font.copy()
                    current_bold_font.config(weight='bold')

                    current_italic_font = My_Note_new.main_font.copy()
                    current_italic_font.config(slant='italic')

                    current_underline_font = My_Note_new.main_font.copy()
                    current_underline_font.config(underline=1)

                    current_overstrike_font = My_Note_new.main_font.copy()
                    current_overstrike_font.config(overstrike=1)

                    current_regular_font = My_Note_new.main_font.copy()

                    Db = Database(file_name)
                    for i in Db.Select_data():
                        for j in ['bold','italic','underline','overstrike','regular']:
                            if j!=i[2]:
                                My_Note_new.pad.tag_remove(f'Format_{j}_text',i[0],i[1])
                            else:
                                My_Note_new.pad.tag_configure(f'Format_{i[2]}_text',font=eval(f'current_{i[2]}_font'))
                                My_Note_new.pad.tag_add(f'Format_{i[2]}_text',i[0],i[1])
            
                main(My_Note_new, f.read(),set_data)
    
    def get_format(self):
        data_lst = []
        style = {'Format_bold_text':'bold','Format_italic_text':'italic','Format_underline_text':'underline','Format_overstrike_text':'overstrike'}
        for x in style:
            for i in range(0,len(self.pad.tag_ranges(x))-1,2):
                a = str(self.pad.tag_ranges(x)[i]).split('<string object: ')[0].replace('>','')
                b = str(self.pad.tag_ranges(x)[i+1]).split('<string object: ')[0].replace('>','')
                data_lst.append([a,b,style[x]])
        return data_lst

    # Important Function for opening a file
    def inserter(self, text=''):
        self.pad.insert(END, text)
    
    # For Shortcut for Bold,Italic,Underline
    def toggler(self,bold=False,underline=False,italic=False):
        if bold:
            if self.Bold.get() == 0:
                self.Bold.set(1)
            elif self.Bold.get() == 1:
                self.Bold.set(0)
        if italic:
            if self.Italic.get() == 0:
                self.Italic.set(1)
            elif self.Italic.get() == 1:
                self.Italic.set(0)
        if underline:
            if self.Underline.get() == 0:
                self.Underline.set(1)
            elif self.Underline.get() == 1:
                self.Underline.set(0)

        self.format()
   
    # For Font_Style Menu
    def format(self,font=False):

        bold = 'normal'
        underline = 0
        italic = 'roman'
        wrap_text = 'none'
        
        if not font:
            for i in [[self.Bold, 'bold'], [self.Italic, 'italic'], [self.Underline, 'underline'], [self.Wrap, 'word']]:
                if i[0].get() == 1:
                    if i[1] == 'bold':
                        bold = i[1]
                    elif i[1] == 'italic':
                        italic = i[1]
                    elif i[1] == 'word':
                        wrap_text = i[1]
                    else:
                        underline = 1
            self.pad_font.config(weight=bold, underline=underline, slant=italic)
            self.pad.configure(wrap=wrap_text)
        else:
            self.show_font()
    
    # To set regular_font
    def regular_setter(self):
        self.Bold.set(0)
        self.Italic.set(0)
        self.Underline.set(0)
        self.format()

    # For Font_Selection
    def set_font_selector(self):
        self.font_name = 'Times New Roman'
        self.font_size = 15

        self.pad_font =  self.main_font = font.Font(self, family=self.font_name,size=self.font_size)
        self.fonts = list(map(str,font.families()))
        self.fonts.sort()

    # To change Font
    def selector(self,font_name,font_size):
        self.font_name = font_name.get()
        self.font_size = font_size.get()
        if self.font_name not in self.fonts:
            _show('Invalid format','Please select a valid Font name and size.')
            self.base.destroy()
            self.set_font_selector()
            self.format(font=True)
            return
        else:
            self.pad_font.configure(family=self.font_name,size=self.font_size)
        self.base.destroy()
    
    #To show font dialog
    def show_font(self):
        self.base = Tk()
        self.base.geometry('400x200')
        self.base.title('Select Font')
        self.base.iconbitmap('Mynote_img.ico')

        font_name = StringVar(self.base,value=self.font_name)
        font_size = StringVar(self.base,value=self.font_size)

        Label(self.base,text='Select Font',font=5).grid(padx=20)
        Lbx = ttk.Combobox(self.base,values=self.fonts,textvariable=font_name)
        Lbx.grid(padx=30)

        Label(self.base,text='Select Size',font=5).grid(column=1,row=0,pady=10)
        SizeBox = ttk.Combobox(self.base,values=[str(i+1) for i in range(99)],textvariable=font_size)
        SizeBox.grid(padx=20,column=1,row=1)

        Button(self.base,text='Apply',command=lambda : self.selector(font_name,font_size)).grid(columnspan=2,pady=70)

        self.base.mainloop()
    
    # Close app
    def onclose(self):
        if not self.issaved:
            if len(self.pad.get(1.0,END))<=1:
                self.destroy()
            else:
                ask = askyesnocancel('Warning','Do you want to save file ?')
                if ask==True:
                    self.save_file()
                    if self.issaved:
                        self.destroy()
                elif ask==False:
                    self.destroy()
        else:
            self.destroy()

    #  Making shortcuts
    def configure_pad(self, status_widget):

        self.protocol('WM_DELETE_WINDOW',self.onclose)

        self.pad.bind('<Control-S>', func=lambda x: self.save_file())
        self.pad.bind('<Control-s>', func=lambda x: self.save_file())

        self.pad.bind('<Control-O>', func=lambda x: self.open_file())
        self.pad.bind('<Control-o>', func=lambda x: self.open_file())

        self.pad.bind('<Control-Alt-S>', func=lambda x: self.save_as_file())
        self.pad.bind('<Control-Alt-s>', func=lambda x: self.save_as_file())

        self.pad.bind('<Control-N>', func=lambda x: self.new_file())
        self.pad.bind('<Control-n>', func=lambda x: self.new_file())

        self.pad.bind('<Control-Z>', func=lambda x: self.pad.edit_undo())
        self.pad.bind('<Control-z>', func=lambda x: self.pad.edit_undo())

        self.pad.bind('<Control-Y>', func=lambda x: self.pad.edit_redo())
        self.pad.bind('<Control-y>', func=lambda x: self.pad.edit_redo())

        self.pad.bind('<Control-F>', func=lambda x: self.find_words('find'))
        self.pad.bind('<Control-f>', func=lambda x: self.find_words('find'))

        self.pad.bind('<Control-G>', func=lambda x: self.find_words('goto'))
        self.pad.bind('<Control-g>', func=lambda x: self.find_words('goto'))

        self.pad.bind('<Control-H>', func=lambda x: self.find_words('replace'))
        self.pad.bind('<Control-h>', func=lambda x: self.find_words('replace'))

        self.pad.bind('<ButtonPress>', func=lambda x: self.status_bar_setter(
            status_widget, 'Working.....'))
        self.pad.bind('<ButtonRelease>', func=lambda x: self.status_bar_setter(
            status_widget, 'Ready'))

        self.pad.bind('<KeyPress>', func=lambda x: self.status_bar_setter(
            status_widget, 'Working.....'))
        self.pad.bind('<KeyRelease>', func=lambda x: self.status_bar_setter(
            status_widget, 'Ready'))

        self.pad.bind(
            '<Control-B>', func=lambda x: self.toggler(bold=1))
        self.pad.bind(
            '<Control-b>', func=lambda x: self.toggler(bold=1))

        self.pad.bind(
            '<Control-I>', func=lambda x: self.toggler(italic=1))
        self.pad.bind(
            '<Control-i>', func=lambda x: self.toggler(italic=1))

        self.pad.bind(
            '<Control-U>', func=lambda x: self.toggler(underline=1))
        self.pad.bind(
            '<Control-u>', func=lambda x: self.toggler(underline=1))

        self.pad.bind('<Alt-F4>', func=lambda x: self.onclose())

        self.pad.bind('<F1>', func=lambda x: _show(
            'About us', 'This My_Note is made by Suraj Kashyap.'))

        self.pad.bind(
            '<Button-3>', lambda x: self.Popup_Menu(x))

        self.pad.focus()
    
    # To Add style to particular region
    def set_style(self,bold=0,underline=0,italic=0,overstrike=0,regular=0):
        words = self.pad.selection_get()

        startindex = self.pad.search(words,INSERT)
        stopindex = f'{startindex.split(".")[0]}.{eval(startindex.split(".")[1])+len(words)}'

        if bold:
            self.current_bold_font = self.pad_font.copy()

            self.pad.tag_remove('Format_italic_text',startindex,stopindex)
            self.pad.tag_remove('Format_underline_text',startindex,stopindex)
            self.pad.tag_remove('Format_overstrike_text',startindex,stopindex)

            self.pad.tag_add('Format_bold_text',startindex,stopindex)
            self.current_bold_font.config(weight='bold')
            self.pad.tag_configure('Format_bold_text',font=self.current_bold_font)

        elif italic:
            self.pad.tag_remove('Format_bold_text',startindex,stopindex)
            self.pad.tag_remove('Format_underline_text',startindex,stopindex)
            self.pad.tag_remove('Format_overstrike_text',startindex,stopindex)

            self.current_italic_font = self.pad_font.copy()

            self.pad.tag_add('Format_italic_text',startindex,stopindex)
            self.current_italic_font.config(slant='italic')
            self.pad.tag_configure('Format_italic_text',font=self.current_italic_font)

        elif underline:
            self.pad.tag_remove('Format_bold_text',startindex,stopindex)
            self.pad.tag_remove('Format_italic_text',startindex,stopindex)
            self.pad.tag_remove('Format_overstrike_text',startindex,stopindex)
            
            self.current_underline_font = self.pad_font.copy()

            self.pad.tag_add('Format_underline_text',startindex,stopindex)
            self.current_underline_font.config(underline=1)
            self.pad.tag_configure('Format_underline_text',font=self.current_underline_font)
            
        elif overstrike:
            self.pad.tag_remove('Format_bold_text',startindex,stopindex)
            self.pad.tag_remove('Format_italic_text',startindex,stopindex)
            self.pad.tag_remove('Format_underline_text',startindex,stopindex)
            
            self.current_overstrike_font = self.pad_font.copy()

            self.pad.tag_add('Format_overstrike_text',startindex,stopindex)
            self.current_overstrike_font.config(overstrike=1)
            self.pad.tag_configure('Format_overstrike_text',font=self.current_overstrike_font)

        elif regular:
            self.pad.tag_remove('Format_bold_text',startindex,stopindex)
            self.pad.tag_remove('Format_italic_text',startindex,stopindex)
            self.pad.tag_remove('Format_underline_text',startindex,stopindex)
            self.pad.tag_remove('Format_overstrike_text',startindex,stopindex)

    # Changing status of bold, italic, underline and regular (Function for Popup Menu)
    def popmenu_setter(self):
        try:
            words = self.pad.selection_get()
            startindex = self.pad.search(words,INSERT)
        except Exception:
            self.bold_status = DISABLED
            self.italic_status = DISABLED
            self.underline_status = DISABLED
            self.overstrike_status = DISABLED
            self.regular_status = DISABLED

        else:
            if 'Format_bold_text' in self.pad.tag_names(startindex):
                self.bold_status = DISABLED
            else:
                self.bold_status = NORMAL

            if 'Format_italic_text' in self.pad.tag_names(startindex):
                self.italic_status = DISABLED
            else:
                self.italic_status = NORMAL

            if 'Format_underline_text' in self.pad.tag_names(startindex):
                self.underline_status = DISABLED
            else:
                self.underline_status = NORMAL
            
            if 'Format_overstrike_text' in self.pad.tag_names(startindex):
                self.overstrike_status = DISABLED
            else:
                self.overstrike_status = NORMAL
            
            if self.overstrike_status == NORMAL and self.underline_status == NORMAL and self.italic_status == NORMAL and self.bold_status == NORMAL:
                self.regular_status=DISABLED
            else:
                self.regular_status=NORMAL

    # For Right Click Menu 
    def Popup_Menu(self, event):
        popmenu = Menu(self.pad, tearoff=0)
        self.popmenu_setter()

        popmenu.add_command(label='Regular',command=lambda : self.set_style(regular=1),state=self.regular_status)

        popmenu.add_command(label='Bold',command=lambda : self.set_style(bold=1),state=self.bold_status)

        popmenu.add_command(label='Italic',command=lambda : self.set_style(italic=1),state=self.italic_status)

        popmenu.add_command(label='Underline',command=lambda : self.set_style(underline=1),state=self.underline_status)

        popmenu.add_command(label='Overstrike',command=lambda : self.set_style(overstrike=1),state=self.overstrike_status)

        popmenu.add_separator()
        popmenu.add_command(label='Clear All', command=lambda : self.pad.delete(1.0, END))
        popmenu.add_command(label='Change_Font', command=lambda :self.format(font=True))
        popmenu.add_command(label='Close', command=self.onclose)
        popmenu.post(event.x_root, event.y_root)

    # For Find function
    def searcher(self,word):
        self.startindex = self.pad.search(word, self.startindex,END,exact=self.exact,nocase=self.nocase)
        if self.startindex:
            self.stopindex = f'{self.startindex.split(".")[0]}.{eval(self.startindex.split(".")[1])+len(word)}'
            self.pad.see(self.startindex)
            self.pad.tag_remove('sel',1.0,END)
            self.pad.tag_add('sel',self.startindex,self.stopindex)
            self.startindex=self.stopindex
        else:
            self.pad.bell()
            self.startindex=1.0

    # For Replace function
    def delete(self,new_text,old_text,all=False):
        def search():
            try:
                self.startindex = self.pad.search(old_text, self.startindex,END,exact=self.exact,nocase=self.nocase)
                if self.startindex:
                    self.stopindex = f'{self.startindex.split(".")[0]}.{eval(self.startindex.split(".")[1])+len(old_text)}'
                    self.pad.see(self.startindex)
                    self.pad.tag_remove('sel',1.0,END)
                    self.pad.tag_add('sel',self.startindex,self.stopindex)
            except Exception:
                self.pad.bell()
                self.startindex = 1.0
                self.stopindex = 1.0
            
        search()
        if self.find_next_press:
            if all:
                n=len(str(self.pad.get(1.0,END)).split(old_text))-1
            else:
                n=1
            for i in range(n):
                if 'sel' in self.pad.tag_names(self.startindex):
                    self.pad.delete(self.startindex,self.stopindex)
                    self.pad.insert(self.startindex,new_text)
                self.startindex = self.stopindex
                search()
            
        self.find_next_press = True

    # For Goto function
    def go(self,line):
        self.pad.see(line+'.0')
        self.pad.tag_remove('sel',1.0,END)
        self.pad.tag_add('sel',f'{line}.end')
        if eval(self.pad.index(END))-1<eval(line+'.0'):
            self.pad.tag_add('sel',eval(self.pad.index(END))-1)

    # Find, Replace, Underline Dialog box
    def find_words(self,pane='find'):

        base = Tk()
        base.minsize(300,250)
        base.maxsize(300,250)
        base.iconbitmap('Mynote_img.ico')
        base.title('Find,Replace,Goto')

        # Find Tab
        find_text=StringVar(base)
        self.matchcase = IntVar(base)
        self.exactword = IntVar(base)

        def toggle(matchcase=False,exactword=False):
            if matchcase:
                if self.matchcase.get()==0:
                    self.nocase=True
                elif self.matchcase.get()==1:
                    self.nocase=False
            if exactword:
                if self.exactword.get()==0:
                    self.exact=False
                elif self.exactword.get()==1:
                    self.exact=True
        

        self.Book = ttk.Notebook(base)
        self.find_tab = Frame(self.Book)
        Label(self.find_tab,text='Find What:',font=('Times New Roman',12)).grid(pady=5,columnspan=2)
        Entry(self.find_tab,textvariable=find_text,font=('Times New Roman',12)).grid(columnspan=2,pady=5)
        Button(self.find_tab,text='Find Next',font=('Times New Roman',12),command = lambda : self.searcher(find_text.get())).grid(pady=5,columnspan=2)

        Checkbutton(self.find_tab,text='Match Case',font=('Times New Roman',10),variable=self.matchcase,command=lambda : toggle(matchcase=True)).grid(padx=15)
        Checkbutton(self.find_tab,text='Whole words only',font=('Times New Roman',10),variable=self.exactword,command=lambda : toggle(exactword=True)).grid(row=3,column=1,padx=15)

        self.Book.pack()
        self.find_tab.pack(fill=BOTH,expand=1)
        self.Book.add(self.find_tab,text='Find')

        # Replace Tab
        self.replace_tab = Frame(self.Book)
        self.replace_tab.pack(fill=BOTH,expand=1)
        self.Book.add(self.replace_tab,text='Replace')

        old_text=StringVar(base)
        new_text=StringVar(base)

        Label(self.replace_tab,text='Find What:',font=('Times New Roman',9)).grid(pady=5,columnspan=2)
        Entry(self.replace_tab,textvariable=old_text,font=('Times New Roman',9)).grid(columnspan=2)

        Label(self.replace_tab,text='Replace With:',font=('Times New Roman',9)).grid(pady=5,columnspan=2)
        Entry(self.replace_tab,textvariable=new_text,font=('Times New Roman',9)).grid(columnspan=2)

        Button(self.replace_tab,text='Find And Replace',font=('Times New Roman',9),command = lambda : self.delete(new_text.get(),old_text.get())).grid(pady=5,row=1,column=2,padx=20)

        self.replace_button = Button(self.replace_tab,text='Replace',font=('Times New Roman',9),command = lambda : self.delete(new_text.get(),old_text.get()),state=NORMAL)
        self.replace_button.grid(pady=5,column=2,row=2,padx=10)
        
        self.replaceall_button=Button(self.replace_tab,text='Replace All',font=('Times New Roman',9),command = lambda : self.delete(new_text.get(),old_text.get(),all=1),state=NORMAL)
        self.replaceall_button.grid(pady=5,column=2,row=3,padx=10)

        Checkbutton(self.replace_tab,text='Match Case',font=('Times New Roman',10),variable=self.matchcase,command=lambda : toggle(matchcase=True)).grid(column=1)
        Checkbutton(self.replace_tab,text='Whole words only',font=('Times New Roman',10),variable=self.exactword,command=lambda : toggle(exactword=True)).grid(column=1,padx=15)

        # Goto
        self.goto_tab=Frame(self.Book)
        self.goto_tab.pack(fill=BOTH,expand=1)
        self.Book.add(self.goto_tab,text='Go To')

        go_line=StringVar(base)

        Label(self.goto_tab,text='Go to Line:',font=('Times New Roman',12)).grid(pady=15)
        Entry(self.goto_tab,textvariable=go_line,font=('Times New Roman',12)).grid(row=0,column=1,pady=15)

        Button(self.goto_tab,text='Go To',font=('Times New Roman',9),command = lambda : self.go(go_line.get())).grid(pady=5,columnspan=2,padx=20)

        if pane=='find':
            self.Book.select(self.find_tab)
        elif pane=='goto':
            self.Book.select(self.goto_tab)
        else:
            self.Book.select(self.replace_tab)
            
        base.mainloop()

    # File Menu
    def File_Menu_setter(self):
        File_Menu = Menu(self, tearoff=0)
        File_Menu.add_command(label='New        Ctrl+N',
                              command=lambda: self.new_file())
        File_Menu.add_command(label='Open        Ctrl+O',
                              command=lambda: self.open_file())
        File_Menu.add_command(label='Save        Ctrl+S',
                              command=lambda: self.save_file())
        File_Menu.add_command(
            label='Save As', command=lambda: self.save_as_file())
        File_Menu.add_separator()
        File_Menu.add_command(label='Exit        Alt+F4', command=self.onclose)
        return File_Menu

    # Edit Menu
    def Edit_Menu_setter(self):
        Edit_Menu = Menu(self, tearoff=0)
        Edit_Menu.add_command(label='Undo',command=self.pad.edit_undo)
        Edit_Menu.add_command(label='Redo',command=self.pad.edit_redo)
        Edit_Menu.add_separator()

        Edit_Menu.add_command(label='Cut        Ctrl+X',
                              command=lambda: self.pad.event_generate('<<Cut>>'))
        Edit_Menu.add_command(label='Copy        Ctrl+C',
                              command=lambda: self.pad.event_generate('<<Copy>>'))
        Edit_Menu.add_command(label='Paste        Ctrl+V',
                              command=lambda: self.pad.event_generate('<<Paste>>'))
        Edit_Menu.add_command(label='Select All        Ctrl+A',
                              command=lambda: self.pad.tag_add('sel',1.0,END))
        Edit_Menu.add_separator()

        Edit_Menu.add_command(label='Find        Ctrl+F',command=self.find_words)
        Edit_Menu.add_command(label='Replace        Ctrl+H',command=lambda :self.find_words('replace'))
        Edit_Menu.add_command(label='Go To        Ctrl+G',command=lambda :self.find_words('goto'))


        Edit_Menu.add_separator()

        Edit_Menu.add_command(label='Close', command=self.destroy)
        return Edit_Menu

    # Font Menu
    def Font_style_setter(self):

        Font_style_Menu = Menu(self, tearoff=0)
        Font_style_Menu.add_command(
            label='Regular', command=self.regular_setter)
        Font_style_Menu.add_checkbutton(
            variable=self.Bold,    label='Bold', command=self.format)
        Font_style_Menu.add_checkbutton(
            variable=self.Italic,  label='Italic', command=self.format)
        Font_style_Menu.add_checkbutton(
            variable=self.Underline, label='Underline', command=self.format)
        Font_style_Menu.add_separator()
        Font_style_Menu.add_checkbutton(
            variable=self.Wrap, label='Wrap Text', command=self.format)
        Font_style_Menu.add_command(
            label='Format', command=lambda: self.format(True))

        return Font_style_Menu

    # Help Menu
    def Help_Menu_setter(self):
        Help_Menu = Menu(self, tearoff=0)
        Help_Menu.add_command(label='About One_Note          F1', command=lambda: _show(
            'About us', 'This MyNote is made by Suraj Kashyap.'))

        return Help_Menu

    # Update Status bar 
    def status_bar_setter(self, status_widget, status):
        status_widget[0].configure(text=status)
        status_widget[1].configure(text=f"Line : {self.pad.index(INSERT).split('.')[0]} Char : {self.pad.index(INSERT).split('.')[1]}")
        self.issaved=False
        self.title_set()
        

class Database():
    def __init__(self,file_name):
        self.connection = connect(f'Data\\{file_name}.db')
        self.db = self.connection.cursor()
        try: 
            self.db.execute("""
                            CREATE TABLE MASTER(
                                Startindex text,
                                Stopindex text,
                                Format text
                            )
                            """)
            self.connection.commit()
        except Exception:
            pass

    def Insert_data(self,startindex,stopindex,format):
        with self.connection:
            self.db.execute('INSERT INTO MASTER VALUES((:start),(:stop),(:style))',{'start':startindex,'stop':stopindex,'style':format})

    def Select_data(self):
        with self.connection:
            self.db.execute('SELECT * FROM MASTER')
            return self.db.fetchall()
    
    def clear(self):
        with self.connection:
            self.db.execute('DELETE FROM MASTER')


# Main Function
def main(MyNote, text='',func=print):
    MyNote.window_set(700, 500, 500, 300)
    status_widget = MyNote.Text_widget_and_scrollbar()
    MyNote.inserter(text)

    MyNote.configure_pad(status_widget)

    # Making Menubar
    mymenu = Menu(MyNote)
    File_Menu = MyNote.File_Menu_setter()
    mymenu.add_cascade(menu=File_Menu, label='File')

    Edit_Menu = MyNote.Edit_Menu_setter()
    mymenu.add_cascade(menu=Edit_Menu, label='Edit')

    Font_style_Menu = MyNote.Font_style_setter()
    mymenu.add_cascade(menu=Font_style_Menu, label='Font_style')

    Help_Menu = MyNote.Help_Menu_setter()
    mymenu.add_cascade(menu=Help_Menu, label='Help')

    MyNote.configure(menu=mymenu)
    func()
    # Running loop
    MyNote.mainloop()
    # exit()

# Main

system('mkdir .\Data')
MyNote = My_Note()
main(MyNote)

