import rhinoscriptsyntax as rs
import math as m

#### SCRIPT PURPOSE####
# this script uses an overlayed grid on a mesh
# to measure the curvature of each grid line at its
# respective intersection points. Using those points
# as reference, curvature values are assigned to the 
# meshes vertices and turned into colors

class contours:
    def __init__(self,EVALPTS,BASECRV,VCRVS):
        #This class takes a single Ucrv all of the horizontal
        #oriented Vcrvs the intersection points between them
        self.pts = EVALPTS
        self.crv = BASECRV
        self.vCrvs = VCRVS
        self.uVals = []
        self.vVals = []
        self.colors = []
        self.position = rs.PointAdd([0,0,0],[0,0,0])
        #This section finds the center position of the baseCrv#
        for i in range(len(self.pts)):
            self.position = rs.PointAdd(self.position,self.pts[i])
        self.position = self.position/len(self.pts)
        #######################################################
    def locateVCrvs(self):
        sortedV = []
        #Function generates a list of Vcrvs that match up to
        #each intersection (grid point) on the Ucrv(baseCrv)
        #being evaluated
        for i in range(len(self.pts)):
            minDist = 10000000
            for j in range(len(self.vCrvs)): 
                param = rs.CurveClosestPoint(self.vCrvs[j],self.pts[i])
                closePt = rs.EvaluateCurve(self.vCrvs[j],param)
                dist = rs.Distance(closePt,self.pts[i])
                if dist<minDist:
                    minDist = dist
                    closest = j
            sortedV.append(self.vCrvs[closest])
        #sortedV is the list of Vcrvs that is closest to each evalPt
        return sortedV
    def uCurvature(self):
        #This fuction retrieves the curvature value in the U direction
        #for each point on the baseCrv (Ucrv)
        Curvatures = []
        for i in range(len(self.pts)):
            param = rs.CurveClosestPoint(self.crv,self.pts[i])
            Curvatures.append(rs.CurveCurvature(self.crv,param)[3])
        return Curvatures
    def vCurvature(self):
        #This fuction retrieves the curvature value in the V direction
        #for each point on the baseCrv(Ucrv)
        Curvatures = []
        #Each point along the baseCrv is assigned a corresponding Vcrv
        sortedV = self.locateVCrvs()
        for i in range(len(self.pts)):
            param = rs.CurveClosestPoint(sortedV[i],self.pts[i])
            Curvatures.append(rs.CurveCurvature(sortedV[i],param)[3])
        return Curvatures
    def collectUV(self):
        self.uVals = self.uCurvature()
        self.vCrvs = self.locateVCrvs()
        self.vVals = self.vCurvature() 

def curvekey(curve):
    point = rs.CurveStartPoint(curve)
    return point[2]

def SortCurvesByZ(curves):
    #Curves in the horizontal (V direction) are sorted by height
    sorted_curves = sorted(curves, key=curvekey)
    return sorted_curves

def SortCurvesByPt(curves,pt):
    #Curves in the vertical (U direction) are sorted from their distance
    #from a reference point
    indexes = []
    distances = []
    sorted = []
    min = 1000000000
    for i in range(len(curves)):
        param = rs.CurveClosestPoint(curves[i],pt)
        crvPt = rs.EvaluateCurve(curves[i],param)
        distances.append(rs.Distance(crvPt,pt))
    for i in range(len(curves)):
        for j in range(len(distances)):
            if distances[j]<min:
                min = distances[j]
                index = j
        indexes.append(index)
        sorted.append(curves[index])
        distances[index] = 1000000000
        min = 1000000000
    return sorted

def Main():
    #### A pre-existing mesh and projected gridlines are selected in rhino 
    mesh = rs.GetObject("please select mesh",rs.filter.mesh)
    uCrvs = rs.GetObjects("please select vertical contours",rs.filter.curve)
    vCrvs = rs.GetObjects("please select horizontal contours",rs.filter.curve)
    refPt = rs.GetObject("please enter reference point",rs.filter.point)
    #### Ucrvs and Vcrvs are ordered by the ref point and height respectively
    uCrvs = SortCurvesByPt(uCrvs,refPt)
    vCrvs = SortCurvesByZ(vCrvs)
    myContours = []
    vertices = rs.MeshVertices(mesh)
    rebuiltV = []
    positions =[]
    red = []
    green = []
    colors = []
    #Grid Curves in V are copied and rebuilt as degree 3 to measure curvature
    for i in range(len(vCrvs)):
        rebuild = rs.CopyObject(vCrvs[i])
        rs.RebuildCurve(rebuild,3,300)
        rebuiltV.append(rebuild)
    #uCrvs intersect with vCrvs to gather up intersection points
    for i in range(len(uCrvs)):
        evalPts=[]
        for j in range(len(vCrvs)):
            intersectionPts = rs.CurveCurveIntersection(uCrvs[i],vCrvs[j])
            if intersectionPts!=None:
                for i in range(len(intersectionPts)):
                    if intersectionPts[i][0]==1:
                        evalPts.append(intersectionPts[i][1])
        rebuildU = rs.CopyObject(uCrvs[i])
        rs.RebuildCurve(rebuildU,3,300)
        #the Ucrv is rebuilt as degree 3 to measure curvature
        #A new contour object is created with rebuilt Ucrv, rebuilt Vcrvs
        #and intersection points
        myContours.append(contours(evalPts,rebuildU,rebuiltV))
    maxRed = 0
    maxGreen = 0
    for i in range(len(myContours)):
        positions.append(myContours[i].position)
    for i in range(len(vertices)):
        #Using the contour objects positions the verticies find their nearest
        #contour object... and then find the nearest grid point to reduce
        #computing time
        contourIndex = rs.PointArrayClosestPoint(positions,vertices[i])
        indexEvalPt = rs.PointArrayClosestPoint(myContours[contourIndex].pts,vertices[i])
        #Curvatures in the U and V direction are asigned to each vertex
        myContours[contourIndex].collectUV()
        #The U and V curvatures are turned into r and g values respectively
        red.append(myContours[contourIndex].uVals[indexEvalPt])
        green.append(myContours[contourIndex].vVals[indexEvalPt])
    #After all the r and g values are found for the entire mesh
    #The values are remapped to the 0-255 range and rgb values are stored
    #in a list called colors
    for i in range(len(vertices)):
        if red[i]>maxRed:
            maxRed = red[i]
        if green[i]>maxGreen:
            maxGreen = green[i]
    for i in range(len(vertices)):
        red[i] = red[i]/(maxRed+.001)*255
        green[i] = green[i]/(maxGreen+.001)*255
        colors.append([red[i],green[i],0])
    #the list of rgb values creates the colors on the mesh at each vertex
    rs.MeshVertexColors(mesh,colors)

Main()