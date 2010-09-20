import itertools
import operator
from credo import modelsuite as msuite
from credo.modelrun import ModelRun
import credo.modelsuite as msuite

l1 = range(-3000, 3001, 1000)
l2 = [0.4, 0.5, 0.7]

v1 = msuite.StgXMLVariant("minX", l1)
v2 = msuite.StgXMLVariant("gravity", l2)

varDicts = msuite.getVariantsDicts(itertools.izip, [v1, v2])
