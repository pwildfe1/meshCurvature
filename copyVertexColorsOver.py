import rhinoscriptsyntax as rs
import math as m

def Main():
    sourceMesh = rs.GetObject("select source mesh for colors",rs.filter.mesh)
    newMesh = rs.GetObject("select mesh to change",rs.filter.mesh)
    srcVertices = rs.MeshVertices(sourceMesh)
    srcColors = rs.MeshVertexColors(sourceMesh)
    vertices = rs.MeshVertices(newMesh)
    newColors = []
    for i in range(len(vertices)):
        filtered = []
        indexes = []
        for j in range(len(srcVertices)):
            if rs.Distance(srcVertices[j],vertices[i])<1:
                filtered.append(srcVertices[j])
                indexes.append(j)
        filteredIndex = rs.PointArrayClosestPoint(filtered,vertices[i])
        index = indexes[filteredIndex]
        newColors.append(srcColors[index])
    rs.MeshVertexColors(newMesh,newColors)

Main()