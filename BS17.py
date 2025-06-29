'''
BS17.py
'''

import sys
import os
import json
from circuit import *
import correction


class Code:

    code_name = 'Bacon-Shor17'

    stabilizers = [
                    [('X',0), ('X',1), ('X',3), ('X',4), ('X',6), ('X',7)],
                    [('X',1), ('X',2), ('X',4), ('X',5), ('X',7), ('X',8)],
                    [('Z',0), ('Z',3), ('Z',1), ('Z',4), ('Z',2), ('Z',5)],
                    [('Z',3), ('Z',6), ('Z',4), ('Z',7), ('Z',5), ('Z',8)],
                   ]

    logical_opers = {'X': [('X',0), ('X',1), ('X',2), ('X',3), ('X',4), ('X',5), 
                           ('X',6), ('X',7), ('X',8)],
                     'Z': [('Z',0), ('Z',1), ('Z',2), ('Z',3), ('Z',4), ('Z',5), 
                           ('Z',6), ('Z',7), ('Z',8)]
                    }

    lookuptable = {
            'Xstabs': { '00': [],
                        '01': [2],
                        '10': [0],
                        '11': [1]
                      },
            'Zstabs': { '00': [],
                        '01': [6],
                        '10': [0],
                        '11': [3]
                       }
            }
