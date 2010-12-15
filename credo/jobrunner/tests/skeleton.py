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

from credo.modelrun import ModelRun
from credo.modelresult import ModelResult
from credo.modelsuite import ModelSuite

class SkeletonModelRun(ModelRun):
    def __init__(self, name, outputPath):
        self.name = name
        self.outputPath = outputPath
    pass

class SkeletonModelResult(ModelResult):
    def __init__(self, modelName):
        self.modelName = modelName
    pass

class SkeletonModelSuite(ModelSuite):
    def __init__(self):
        self.runs = []
        self.resultsList = []
