from __future__ import annotations # Anotations pour le Entity -> return Entity
from tkinter.constants import NO, SEL
from ecoords import ECoord
from numpy import ndarray
import PIL
import math
import copy


class AABB : # All unit are expressed in inches
    xmin : float 
    xmax : float 
    ymin : float 
    ymax : float

    def __init__(self, xmin, xmax, ymin, ymax) -> None:
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def getCenter(self) -> tuple[float, float]  : # (x, y)
        centerX = self.xmax - self.xmin
        centerY = self.ymax - self.ymin
        return (centerX, centerY)

    def merge(box1 : AABB, box2 : AABB) -> AABB : 
        xmin = min(box1.xmin, box2.xmin)
        xmax = max(box1.xmax, box2.xmax)
        ymin = min(box1.ymin, box2.ymin)
        ymax = max(box1.ymax, box2.ymax)
        return AABB(xmin, xmax, ymin, ymax)
    
    def __str__(self):
     return "[xmin=" + str(self.xmin) + ", xmax=" + str(self.xmax) + ", ymin=" + str(self.ymin) + ", ymax=" + str(self.ymax) + "]"


class Entity:
    #   var : Public 
    #  _var : Protected
    # __var : Private

    __name : str # Le nom de l'objet dans le logiciel (user friendly)
   
    __rengData : ECoord # Les données de base non transformées
    __vengData : ECoord # Les données de base non transformées
    __vcutData : ECoord # Les données de base non transformées

    __transformedRengData : ECoord # Les données de base non transformées
    __transformedVengData : ECoord # Les données de base non transformées
    __transformedVcutData : ECoord # Les données de base non transformées

    __rawBounds : AABB # La taille de la "feuille" du fichier chargé (en pouce)
    __bounds : AABB # L'AABB dde l'entité
    __pos : tuple[float, float] # La position de l'objet en pouces
    __angle : float # La rotation de l'objet en degré
    __scale : tuple[float, float] # L'échelle de l'objet
    __updateFlag : bool

    def __init__(self, reng : ECoord, veng : ECoord, vcut : ECoord, rawBounds : AABB) -> None:
        self.__rengData = reng
        self.__vengData = veng
        self.__vcutData = vcut
        self.__rawBounds = rawBounds

        self.__name = "New Object"
        self.resetTransform()

    def resetTransform(self) -> None :
        self.__updateFlag = True

        self.__transformedRengData = None
        self.__transformedVengData = None
        self.__transformedVcutData = None
        
        self.__updateBounds()

        self.__pos = (0, 0)
        self.__angle = 0
        self.__scale = (1, 1)


    def resetCacheFlag(self) -> None : 
        self.__updateFlag = False

    def getUpdateFlag(self) -> bool :
        return self.__updateFlag

    def clone(self) -> Entity :
        return copy.deepcopy(self)

    def getRengData(self) -> ECoord : 
        return self.__rengData if (self.__transformedRengData == None) else self.__transformedRengData

    def getVengData(self) -> ECoord : 
        return self.__vengData if (self.__transformedVengData == None) else self.__transformedVengData

    def getVcutData(self) -> ECoord : 
        return self.__vcutData if (self.__transformedVcutData == None) else self.__transformedVcutData

    def getName(self) -> str : 
        return self.__name

    def setName(self, name) -> None :
        assert isinstance(name, str)
        assert str != None
        self.__name = name
        
    def getBounds(self) -> AABB :
        return self.__bounds
    
    def getRawBounds(self) -> AABB : 
        return self.__rawBounds
    
    # Update the bounds.
    # Because the bounds have changed, the ecoords must be moved to match the new bounds
    # Ecoord pos are relative to the bounds size
    def updateRawBounds(self, newBounds : AABB) -> None : 
        assert(newBounds != None)
        assert (newBounds.xmin == 0)
        assert (newBounds.ymin == 0)
        
        
        self.__rawBounds.xmax = newBounds.xmax
        if newBounds.ymax == self.__rawBounds.ymax:
            print("[Entity \"" + self.__name + "\"] Update bounds ignored")
            return
        
        deltaY = newBounds.ymax - self.__rawBounds.ymax
        self.__rawBounds.ymax = newBounds.ymax
        print("[Entity \"" + self.__name + "\"] Update bounds (oldY=" + str(self.__rawBounds.ymax) + ", newY=" + str(newBounds.ymax) + ", dy=" + str(deltaY) + ")")

        
        if self.__rengData != None : 
            self.__rengData.moveFnc(0, deltaY)
        if self.__vengData != None : 
            self.__vengData.moveFnc(0, deltaY)
        if self.__vcutData != None:
            self.__vcutData.moveFnc(0, deltaY)
        if self.__transformedRengData != None :
            self.__transformedRengData.moveFnc(0, deltaY)
        if self.__transformedVengData != None :
            self.__transformedVengData.moveFnc(0, deltaY)
        if self.__transformedVcutData != None :
            self.__transformedVcutData.moveFnc(0, deltaY)
            
        self.__updateFlag = True
        self.__updateBounds()
        
    # x and y in inches
    def setPos(self, x : float, y : float) -> None :
        if x == self.__pos[0] and y == self.__pos[1] : 
            return
        
        dx = x - self.__pos[0]
        dy = y - self.__pos[1]
        print("dx=" + str(dx) + ", dy=" + str(dy))
        
        self.__updateFlag = True
        self.__setTransformedIfEmpty()
        self.__pos = [x, y]
        self.__transformedRengData.moveFnc(dx, dy)
        self.__transformedVengData.moveFnc(dx, dy)
        self.__transformedVcutData.moveFnc(dx, dy)
        self.__updateBounds()
        
    def getPos(self) -> None : 
        return copy.deepcopy(self.__pos)

    def __updateBounds(self) -> None :
        rengData = self.getRengData()
        vengData = self.getVengData()
        vcutData = self.getVcutData()
        
        self.__bounds = AABB(float("inf"), -float("inf"), float("inf"), -float("inf"))

        if(rengData != None) :
            self.__bounds = AABB(rengData.bounds[0], rengData.bounds[1], rengData.bounds[2], rengData.bounds[3])
        if(vengData != None) :
            self.__bounds.xmin = min(self.__bounds.xmin, vengData.bounds[0])
            self.__bounds.xmax = max(self.__bounds.xmax, vengData.bounds[1])
            self.__bounds.ymin = min(self.__bounds.ymin, vengData.bounds[2])
            self.__bounds.ymax = max(self.__bounds.ymax, vengData.bounds[3])
        if(vcutData != None) :
            self.__bounds.xmin = min(self.__bounds.xmin, vcutData.bounds[0])
            self.__bounds.xmax = max(self.__bounds.xmax, vcutData.bounds[1])
            self.__bounds.ymin = min(self.__bounds.ymin, vcutData.bounds[2])
            self.__bounds.ymax = max(self.__bounds.ymax, vcutData.bounds[3])

    def __setTransformedIfEmpty(self) -> None :
        if(self.__transformedRengData == None) : 
            self.__transformedRengData = copy.deepcopy(self.__rengData)
            
        if(self.__transformedVengData == None) : 
            self.__transformedVengData = copy.deepcopy(self.__vengData)
            
        if(self.__transformedVcutData == None) : 
            self.__transformedVcutData = copy.deepcopy(self.__vcutData)
                        
        
   # def move(self, x : float, y : float) -> None:
    #    self.pos[0] += x
    #    self.pos[1] += y

    #def 
    #def clone(self) : 
    #    copy = Entity()



class EntityList:

    __entities : list(Entity)
    __rengData : ECoord
    __vcutData : ECoord
    __vengData : ECoord
    __bounds : AABB
    __rawBounds : AABB
    __cacheFlag : bool # True : cache need to be updated

    def __init__(self) -> None:
        self.clear()

    def addEntity(self, entity : Entity) -> None :
        assert (entity != None)
        
        self.__rawBounds = AABB.merge(self.__rawBounds, entity.getRawBounds())
        self.__entities.append(entity)

        for lentity in self.__entities : 
            lentity.updateRawBounds(self.__rawBounds)
        
        self.__cacheFlag = True
        
    #remove the entity given in argument from the list
    # entity : Entity -> entity to be removed from the list    
    def deleteEntity(self, entity : Entity) -> None:
        assert (entity != None) 
        self.__entities.remove(entity)
        self.__cacheFlag = True
                      
    #create a duplicate of the entity given in argument and append it at the end of the list
    # entity : Entity -> entity to be duplicated
    def duplicateEntity(self, entity : Entity) -> None:
        assert (entity != None) 
        self.__entities.append(entity.clone())
        self.__cacheFlag = True

    def getEntities(self) -> list(Entity) :
        return self.__entities


    def clear(self) :
        self.__entities = []
        self.__rengData = ECoord()
        self.__vcutData = ECoord()
        self.__vengData = ECoord()
        self.__bounds = AABB(float("inf"), -float("inf"), float("inf"), -float("inf"))
        self.__rawBounds = AABB(float("inf"), -float("inf"), float("inf"), -float("inf"))
        self.__cacheFlag = False

    def getRengData(self) -> ECoord :
        self.__updateCache()
        return self.__rengData

    def getVengData(self) -> ECoord :
        self.__updateCache()
        return self.__vengData

    def getVcutData(self) -> ECoord :
        self.__updateCache()
        return self.__vcutData
    
    def getSheetBounds(self) -> AABB :
        return self.__rawBounds

    def __updateCacheFlag(self) -> None :
        if(self.__cacheFlag != True) : 
            for entity in self.__entities :
                if entity.getUpdateFlag() :
                    self.__cacheFlag = True
                    break


    def __updateCache(self) -> None :
        self.__updateCacheFlag()

        if self.__cacheFlag == True :
            # do some stuff to update the data
            self.__rengData.reset()
            self.__vengData.reset()
            self.__vcutData.reset()
            
            self.__bounds = AABB(float("inf"), -float("inf"), float("inf"), -float("inf"))

            ## create picture with pixels in bounds 
        

            #picture = [255] * picWidth * picHeight
            deltaY = 0
            for entity in self.__entities :
                deltaY = min(deltaY, entity.getBounds().ymin)
                self.__rawBounds.xmax = max(self.__rawBounds.xmax, entity.getBounds().xmax)
            self.__rawBounds.ymax -= deltaY
  
            for entity in self.__entities :
                entity.updateRawBounds(self.__rawBounds)    
            
            print("[Design] bounds="+ str(self.__rawBounds))
            picWidth = math.ceil(self.__rawBounds.xmax * 1000)
            picHeight = math.ceil(self.__rawBounds.ymax * 1000) 
            picture = PIL.Image.new("L", (picWidth, picHeight), (100))
            print("creating picture(size=(" + str(picWidth) + ", " + str(picHeight) +"))")    
            
            for entity in self.__entities :
                #print("entity(name=" + entity.getName() + ", bounds=" + str(entity.getBounds()))
                ## Process the picture 
                im = entity.getRengData().image
                if im != None :
                    entityPos = entity.getPos()
                    imWidth, imHeight = im.size
                    left = math.ceil(entityPos[0] * 1000)
                    up = -math.ceil(entityPos[1] * 1000)
                    right = left + imWidth
                    down = up + imHeight
                    region = (left, up, right, down)
                    #print("Entity \"" + entity.getName() + "\" image copied to " + str(region))
                    picture.paste(im, (left, up))

                
                ## End picture process
                
                
                self.__rengData.addEcoord(entity.getRengData())
                self.__vengData.addEcoord(entity.getVengData())
                self.__vcutData.addEcoord(entity.getVcutData())
                entity.resetCacheFlag()
                
                
            #self.__rengData.image = PIL.Image.frombytes("L", (picWidth, picHeight), bytes(picture))
            self.__rengData.image = picture


            self.__rengData.computeEcoordsLen()
            self.__vengData.computeEcoordsLen()
            self.__vcutData.computeEcoordsLen()
        
            self.__cacheFlag = False
    
