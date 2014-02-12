

'''tix_Editor_simple1.py a very simple Tkinter/Tix editor shows you
how to create a menu and use the file dialog to read and write files
of text data for faintful hints see:
http://tix.sourceforge.net/man/html/contents.htm tested with Python27
and Python32 by vegaseat

'''
try:
    # Python2
    import Tix as tix
    #import Tkinter as tk # use tix instead
    import tkFileDialog as tkfd
except ImportError:
    # Python3
    import tkinter.tix as tix
    #import tkinter as tk # use tix instead
    import tkinter.filedialog as tkfd

class MyEditor(object):
    def __init__(self, master):
        frame = tix.Frame(master)
        frame.pack(fill='both', expand=1)
        self.edit = tix.ScrolledText(frame, bg='white')
        self.edit.pack()
        menu = tix.Menu(master)
        root.config(menu=menu)
        # file menu
        filemenu = tix.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.new_text)
        filemenu.add_command(label="Open", command=self.file_open)
        filemenu.add_command(label="SaveAs", command=self.file_saveas)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.do_exit)
        # start with cursor in the editor area
        self.edit.focus()
            
    def new_text(self):
        """clear the text area so you can start new text"""
        self.edit.text.delete(0.0, 'end')
        
    def file_open(self):
        """open a file to read"""
        # the filetype mask (default is all files)
        mask = \
               [("Text and Python files","*.txt *.py *.pyw"),
                ("HTML files","*.htm *.html"),
                ("All files","*.*")]
        fin = tkfd.askopenfile(filetypes=mask, mode='r')
        text = fin.read()
        if text != None:
            # delete any old text first
            self.edit.text.delete(0.0, 'end')
            self.edit.text.insert('end', text)
            
    def file_saveas(self):
        """get a filename and save your text to it"""
        # default extension is optional, will add .txt if missing
        fout = tkfd.asksaveasfile(mode='w', defaultextension=".txt")
        text2save = str(self.edit.text.get(0.0, 'end'))
        print(text2save) # test
        fout.write(text2save)
        fout.close()
        
    def do_exit(self):
        root.destroy()

if __name__ == '__main__':
    root = tix.Tk()
    # use width x height + x_offset + y_offset (no spaces!)
    root.geometry("%dx%d+%d+%d" % (640, 300, 120, 80))
    info1 = "simple tkinter/tix based editor "
    info2 = "(ctrl+c=copy ctrl+v=paste ctrl+x=cut ctrl+/=select all)"
    root.title(info1+info2)
    myed = MyEditor(root)
    root.mainloop()
            
