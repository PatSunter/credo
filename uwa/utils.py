"""A module for general utility functions in UWA, that don't clearly fit
into other modules."""

import os

def prepareOutputLogDirs(outputPath, logPath):
    """Prepare the output and log dirs - usually in preparation
    for running a :class:`uwa.modelrun.ModelRun`."""
    # TODO: complete    
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    if not os.path.exists(logPath):
        os.makedirs(logPath)
