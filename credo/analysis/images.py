##  Copyright (C), 2010, Monash University
##  Copyright (C), 2010, Victorian Partnership for Advanced Computing (VPAC)
##  
##  This file is part of the CREDO library.
##  Developed as part of the Simulation, Analysis, Modelling program of 
##  AuScope Limited, and funded by the Australian Federal Government's
##  National Collaborative Research Infrastructure Strategy (NCRIS) program.
##
##  This library is free software; you can redistribute it and/or
##  modify it under the terms of the GNU Lesser General Public
##  License as published by the Free Software Foundation; either
##  version 2.1 of the License, or (at your option) any later version.
##
##  This library is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  Lesser General Public License for more details.
##
##  You should have received a copy of the GNU Lesser General Public
##  License along with this library; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
##  MA  02110-1301  USA

"""Utilities for basic image analysis and testing in relation to CREDO.
Original image test comparison scripts contributed by Owen Kaluza.
You will need the Python Imaging Library (PIL) installed to use."""

import sys
from math import sqrt
from math import fabs
import Image
import ImageChops

def normalise(array, maxval):
   norm = [float(x) / maxval for x in array]
   return norm

def colourDiff(img1, img2):
    """Calculate image difference by colour histogram.

    :arg img1: open PIL image
    :arg img2: open PIL image
    :returns: float representing euclidian distance between images
      in colour histogram space
    """

    #Calculate image difference by colour histogram 
    width, height = img1.size
    pixels = width * height

    #Normalise values to [0,1]
    hist1 = normalise(img1.histogram(), pixels)
    hist2 = normalise(img2.histogram(), pixels)

    #Reduce from 256 to 64 bins per component
    hist_1 = [0] * (len(hist1) / 4)
    hist_2 = [0] * (len(hist2) / 4)
    for x in range(len(hist1)):
        hist_1[x/4] += hist1[x]
        hist_2[x/4] += hist2[x]

    #Subtract normalised histograms to get a distance vector
    dist = [fabs(a - b) for a, b in zip(hist_1, hist_2)]

    #Calculate euclidean distance between images in colour histogram space
    dist = sqrt(sum([x*x for x in (dist)]))

    #Return value in range [0,1]
    return dist / sqrt(6)

def pixelDiff2x2(img1, img2):
    """Compare two open images on a 2x2 basis."""
    #Simple check for transforms: resize to 2x2 and compare pixel by pixel
    img1b = img1.resize((2, 2), Image.ANTIALIAS)
    img2b = img2.resize((2, 2), Image.ANTIALIAS)

    return pixelDiff(img1b, img2b)

def pixelDiff(img1, img2):
    """Compare two open images on a pixel by pixel basis."""
    width, height = img1.size
    pixels = width * height

    #This subtracts each pixel value from the other
    diff = ImageChops.difference(img1, img2)
    #Create an image vector
    components = []
    pix = diff.load()
    width, height = diff.size
    for x in range(width):
        for y in range(height):
            for z in pix[x,y]:
                components.append(z)

    #Calculate euclidean distance 
    dist = sqrt(sum([x*x for x in (components)]))

    #Scale to [0,1] by dividing by maximum possible difference
    n = len(img1.getbands())
    maxdist = sqrt(pixels * n * (255*255))   #pixels * components * (255 possible values)^2
    return dist / maxdist

def compare(imgFilename1, imgFilename2, verbose=False):
    """Compare two image files.

    :returns: A tuple containing the diffs for each component
      (colour space, 4 pixel subsample)."""
    img1 = Image.open(imgFilename1)
    img2 = Image.open(imgFilename2)
    #Check size and components match
    if img1.size != img2.size or img1.getbands() != img2.getbands():
        return False
    #Colour comparison
    dist1 = colourDiff(img1, img2)
    if verbose: print "Colour space difference: %f" % dist1
    #Colour compare is not sensitive to flip/rotate so do 
    #a simple pixel by pixel compare as well
    dist2 = pixelDiff2x2(img1, img2)
    if verbose: print "Difference on 4 pixel subsample: %f" % dist2
    #Test fails if either value outside tolerance
    return dist1, dist2


if __name__ == "__main__":
    #Example usage, compare two images passed on command line
    diffs = compare(sys.argv[1], sys.argv[2])
