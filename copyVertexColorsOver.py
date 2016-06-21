import rhinoscriptsyntax as rs
import math as m

######## THIS SCRIPT PULLS COLORS FROM ONE MESH TO ANOTHER ##########
# This helps if you modify a mesh through splitting and color is lost
# you can overalay that modified mesh on its original and the colors
# will transfer over.

def Main():
    #sourceMesh is the original mesh, newMesh is the mesh we want to copy
    #the colors to.
    sourceMesh = rs.GetObject("select source mesh for colors",rs.filter.mesh)
    newMesh = rs.GetObject("select mesh to change",rs.filter.mesh)
    srcVertices = rs.MeshVertices(sourceMesh)
    srcColors = rs.MeshVertexColors(sourceMesh)
    vertices = rs.MeshVertices(newMesh)
    newColors = []
    for i in range(len(vertices)):
        filtered = []
        indexes = []
        # This section filters out far vertices to save computing time
        for j in range(len(srcVertices)):
            if rs.Distance(srcVertices[j],vertices[i])<1:
                filtered.append(srcVertices[j])
                indexes.append(j)
        ##############################################################
        filteredIndex = rs.PointArrayClosestPoint(filtered,vertices[i])
        index = indexes[filteredIndex]
        newColors.append(srcColors[index])
    rs.MeshVertexColors(newMesh,newColors)

Main()