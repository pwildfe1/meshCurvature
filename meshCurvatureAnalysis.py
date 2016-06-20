import rhinoscriptsyntax as rs
import math as m

class contours:
    def __init__(self,EVALPTS,BASECRV,VCRVS,RESO):
        self.pts = EVALPTS
        self.crv = BASECRV
        self.vCrvs = VCRVS
        self.reso = RESO
        self.uVals = []
        self.vVals = []
        self.colors = []
        self.position = rs.PointAdd([0,0,0],[0,0,0])
        for i in range(len(self.pts)):
            self.position = rs.PointAdd(self.position,self.pts[i])
        self.position = self.position/len(self.pts)
    def locateVCrvs(self):
        sortedV = []
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
        return sortedV
    def uCurvature(self):
        Curvatures = []
        for i in range(len(self.pts)):
            param = rs.CurveClosestPoint(self.crv,self.pts[i])
            Curvatures.append(rs.CurveCurvature(self.crv,param)[3])
        return Curvatures
    def vCurvature(self):
        Curvatures = []
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
    sorted_curves = sorted(curves, key=curvekey)
    return sorted_curves

def SortCurvesByPt(curves,pt):
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
    mesh = rs.GetObject("please select mesh",rs.filter.mesh)
    uCrvs = rs.GetObjects("please select vertical contours",rs.filter.curve)
    vCrvs = rs.GetObjects("please select horizontal contours",rs.filter.curve)
    refPt = rs.GetObject("please enter reference point",rs.filter.point)
    uCrvs = SortCurvesByPt(uCrvs,refPt)
    vCrvs = SortCurvesByZ(vCrvs)
    myContours = []
    vertices = rs.MeshVertices(mesh)
    rebuiltV = []
    positions =[]
    red = []
    green = []
    colors = []
    for i in range(len(vCrvs)):
        rebuild = rs.CopyObject(vCrvs[i])
        rs.RebuildCurve(rebuild,3,300)
        rebuiltV.append(rebuild)
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
        myContours.append(contours(evalPts,rebuildU,rebuiltV,.01))
    maxRed = 0
    maxGreen = 0
    for i in range(len(myContours)):
        positions.append(myContours[i].position)
    for i in range(len(vertices)):
        contourIndex = rs.PointArrayClosestPoint(positions,vertices[i])
        indexEvalPt = rs.PointArrayClosestPoint(myContours[contourIndex].pts,vertices[i])
        myContours[contourIndex].collectUV()
        red.append(myContours[contourIndex].uVals[indexEvalPt])
        green.append(myContours[contourIndex].vVals[indexEvalPt])
    for i in range(len(vertices)):
        if red[i]>maxRed:
            maxRed = red[i]
        if green[i]>maxGreen:
            maxGreen = green[i]
    for i in range(len(vertices)):
        red[i] = red[i]/(maxRed+.001)*255
        green[i] = green[i]/(maxGreen+.001)*255
        colors.append([red[i],green[i],0])
    rs.MeshVertexColors(mesh,colors)

Main()