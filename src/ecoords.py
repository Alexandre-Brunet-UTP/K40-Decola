#!/usr/bin/python
"""
    Copyright (C) <2018>  <Scorch>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from math import *
from __future__ import annotations

class ECoord:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.image      = None
        self.reset_path()

    def reset_path(self):
        self.src_ecoords = [] # Ecoords without dupplucation or transformation.
        self.src_bounds = (0,0,0,0)
        self.ecoords    = []
        self.len        = None
        self.move       = 0
        self.sorted     = False
        self.rpaths     = False 
        self.bounds     = (0,0,0,0)
        self.gcode_time = 0
        self.hull_coords= []
        self.n_scanlines= 0

    def make_ecoords(self,coords,scale=1):
        self.reset()
        self.len  = 0
        self.move = 0
        
        xmax, ymax = -1e10, -1e10
        xmin, ymin =  1e10,  1e10
        self.ecoords=[]
        Acc=.001
        oldx = oldy = -99990.0
        first_stroke = True
        loop=0
        for line in coords:
            XY = line
            x1 = XY[0]*scale
            y1 = XY[1]*scale
            x2 = XY[2]*scale
            y2 = XY[3]*scale
            dxline= x2-x1
            dyline= y2-y1
            len_line=sqrt(dxline*dxline + dyline*dyline)
            
            dx = oldx - x1
            dy = oldy - y1
            dist   = sqrt(dx*dx + dy*dy)
            # check and see if we need to move to a new discontinuous start point
            if (dist > Acc) or first_stroke:
                loop = loop+1
                self.ecoords.append([x1,y1,loop])
                if not first_stroke:
                    self.move = self.move + dist
                first_stroke = False
                
            self.len = self.len + len_line
            self.ecoords.append([x2,y2,loop])
            oldx, oldy = x2, y2
            xmax=max(xmax,x1,x2)
            ymax=max(ymax,y1,y2)
            xmin=min(xmin,x1,x2)
            ymin=min(ymin,y1,y2)
        self.bounds = (xmin,xmax,ymin,ymax)
        self.src_ecoords = self.ecoords
        self.src_bounds = self.bounds

    def set_ecoords(self,ecoords,data_sorted=False):
        self.ecoords = ecoords
        self.src_ecoords = self.ecoords
        self.computeEcoordsLen()
        self.data_sorted=data_sorted

    def set_image(self,PIL_image):
        self.image = PIL_image
        self.reset_path()

    def computeEcoordsLen(self):  
        xmax, ymax = -1e10, -1e10
        xmin, ymin =  1e10,  1e10
        
        if self.ecoords == [] :
            self.len=0
            return
        on = 0
        move = 0
        time = 0
        for i in range(2,len(self.ecoords)):
            x1 = self.ecoords[i-1][0]
            y1 = self.ecoords[i-1][1]
            x2 = self.ecoords[i][0]
            y2 = self.ecoords[i][1]
            loop      = self.ecoords[i  ][2]
            loop_last = self.ecoords[i-1][2]
            
            xmax=max(xmax,x1,x2)
            ymax=max(ymax,y1,y2)
            xmin=min(xmin,x1,x2)
            ymin=min(ymin,y1,y2)
            
            dx = x2-x1
            dy = y2-y1
            dist = sqrt(dx*dx + dy*dy)
            
            if len(self.ecoords[i]) > 3:
                feed = self.ecoords[i][3]
                time = time + dist/feed*60
                
            if loop == loop_last:
                on   = on + dist 
            else:
                move = move + dist

        self.bounds = (xmin,xmax,ymin,ymax)
        self.len = on
        self.move = move
        self.gcode_time = time

    # All units used by fill are using inches as unit
    def fill_area(self, step_x, step_y, areaMaxX, areaMinY):
        # self.bounds(xmin, xmax, ymin, ymax)
        if len(self.src_ecoords)==0:
            return
        yOffset = 0
        loop = 1

        newEcoords = []

        # Tant qu'on ne dépasse pas en Y
        yMin = -step_y
        while (yMin > areaMinY):            
            # Tant qu'on ne dépasse pas en X
            xMax = step_x
            xOffset = 0
            while (xMax < areaMaxX):
                loop = self.append_translated_ecoords_to_array(newEcoords, xOffset, yOffset, loop) +1
                xMax += step_x
                xOffset += step_x

            yMin -= step_y
            yOffset -= step_y

        self.ecoords = newEcoords
        self.computeEcoordsLen()
    


    def append_translated_ecoords_to_array(self, dstArray, xOffset, yOffset, loop):
        oldLoop = self.src_ecoords[0][2]
        for i in range(len(self.src_ecoords)):

            #increment the loop if needed
            if self.src_ecoords[i][2] != oldLoop:
                loop = loop+1
                oldLoop = self.src_ecoords[i][2]

            x = self.src_ecoords[i][0] + xOffset
            y = self.src_ecoords[i][1] + yOffset
            dstArray.append([x, y, loop])

        return loop


    def addEcoord(self, newEcoord : ECoord) -> None :
        if newEcoord == None :
            return

        loop = 0 
        ecoordSize = len(self.ecoords)
        if(ecoordSize != 0) :
            loop = self.ecoords[ecoordSize-1][2] + 1

        for i in range(0, len(newEcoord.ecoords)) :
            data = newEcoord.ecoords[i]
            newData = [data[0], data[1], data[2]+loop]

            if newData[0] < self.bounds[0] :
                self.bounds[0] = newData[0]
            if newData[0] > self.bounds[1] :
                self.bounds[1] = newData[0]
            if newData[1] < self.bounds[2] :
                self.bounds[2] = newData[1]
            if newData[1] > self.bounds[3] :
                self.bounds[3] = newData[1]

            self.ecoords.append(newData)