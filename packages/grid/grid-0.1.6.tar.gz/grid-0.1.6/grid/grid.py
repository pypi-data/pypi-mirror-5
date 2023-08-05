# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>


# <codecell>

#!/usr/bin/python

'''
Daniel J. Sindhikara
sindhikara@gmail.com
Handles 3D volumetric data
Copyright 2013 Daniel Jon Sindhikara
'''

from __future__ import division
import numpy as np
import os

# <codecell>

class Grid:

    '''
Contains volumetric data
    '''

    def __init__(
        self,
        distribution,
        origin,
        gridcount,
        deltas,
        concentration=-1.0,
        ):
        if type(distribution) is list:
            self.distribution = np.array(distribution)
        elif type(distribution) is np.ndarray:
            self.distribution = distribution
        self.origin = origin
        self.gridcount = gridcount
        self.deltas = deltas
        self.concentration = concentration  # in molar

    def getvalue(self, coord): 
        return linearinterpolatevalue(self.distribution, self.origin,
                self.deltas, coord)

    def writedx(self, filename):
        printdxfrom3d(self.distribution, self.origin, self.deltas,
                      self.gridcount, filename)

    def nearestgridindices(self, coord):
        '''
        Given a 3D cartesian coordinate, return nearest grid indices
        '''

        gridindices = [int(round((coord[i] - self.origin[i])
                       / self.deltas[i])) for i in range(3)]
        return gridindices

    def coordfromindices(self, indices):
        return [indices[i] * self.deltas[i] + self.origin[i] for i in
                range(3)]

    def coarseRDF(self, coord):
        '''
        Given a 3D cartesian coordinate, return 1D distribution as list, spaced by gridspacing
        '''

        dist = []
        myindices = self.nearestgridindices(coord)
        for shellindex in shellindices:
            avg = 0.0
            try:
                for indexonshell in shellindex:
                    avg += self.distribution[myindices[0]
                            + indexonshell[0]][myindices[0]
                            + indexonshell[1]][myindices[2]
                            + indexonshell[2]]
                avg = avg / len(shellindex)
                dist.append(avg)
            except IndexError:
                break
        return dist

    def interpRDF(
        self,
        coord,
        delta,
        limit,
        ):
        '''
        Given 3D cartesian coordinate (list-like object of floats),
        delta (float), and limit (float),
        
        return RDF

        by averaging linear interpolated g(r_vec) on points on spherical shell.
        '''

        spherefilename = \
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'data', 'points', '200.pts')
        spherepoints = [[float(element) for element in line.split()]
                        for line in open(spherefilename).readlines()]
        rdf = []
        for radius in np.arange(0, limit, delta):
            mysum = 0
            for point in spherepoints:
                mysum += self.getvalue([point[dim] * radius
                        + coord[dim] for dim in range(3)])
            rdf.append(float(mysum / len(spherepoints)))
        return rdf

# <codecell>

def rdf23dgrid(
    rdf,
    rdfdelta,
    griddelta,
    gridorigin,
    shellindices,
    ):
    '''
    Convert 1d RDF to 3D grid.
    '''

    gridcount = [len(shellindices) * 2 + 1] * 3  # + 1 is to make it odd, let
    mydist = np.array([[[1.0 for i in range(gridcount[0])] for j in
                      range(gridcount[1])] for k in
                      range(gridcount[2])])

    indexmultiplier = int(griddelta / rdfdelta)  # from 3D grid index to 1D rdf index
    for (i, shell) in enumerate(shellindices):  # loop through shells
        myrdf = rdf[i * indexmultiplier]
        for shellindex in shell:
            distindex = tuple([shellindex[dim] + int(gridcount[dim]
                              / 2) for dim in range(3)])

            # above will put shell 0 at the int(gridcount/2) aka numshells/2 + 1

            mydist[distindex] = myrdf
    return Grid(mydist, gridorigin, gridcount, [griddelta] * 3)

# <codecell>

def dx2Grid(dxfilename):
    '''
    Reads a dx file into a Grid class object 
    '''

    # for now Ghetto rigged to use old readdx function

    (distributions, origin, deltas, gridcount) = readdx([dxfilename])
    return Grid(distributions[0], origin, gridcount, deltas)

# <codecell>

def readdx(filenames):
    '''
    Reads one or more dx files into memory
    returns grid data and single 4D array containing dx data [index][xindex][yindex][zindex]
    '''

    import gzip
    import numpy as np

    def opendxfile(filename):
        if 'gz' in filename:
            dxfile = gzip.open(filename, 'rb')
        else:
            dxfile = open(filename, 'r')
        return dxfile

    dxfile = opendxfile(filenames[0])
    dxlines = []
    for i in range(10):  # only need the first few lines to get grid data
        dxlines.append(dxfile.readline())
    dxfile.close()
    gridcount = []
    origin = []
    deltas = [0, 0, 0]
    startline = 0
    for (i, line) in enumerate(dxlines):
        splitline = line.split()
        if len(splitline) > 2:
            if splitline[1] == '1':
                gridcount.append(int(splitline[5]))
                gridcount.append(int(splitline[6]))
                gridcount.append(int(splitline[7]))

                # print "# gridcounts ",gridcount

            if splitline[0] == 'origin':
                origin.append(float(splitline[1]))
                origin.append(float(splitline[2]))
                origin.append(float(splitline[3]))
            if splitline[0] == 'delta':
                if float(splitline[1]) > 0:
                    deltas[0] = float(splitline[1])
                if float(splitline[2]) > 0:
                    deltas[1] = float(splitline[2])
                if float(splitline[3]) > 0:
                    deltas[2] = float(splitline[3])
            if splitline[1] == '3':
                numpoints = int(splitline[9])

                # print "# Total number of gridpoints is ",numpoints

                startline = i + 1
        if startline > 1:
            break
    distributions = np.array([[[[0.0 for x in range(gridcount[2])]
                             for y in range(gridcount[1])] for z in
                             range(gridcount[0])] for w in
                             range(len(filenames))])
    gridvolume = deltas[0] * deltas[1] * deltas[2]

    # print "# I have to read",len(filenames)*gridcount[2]*gridcount[1]*gridcount[0],"values."

    for (i, dxfilename) in enumerate(filenames):
        dxfile = opendxfile(dxfilename)
        dxtext = dxfile.read()
        dxfile.close()
        splittext = dxtext.split()
        del splittext[0:splittext.index('follows') + 1]  # get rid of header text, last word is "follows"
        floats = []
        for element in splittext:
            if len(element) > 0:
                try:
                    floats.append(float(element))
                except ValueError:
                    pass
        assert len(floats) == gridcount[0]*gridcount[1]*gridcount[2]
        index = 0
        for x in range(gridcount[0]):
            for y in range(gridcount[1]):
                for z in range(gridcount[2]):
                    distributions[i][x][y][z] = floats[index]
                    index += 1  # there's probably a more pythonic way to do this

    # print "# corr[0][0][0][0] = ",distributions[0][0][0][0],"[0][-1][-1][-1]=",distributions[0][-1][-1][-1]
    # distributions=np.array(distributions)

    return (distributions, origin, deltas, gridcount)

# <codecell>

def printdxfrom1dzfast(
    values,
    origin,
    delta,
    gridcounts,
    filename,
    ):
    ''' Print a dx file'''

    f = open(filename, 'w')
    f.write("#DX file from Dan's program\n")
    f.write('object 1 class gridpositions counts {0} {1} {2}\n'.format(gridcounts[0],
            gridcounts[1], gridcounts[2]))
    f.write('origin {0} {1} {2}\n'.format(origin[0], origin[1],
            origin[2]))
    f.write('delta {0} 0 0\n'.format(delta[0]))
    f.write('delta 0 {0} 0\n'.format(delta[1]))
    f.write('delta 0 0 {0}\n'.format(delta[2]))
    f.write('object 2 class gridconnections counts {0} {1} {2}\n'.format(gridcounts[0],
            gridcounts[1], gridcounts[2]))
    f.write('object 3 class array type double rank 0 items {0} data follows\n'.format(gridcounts[0]
            * gridcounts[1] * gridcounts[2]))
    for value in values:
        f.write('{0}\n'.format(value))
    f.write('object {0} class field\n'.format(filename))
    f.close()

# <codecell>

def printdx(
    values,
    indices,
    origin,
    delta,
    gridcounts,
    filename,
    ):
    ''' Print a dx file'''

    gridvalues = [0.0] * gridcounts[0] * gridcounts[1] * gridcounts[2]
    if len(values) != len(gridvalues):
        exit('error! len(gridvalues) %s != len(values) %s'
             % (len(gridvalues), len(values)))
    for (i, value) in enumerate(values):  # warning, this doubles the memory usage
        gridindex = indices[i][2] + indices[i][1] * gridcounts[2] \
            + indices[i][0] * gridcounts[2] * gridcounts[1]
        gridvalues[gridindex] = value

    f = open(filename, 'w')
    f.write("#DX file from Dan's program\n")
    f.write('object 1 class gridpositions counts {0} {1} {2}\n'.format(gridcounts[0],
            gridcounts[1], gridcounts[2]))
    f.write('origin {0} {1} {2}\n'.format(origin[0], origin[1],
            origin[2]))
    f.write('delta {0} 0 0\n'.format(delta[0]))
    f.write('delta 0 {0} 0\n'.format(delta[1]))
    f.write('delta 0 0 {0}\n'.format(delta[2]))
    f.write('object 2 class gridconnections counts {0} {1} {2}\n'.format(gridcounts[0],
            gridcounts[1], gridcounts[2]))
    f.write('object 3 class array type double rank 0 items {0} data follows\n'.format(gridcounts[0]
            * gridcounts[1] * gridcounts[2]))
    for gridvalue in gridvalues:
        f.write('{0}\n'.format(gridvalue))
    f.write('object {0} class field\n'.format(filename))
    f.close()

# <codecell>

def printdxfrom3d(
    distribution,
    origin,
    delta,
    gridcounts,
    filename,
    ):
    ''' print a dx file given a 3d list'''

    f = open(filename, 'w')
    f.write("#DX file from Dan's program\n")
    f.write('object 1 class gridpositions counts {0} {1} {2}\n'.format(gridcounts[0],
            gridcounts[1], gridcounts[2]))
    f.write('origin {0} {1} {2}\n'.format(origin[0], origin[1],
            origin[2]))
    f.write('delta {0} 0 0\n'.format(delta[0]))
    f.write('delta 0 {0} 0\n'.format(delta[1]))
    f.write('delta 0 0 {0}\n'.format(delta[2]))
    f.write('object 2 class gridconnections counts {0} {1} {2}\n'.format(gridcounts[0],
            gridcounts[1], gridcounts[2]))
    f.write('object 3 class array type double rank 0 items {0} data follows\n'.format(gridcounts[0]
            * gridcounts[1] * gridcounts[2]))
    for i in range(gridcounts[0]):
        for j in range(gridcounts[1]):
            for k in range(gridcounts[2]):
                f.write('{0}\n'.format(distribution[i][j][k]))
    f.write('object {0} class field\n'.format(filename))
    f.close()

# <codecell>

def getcoordfromindices(indices, origin, deltas):
    '''Returns coordinates as a length 3 list of floats 
    '''

    coords = []
    for i in range(3):
        coords.append(float(indices[i]) * deltas[i] + origin[i])
    return coords

# <codecell>

def getindicesfromcoord(coord, origin, deltas):
    indices = []
    for i in range(3):
        indices.append(int((coord[i] - origin[i]) / deltas[i] + 0.5))
    return indices

# <codecell>

def precomputeshellindices(maxindex):
    '''return a list of 3d lists containing the indices in successive search shells
i.e. 0 = [0,0,0]
     1 = [[-1,-1,-1],[-1,0,-1],..
    essentially how much to shift i,j,k indices from center to find grid point on shell
at index radius
    This will make evacuation phase faster
    '''

    from math import sqrt
    shellindices = [[[0, 0, 0]]]
    for index in range(1, maxindex):

        # range[0]

        indicesinthisshell = []
        for i in range(-index, index + 1):
            for j in range(-index, index + 1):
                for k in range(-index, index + 1):

                    # print "math.sqrt(i*i + j*j + k*k))=",math.sqrt(i*i + j*j + k*k),"index = ",index

                    if int(sqrt(i * i + j * j + k * k)) == index:  # I think this will miss some
                        indicesinthisshell.append((i, j, k))
        shellindices.append(tuple(indicesinthisshell))
    return tuple(shellindices)

# <codecell>

def createprecomputedindicesjson(numshells=40):
    '''
stores a local file called shells.json
    '''

    shellindices = precomputeshellindices(numshells)
    from json import dump
    import os
    outfile = os.path.join(os.path.dirname(__file__), "data", 'shells.json')
    f = open(outfile, 'w')
    dump(shellindices, f)
    f.close()

# <codecell>

def readshellindices():
    import os
    infile = os.path.join(os.path.dirname(__file__),"data", 'shells.json')
    from json import load
    f = open(infile, 'rb')
    shellindices = load(f)
    return shellindices

# <codecell>

def getlinearweightsandindices(origin, deltas, coord):
    '''
given one 3D coordinate, return 8 corner indices and weights
that would allow direct linear interpolation
This subroutine is separated from linearinterpolatevalue to allow
precomputation of weights and indices
    '''

    ccrd = []  # coordinates of corners
    cindices = []  # indices of corners
    cdist = []  # distances to corner

    # below store indices and coordinates of 8 nearby corners

    cindices.append((int((coord[0] - origin[0]) / deltas[0]),
                    int((coord[1] - origin[1]) / deltas[1]),
                    int((coord[2] - origin[2]) / deltas[0])))
    ccrd.append(getcoordfromindices(cindices[-1], origin, deltas))
    cindices.append((cindices[0][0] + 1, cindices[0][1],
                    cindices[0][2]))
    ccrd.append(getcoordfromindices(cindices[-1], origin, deltas))
    cindices.append((cindices[0][0], cindices[0][1] + 1,
                    cindices[0][2]))
    ccrd.append(getcoordfromindices(cindices[-1], origin, deltas))
    cindices.append((cindices[0][0], cindices[0][1], cindices[0][2]
                    + 1))
    ccrd.append(getcoordfromindices(cindices[-1], origin, deltas))
    cindices.append((cindices[0][0] + 1, cindices[0][1] + 1,
                    cindices[0][2]))
    ccrd.append(getcoordfromindices(cindices[-1], origin, deltas))
    cindices.append((cindices[0][0], cindices[0][1], cindices[0][2]
                    + 1))
    ccrd.append(getcoordfromindices(cindices[-1], origin, deltas))
    cindices.append((cindices[0][0] + 1, cindices[0][1], cindices[0][2]
                    + 1))
    ccrd.append(getcoordfromindices(cindices[-1], origin, deltas))
    cindices.append((cindices[0][0] + 1, cindices[0][1] + 1,
                    cindices[0][2] + 1))
    ccrd.append(getcoordfromindices(cindices[-1], origin, deltas))
    totalweight = 0.0
    weights = []
    exactindex = -1
    for (i, crd) in enumerate(ccrd):
        if crd == coord:
            exactindex = i
    if exactindex > -1:
        weights = [0.0 for i in range(8)]
        weights[exactindex] = 1.0
        totalweight = 1.0
    else:
        for crd in ccrd:  # coordinates of corners
            myweight = ((coord[0] - crd[0]) ** 2 + (coord[1] - crd[1])
                        ** 2 + (coord[2] - crd[2]) ** 2) ** -0.5
            weights.append(myweight)
            totalweight += myweight
    normweights = [weight / totalweight for weight in weights]
    return (normweights, cindices)

# <codecell>

def linearinterpolatevalue(
    distribution,
    origin,
    deltas,
    coord,
    ):
    '''given a 3d coordinate, using a linear interpolation from the 8 nearest gridpoints,
estimate the value at that coordinate
    '''

    (weights, cindices) = getlinearweightsandindices(origin, deltas,
            coord)
    value = 0
    for (i, mycindices) in enumerate(cindices):
        try:
            value += distribution[mycindices] * weights[i]
        except:
            print 'Failed to find gridpoint at', mycindices
            print 'coordinate=', coord
            return False
    return value

# <codecell>

def calcrdf(
    distribution,
    origin,
    deltas,
    coord,
    deltar=0.1,
    maxradius=20.0,
    numsumgrids=20,
    ):
    '''
Calculates the radial distribution function about a point using the 3d distribution
    '''

    def shellintegral(radius, delta, center):
        sum = 0.0
        count = 0.0
        for i in range(int(2.0 * radius / delta)):
            for j in range(int(2.0 * radius / delta)):
                for k in range(int(2.0 * radius / delta)):
                    x = float(i) * delta - radius
                    y = float(j) * delta - radius
                    z = float(k) * delta - radius
                    thisrad = (x ** 2 + y ** 2 + z ** 2) ** 0.5
                    if thisrad > radius - delta / 2.0 and thisrad \
                        < radius + delta / 2.0:
                        mycoord = [center[0] + x, center[1] + y,
                                   center[2] + z]
                        sum += linearinterpolatevalue(distribution,
                                origin, deltas, mycoord)
                        count += 1.0
        sum = sum / count
        return sum

    radii = [(float(i) + 0.5) * deltar for i in range(int(maxradius
             / deltar))]
    gr = []
    for (i, rad) in enumerate(radii):
        subdelta = deltar * (float(i) + 0.5) / float(numsumgrids)
        gr.append(shellintegral(rad, subdelta, coord))

    return (radii, gr)

# <codecell>





# <codecell>


