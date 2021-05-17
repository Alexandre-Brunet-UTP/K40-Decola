from tkinter.constants import NO, SEL
from ecoords import ECoord
from __future__ import annotations # Anotations pour le Entity -> return Entity
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

    __bounds : AABB # L'AABB dde l'entité
    __pos : tuple[float, float] # La position de l'objet en pouces
    __angle : float # La rotation de l'objet en degré
    __scale : tuple[float, float] # L'échelle de l'objet

    def __init__(self, reng : ECoord, veng : ECoord, vcut : ECoord) -> None:
        self.__rengData = reng
        self.__vengData = veng
        self.__vcutData = vcut

        self.__name = "New Object"
        self.resetTransform()

    def resetTransform(self) -> None :
        self.__bounds = AABB(0, 0, 0, 0)

        if(self.rengData != None) :
            self.__bounds = AABB(self.__rengData.bounds[0], self.__rengData.bounds[1], self.__rengData.bounds[2], self.__rengData.bounds[3])
        if(self.vengData != None) :
            self.__bounds.xmin = min(self.__bounds.xmin, self.__vengData.bounds[0])
            self.__bounds.xmax = max(self.__bounds.xmax, self.__vengData.bounds[1])
            self.__bounds.ymin = min(self.__bounds.ymin, self.__vengData.bounds[2])
            self.__bounds.tmax = max(self.__bounds.ymax, self.__vengData.bounds[3])
        if(self.vcutData != None) :
            self.__bounds.xmin = min(self.__bounds.xmin, self.__vcutData.bounds[0])
            self.__bounds.xmax = max(self.__bounds.xmax, self.__vcutData.bounds[1])
            self.__bounds.ymin = min(self.__bounds.ymin, self.__vcutData.bounds[2])
            self.__bounds.tmax = max(self.__bounds.ymax, self.__vcutData.bounds[3])

        self.__pos = self.bounds.getCenter()
        self.__angle = 0
        self.__scale = (1, 1)

        self.__transformedRengData = None
        self.__transformedVengData = None
        self.__transformedVcutData = None

    def isCached(self) -> bool :
        return True

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
    __cacheFlag : bool # True : cache need to be updated

    def __init__(self) -> None:
        self.__entities = []
        self.__rengData = ECoord()
        self.__vcutData = ECoord()
        self.__vengData = ECoord()
        self.__cacheFlag = False

    def addEntity(self, entity : Entity) -> None :
        assert (entity != None) 
        self.__entities.append(entity)
        self.__cacheFlag = True

    def getRengData(self) -> ECoord :
        self.__updateCache()
        return self.__rengData

    def getVengData(self) -> ECoord :
        self.__updateCache()
        return self.__vengData

    def getVcutData(self) -> ECoord :
        self.__updateCache()
        return self.__vcutData

    def __updateCacheFlag(self) -> None :
        if(self.__cacheFlag != True) : 
            for entity in self.__entities :
                if not entity.isCached() :
                    self.__cacheFlag = True
                    break


    def __updateCache(self) -> None :
        self.__updateCacheFlag()

        if self.__cacheFlag == True :
            # do some stuff to update the data
            self.__rengData.reset()
            self.__vengData.reset()
            self.__vcutData.reset()

            for entity in self.__entities :
                self.__rengData.addEcoord(entity.getRengData())
                self.__vengData.addEcoord(entity.getVengData())
                self.__vcutData.addEcoord(entity.getVcutData())
            
            self.__rengData.computeEcoordsLen()
            self.__vengData.computeEcoordsLen()
            self.__vcutData.computeEcoordsLen()
    
