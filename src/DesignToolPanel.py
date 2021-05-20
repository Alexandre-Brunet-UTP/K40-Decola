from tkinter import *
from typing import Callable
from entity import EntityList
from entity import Entity

class EntryField:
    __label : Label
    __entry : Entry
    __value : StringVar

   
    def __init__(self, name : str, master : Tk, traceCallback = None, enabled : bool = True) -> None:
        self.__value = StringVar()
        self.__label = Label(master, text=name)
        self.__entry = Entry(master, width="15", textvariable=self.__value, justify="center", fg="black")

        if(traceCallback != None) :
            self.__value.trace_variable("w", traceCallback)

        self.setEnabled(enabled)

    def updateUI(self, xPos : int, yPos : int, visible : bool) -> None:

        if visible :
            self.__label.place(x=xPos-80, y=yPos, width=110, height=21)
            self.__entry.place(x=xPos+20, y=yPos, width=110, height=23)
        else :
            self.__label.place_forget()
            self.__entry.place_forget()

    def clearText(self) -> None :
        self.__value.set("")

    def setText(self, content) -> None : 
        self.__value.set(str(content))

    def getText(self) -> str :
        return self.__value.get()

    def setEnabled(self, enabled : bool) :
        self.__entry["state"] = NORMAL if enabled else DISABLED


class EntityListView(Frame):

    __entities : EntityList
    __scrollbar : Scrollbar
    __list : Listbox

    def __init__(self, master, eList : EntityList, listCallback):
        Frame.__init__(self, master)

        self.__entities = eList

        self.__scrollbar = Scrollbar(self)

        self.__list = Listbox(self, yscrollcommand=self.__scrollbar.set)
      

        self.__scrollbar.config(command=self.__list.yview)

        self.__scrollbar.pack(side=RIGHT, fill=Y)
        self.__list.pack(side=LEFT, fill=BOTH)

        self.__list.bind("<<ListboxSelect>>", listCallback)


    def updateUI(self, xPos : int, yPos : int, w : int, h : int, visible : bool) -> None :
        if visible :
            self.__list.delete(0, END)
            for entity in self.__entities.getEntities():
                self.__list.insert(END, entity.getName())

            self.place(x=xPos, y=yPos, width=w, height=h)
        else :
            self.place_forget()



class DesignToolPanel:

    __master : Tk
    #vertSeparator : Frame
    __title : Label

    __entities : EntityList
    __currentEntity : Entity
    __nameEntry : EntryField
    __scaleEntry : EntryField
    __angleEntry : EntryField
    __xPosEntry : EntryField
    __yPosEntry : EntryField
    __width : int
    __isVisible : bool
    __entitiesList : EntityListView
    __validateButton : Button
    __cancelButton : Button
    __hidePannelButton : Button
    __refeshCallback : Callable[[None], None]
    __ecoordCallback : Callable[[None], None]


    def __init__(self, master : Tk, entities : EntityList, hideCallback, refreshUICallback, ecoordCallback) -> None:
        self.master = master
        self.__isVisible = True
        self.__entities = entities
        self.__currentEntity = None
        self.__refeshCallback = refreshUICallback
        self.__ecoordCallback = ecoordCallback

        self.__width = 150

      # Design Tool Settings Column    #
        #self.vertSeparator = Frame(self.master, height=2, bd=1, relief=SUNKEN)
        self.__title = Label(self.master,text="Design Tool Settings",anchor=CENTER)
        #self.separator_adv = Frame(self.master, height=2, bd=1, relief=SUNKEN)  

        # Gestion de l'angle et de la psoition du dessin en X et Y
        self.separator_comb = Frame(self.master, height=2, bd=1, relief=SUNKEN) 
        
        self.__nameEntry = EntryField(name="Name", master=self.master)
        self.__scaleEntry = EntryField(name="Scale", master=self.master, enabled=False)
        self.__angleEntry = EntryField(name="Angle", master=self.master, enabled=False)
        self.__xPosEntry = EntryField(name="Position X", master=self.master, enabled=True)
        self.__yPosEntry = EntryField(name="Position Y", master=self.master, enabled=True)
        
        self.__validateButton = Button(self.master,text="Validate", bg="green",  command=self.__onValidateButton)
        self.__cancelButton = Button(self.master,text="Cancel", bg="light coral", command=self.__onResetButton)
        #cacher le menu vertical de Design tool settings
        self.__hidePannelButton = Button(self.master,text="Hide Design Tool", command=hideCallback)


        self.__entitiesList = EntityListView(self.master, entities, self.__onListChangeCallback)

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
        self.__entitiesList.updateUI(xPos=refXPos-35, yPos=50, w=150, h=windowHeight-350, visible=self.__isVisible)

        if self.__isVisible :
            self.__title.place(x=refXPos, y=10)
            self.__hidePannelButton.place (x=refXPos-70, y=refYPos, width=200, height=30)
            self.__cancelButton.place (x=refXPos+35, y=refYPos-35, width=95, height=30)
            self.__validateButton.place(x=refXPos-70, y=refYPos-35, width=95, height=30)
        else :
            self.__title.place_forget()
            self.__hidePannelButton.place_forget()
            self.__cancelButton.place_forget()
            self.__validateButton.place_forget()



    #def varCallback(self, varName, index, mode) -> None:

    def __onValidateButton(self) -> None:
        if self.__currentEntity == None :
            return
        
        self.__currentEntity.setName(self.__nameEntry.getText())
        
        xPos = float(self.__xPosEntry.getText())
        yPos = float(self.__yPosEntry.getText())
        self.__currentEntity.setPos(xPos, yPos)
        self.__ecoordCallback()
        self.__refeshCallback()
        
    def __onResetButton(self) -> None :
        if self.__currentEntity == None : 
            return
        
        self.__nameEntry.setText(self.__currentEntity.getName())
        self.__xPosEntry.setText(self.__currentEntity.getPos()[0])
        self.__yPosEntry.setText(self.__currentEntity.getPos()[1])

    #    self.entry_set(self.Entry_Vcut_passes, self.Entry_Vcut_passes_Check(), new=1)

    def __selectEntity(self, index : int) -> None :
        if index == None :
            pass
           # self.__currentEntity = None
           # self.__nameEntry.clearText()
           # self.__scaleEntry.clearText()
           # self.__angleEntry.clearText()
            #self.__xPosEntry.clearText()
            #self.__yPosEntry.clearText()
        else :
            entity : Entity
            entity = self.__entities.getEntities()[index]
            self.__currentEntity = entity
            self.__nameEntry.setText(entity.getName())
            
            pos = self.__currentEntity.getPos()
            self.__xPosEntry.setText(pos[0])
            self.__yPosEntry.setText(pos[1])

    def __onListChangeCallback(self, event) -> None:
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.__selectEntity(index)
        else:
            self.__selectEntity(None)