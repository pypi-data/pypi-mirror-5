#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2012 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

# the purpose of this file is to collect all utility methods that compute
# attributes of blocks, based on their contents. 

__all__ = ['has_discrete_variables']

from six import itervalues, iteritems
from coopr.pyomo.base import Var, BooleanSet, IntegerSet, Block


def has_discrete_variables(block):
    # Return True if there is a discrete variable in this block or any
    # sub-block.
    for block in block.all_blocks():
        for var in itervalues(block.active_subcomponents(Var)):
            if isinstance(var.domain, IntegerSet) \
                    or isinstance(var.domain, BooleanSet):
                return True

    return False
