from tkinter import *

class EntryField:
    __label : Label
    __entry : Entry
    __value : StringVar

   
    def __init__(self, name : str, master : Tk, traceCallback) -> None:
        self.__value = StringVar()
        self.__label = Label(master, text=name)
        self.__entry = Entry(master, width="15", textvariable=self.__value, justify="center", fg="black")
        if(traceCallback != None) :
            self.__value.trace_variable("w", traceCallback)

    def updateUI(self, xPos : int, yPos : int, visible : bool) -> None:
        if visible :
            self.__label.place(x=xPos-80, y=yPos, width=110, height=21)
            self.__entry.place(x=xPos+20, y=yPos, width=110, height=23)
        else :
            self.__label.place_forget()
            self.__entry.place_forget()

class EntityListView(Frame):

    def __init__(self, master):




class DesignToolPanel:

    __master : Tk
    vertSeparator : Frame
    label_title : Label

    __nameEntry : EntryField
    __scaleEntry : EntryField
    __angleEntry : EntryField
    __xPosEntry : EntryField
    __yPosEntry : EntryField
    __width : int
    __isVisible : bool


    def __init__(self, master : Tk, hideCallback) -> None:
        self.master = master
        self.__isVisible = True

        self.__width = 150

      # Design Tool Settings Column    #
        self.vertSeparator = Frame(self.master, height=2, bd=1, relief=SUNKEN)
        self.label_title = Label(self.master,text="Design Tool Settings",anchor=CENTER)
        self.separator_adv = Frame(self.master, height=2, bd=1, relief=SUNKEN)  

        # Gestion de l'angle et de la psoition du dessin en X et Y
        self.separator_comb = Frame(self.master, height=2, bd=1, relief=SUNKEN) 
        
        self.__nameEntry = EntryField("Name", self.master, None)
        self.__scaleEntry = EntryField("Scale", self.master, None)
        self.__angleEntry = EntryField("Angle", self.master, None)
        self.__xPosEntry = EntryField("Position X", self.master, None)
        self.__yPosEntry = EntryField("Position Y", self.master, None)
        
        self.Validate_Design_Tool = Button(self.master,text="Validate", command=None)
        self.Cancel_Design_Tool = Button(self.master,text="Cancel", command=None)
        #cacher le menu vertical de Design tool settings
        self.Hide_Design_Button = Button(self.master,text="Hide Design Tool", command=hideCallback)

        self.Cancel_Design_Tool.configure(bg='light coral')
        self.Validate_Design_Tool.configure(bg='green')

    def setVisible(self, state : bool) -> None :
        self.__isVisible = state

    def updateUI(self, windowWidth : int, windowHeight : int) :
        refXPos = windowWidth - self.__width
        refYPos = windowHeight - 70

        self.__nameEntry.updateUI(xPos=refXPos, yPos=refYPos-190, visible=self.__isVisible)
        self.__scaleEntry.updateUI(xPos=refXPos, yPos=refYPos-160, visible=self.__isVisible)
        self.__angleEntry.updateUI(xPos=refXPos, yPos=refYPos-130, visible=self.__isVisible)
        self.__xPosEntry.updateUI(xPos=refXPos, yPos=refYPos-100, visible=self.__isVisible)
        self.__yPosEntry.updateUI(xPos=refXPos, yPos=refYPos-70, visible=self.__isVisible)

        if self.__isVisible :
            self.label_title.place(x=refXPos, y=10)
            self.Hide_Design_Button.place (x=refXPos-70, y=refYPos, width=200, height=30)
            self.Cancel_Design_Tool.place (x=refXPos+35, y=refYPos-35, width=95, height=30)
            self.Validate_Design_Tool.place(x=refXPos-70, y=refYPos-35, width=95, height=30)
        else :
            self.label_title.place_forget()
            self.Hide_Design_Button.place_forget()
            self.Cancel_Design_Tool.place_forget()
            self.Validate_Design_Tool.place_forget()