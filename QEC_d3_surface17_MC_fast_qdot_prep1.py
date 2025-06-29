import sys
import os
import time
import json
import copy
import random as rd
import multiprocessing as mp
import circuit as cir
import steane
import surface17 as surf17
import BS17
import correction as cor
import chper_wrapper as wrapper
import MC_functions as mc
import qcircuit_functions as qfun
import qcircuit_wrapper as qwrap
#from visualizer import browser_vis as brow


chp_loc = './chp_extended'
error_model = 'qdot1'
p1, p2, p_meas, I_gate_data, I_gate_anc = 0.01, 0.01, 0.01, 0.01, 0.01
I_prep, p_prep, I_meas = 0.1, 0.1, 0.1

# these don't matter for the fast sampler
error_dict, Is_after2q, Is_after_1q = wrapper.dict_for_error_model(error_model, p1, p2, 
                                                                   p_meas, I_gate_data,
                                                                   I_gate_anc, I_prep,
                                                                   p_prep, I_meas)
error_info = mc.read_error_info(error_dict)
#print error_dict
#sys.exit(0)



n_proc = int(sys.argv[1])
QEC_kind = sys.argv[2]   # surface17 or surface17min or BS17
state = sys.argv[3]  # either 'Z' or 'X'

# Read the json file with the subset information
#subset_filename = './MC_results/QECd3_surface17/qdot1/prep/subset_dictST.json'
#subset_filename = './MC_results/QECd3_surface17/qdot1/2/subset_dictST.json'
subset_filename = './MC_results/QECd3_surface17/qdot1/prep/subset_dictLDintersection.json'
#subset_filename = './MC_results/QECd3_BS17/qdot1/prep/subset_dictLD.json'
subset_file = open(subset_filename, 'r')
subset_dict = json.load(subset_file)
subset_file.close()



#n_rounds = 2
#even_spaced = True

# Define initial state
#if QEC_kind[:9] == 'surface17':
    #init_stabs = surf17.Code.stabilizers_CHP[state][:]
    #init_destabs = surf17.Code.destabilizers_CHP[state][:]
    #init_state = [init_stabs, init_destabs]
    
    # for the preparation circuit, we don't define an initial state
    # because the circuit has prep gates at the beginning.

init_state = [[],[]]


if QEC_kind == 'surface17':
    output_folder = './MC_results/QECd3_surface17/'+error_model+'/prep/'+state+'/'
elif QEC_kind == 'surface17min':
    output_folder = './MC_results/QECd3_surface17/'+error_model+'/prepmin/'+state+'/'
elif QEC_kind == 'BS17':
    output_folder = './MC_results/QECd3_BS17/'+error_model+'/prep/'+state+'/'




def generate_wait_circ(n_data):
    '''
    '''

    circ_I = cir.Circuit()
    for i in range(n_data):
        circ_I.add_gate_at([i], 'I_idle')

    return circ_I






def generate_bare_meas_qdot_all_stabs(idle_prep):
    '''
    Generates stabilizer measurements with bare ancilla, no cat states,
    for the solid-state-specific schedule

    idle_prep: True = the ancillae state prep takes time 
               False = the ancillae state prep is instantaneous
               (no memory errors on data qubits) 
    ''' 

    n_data = 9
    n_ancilla = 8
    
    bare_meas_circ = cir.Circuit()

    # time step 0: preparation of the ancillae
    # I_meas on all data qubits to account for memory errors
    # associated to the idling time
    
    if idle_prep:
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_prep')
    for i in range(n_data, n_data+n_ancilla):
        bare_meas_circ.add_gate_at([i], 'PrepareZPlus')
        bare_meas_circ.add_gate_at([i], 'H')  # later change this for Y rotation
        

    # time step 1
    # CNOTs for X stabs
    bare_meas_circ.add_gate_at([0], 'H')
    bare_meas_circ.add_gate_at([4], 'H')
    bare_meas_circ.add_gate_at([11,0], 'CZ')
    bare_meas_circ.add_gate_at([14,4], 'CZ')
    bare_meas_circ.add_gate_at([0], 'H')
    bare_meas_circ.add_gate_at([4], 'H')
    # CZs for Z stabs
    bare_meas_circ.add_gate_at([10,3], 'CZ')
    bare_meas_circ.add_gate_at([12,5], 'CZ')
    bare_meas_circ.add_gate_at([13,7], 'CZ')
    # I_gate on all qubits to account for memory errors
    for i in range(n_data):
        bare_meas_circ.add_gate_at([i], 'I_gate_data')
    for i in range(n_data, n_data+n_ancilla):
        bare_meas_circ.add_gate_at([i], 'I_gate_anc')


    # time step 2
    # CNOTs for X stabs
    bare_meas_circ.add_gate_at([1], 'H')
    bare_meas_circ.add_gate_at([5], 'H')
    bare_meas_circ.add_gate_at([7], 'H')
    bare_meas_circ.add_gate_at([11,1], 'CZ')
    bare_meas_circ.add_gate_at([14,5], 'CZ')
    bare_meas_circ.add_gate_at([16,7], 'CZ')
    bare_meas_circ.add_gate_at([1], 'H')
    bare_meas_circ.add_gate_at([5], 'H')
    bare_meas_circ.add_gate_at([7], 'H')
    # CZs for Z stabs
    bare_meas_circ.add_gate_at([10,0], 'CZ')
    bare_meas_circ.add_gate_at([12,2], 'CZ')
    bare_meas_circ.add_gate_at([13,4], 'CZ')
    # I_gate on all qubits to account for memory errors
    for i in range(n_data):
        bare_meas_circ.add_gate_at([i], 'I_gate_data')
    for i in range(n_data, n_data+n_ancilla):
        bare_meas_circ.add_gate_at([i], 'I_gate_anc')

    
    # time step 3
    # CNOTs for X stabs
    bare_meas_circ.add_gate_at([2], 'H')
    bare_meas_circ.add_gate_at([4], 'H')
    bare_meas_circ.add_gate_at([6], 'H')
    bare_meas_circ.add_gate_at([8], 'H')
    bare_meas_circ.add_gate_at([9,2], 'CZ')
    bare_meas_circ.add_gate_at([11,4], 'CZ')
    bare_meas_circ.add_gate_at([16,6], 'CZ')
    bare_meas_circ.add_gate_at([14,8], 'CZ')
    bare_meas_circ.add_gate_at([2], 'H')
    bare_meas_circ.add_gate_at([4], 'H')
    bare_meas_circ.add_gate_at([6], 'H')
    bare_meas_circ.add_gate_at([8], 'H')
    # CZs for Z stabs
    bare_meas_circ.add_gate_at([12,1], 'CZ')
    bare_meas_circ.add_gate_at([15,5], 'CZ')
    bare_meas_circ.add_gate_at([13,3], 'CZ')
    # I_gate on all qubits to account for memory errors
    for i in range(n_data):
        bare_meas_circ.add_gate_at([i], 'I_gate_data')
    for i in range(n_data, n_data+n_ancilla):
        bare_meas_circ.add_gate_at([i], 'I_gate_anc')
    

    # time step 4
    # CNOTs for X stabs
    bare_meas_circ.add_gate_at([1], 'H')
    bare_meas_circ.add_gate_at([3], 'H')
    bare_meas_circ.add_gate_at([7], 'H')
    bare_meas_circ.add_gate_at([9,1], 'CZ')
    bare_meas_circ.add_gate_at([11,3], 'CZ')
    bare_meas_circ.add_gate_at([14,7], 'CZ')
    bare_meas_circ.add_gate_at([1], 'H')
    bare_meas_circ.add_gate_at([3], 'H')
    bare_meas_circ.add_gate_at([7], 'H')
    # CZs for Z stabs
    bare_meas_circ.add_gate_at([12,4], 'CZ')
    bare_meas_circ.add_gate_at([13,6], 'CZ')
    bare_meas_circ.add_gate_at([15,8], 'CZ')
    # I_gate on all qubits to account for memory errors
    for i in range(n_data):
        bare_meas_circ.add_gate_at([i], 'I_gate_data')
    for i in range(n_data, n_data+n_ancilla):
        bare_meas_circ.add_gate_at([i], 'I_gate_anc')


    # time step 5: measurement of the ancillae
    for i in range(n_data, n_data+n_ancilla):
        bare_meas_circ.add_gate_at([i], 'H')  # later change this for Y rotation
        bare_meas_circ.add_gate_at([i], 'ImZ')
        bare_meas_circ.add_gate_at([i], 'MeasureZ')
    # I_meas on all data qubits to account for memory errors
    # associated to the idling time
    for i in range(n_data):
        bare_meas_circ.add_gate_at([i], 'I_meas')

    
    bare_meas_circ.to_ancilla(range(n_data, n_data+n_ancilla))

    return bare_meas_circ



def generate_bare_meas_qdot_all_stabs_sequential(idle_prep, first_stabs='X', prep_data=False):
    '''
    Generates stabilizer measurements with bare ancilla, no cat states,
    for the solid-state-specific schedule, sequentially

    idle_prep: True = the ancillae state prep takes time 
               False = the ancillae state prep is instantaneous
               (no memory errors on data qubits) 
    ''' 

    n_data = 9
    n_ancilla = 8
    
    bare_meas_circ = cir.Circuit()

    # time step 0: preparation of the ancillae
    # I_meas on all data qubits to account for memory errors
    # associated to the idling time
    
    if idle_prep:
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_prep')
    
    if prep_data:
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'PrepareZPlus')
        
        # if the first stabs are Z, it's because we want to prepare a logical +.
        if first_stabs == 'Z':
            for i in range(n_data):
                bare_meas_circ.add_gate_at([i], 'H')


    for i in range(n_data, n_data+n_ancilla):
        bare_meas_circ.add_gate_at([i], 'PrepareZPlus')
        bare_meas_circ.add_gate_at([i], 'H')  # later change this for Y rotation
        

    if first_stabs == 'X':

        # First, X stabs:
    
        # time step 1
        bare_meas_circ.add_gate_at([0], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        bare_meas_circ.add_gate_at([11,0], 'CZ')
        bare_meas_circ.add_gate_at([14,4], 'CZ')
        bare_meas_circ.add_gate_at([0], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')



        # time step 2
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([5], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        bare_meas_circ.add_gate_at([11,1], 'CZ')
        bare_meas_circ.add_gate_at([14,5], 'CZ')
        bare_meas_circ.add_gate_at([16,7], 'CZ')
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([5], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

    
        # time step 3
        bare_meas_circ.add_gate_at([2], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        bare_meas_circ.add_gate_at([6], 'H')
        bare_meas_circ.add_gate_at([8], 'H')
        bare_meas_circ.add_gate_at([9,2], 'CZ')
        bare_meas_circ.add_gate_at([11,4], 'CZ')
        bare_meas_circ.add_gate_at([16,6], 'CZ')
        bare_meas_circ.add_gate_at([14,8], 'CZ')
        bare_meas_circ.add_gate_at([2], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        bare_meas_circ.add_gate_at([6], 'H')
        bare_meas_circ.add_gate_at([8], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')
    

        # time step 4
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([3], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        bare_meas_circ.add_gate_at([9,1], 'CZ')
        bare_meas_circ.add_gate_at([11,3], 'CZ')
        bare_meas_circ.add_gate_at([14,7], 'CZ')
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([3], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')



        # Next, Z stabs:

        # time step 5
        bare_meas_circ.add_gate_at([10,3], 'CZ')
        bare_meas_circ.add_gate_at([12,5], 'CZ')
        bare_meas_circ.add_gate_at([13,7], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

        # time step 6
        bare_meas_circ.add_gate_at([10,0], 'CZ')
        bare_meas_circ.add_gate_at([12,2], 'CZ')
        bare_meas_circ.add_gate_at([13,4], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')
    
        # time step 7
        bare_meas_circ.add_gate_at([12,1], 'CZ')
        bare_meas_circ.add_gate_at([15,5], 'CZ')
        bare_meas_circ.add_gate_at([13,3], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

        # time step 8
        bare_meas_circ.add_gate_at([12,4], 'CZ')
        bare_meas_circ.add_gate_at([13,6], 'CZ')
        bare_meas_circ.add_gate_at([15,8], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

    
        # time step 9: measurement of the ancillae
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'H')  # later change this for Y rotation
            bare_meas_circ.add_gate_at([i], 'ImZ')
            bare_meas_circ.add_gate_at([i], 'MeasureZ')
        # I_meas on all data qubits to account for memory errors
        # associated to the idling time
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_meas')



    elif first_stabs == 'Z':
        
        # First, Z stabs:

        # time step 1
        bare_meas_circ.add_gate_at([10,3], 'CZ')
        bare_meas_circ.add_gate_at([12,5], 'CZ')
        bare_meas_circ.add_gate_at([13,7], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

        # time step 2
        bare_meas_circ.add_gate_at([10,0], 'CZ')
        bare_meas_circ.add_gate_at([12,2], 'CZ')
        bare_meas_circ.add_gate_at([13,4], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')
    
        # time step 3
        bare_meas_circ.add_gate_at([12,1], 'CZ')
        bare_meas_circ.add_gate_at([15,5], 'CZ')
        bare_meas_circ.add_gate_at([13,3], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

        # time step 4
        bare_meas_circ.add_gate_at([12,4], 'CZ')
        bare_meas_circ.add_gate_at([13,6], 'CZ')
        bare_meas_circ.add_gate_at([15,8], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

    

        # Next, X stabs:
    
        # time step 5
        bare_meas_circ.add_gate_at([0], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        bare_meas_circ.add_gate_at([11,0], 'CZ')
        bare_meas_circ.add_gate_at([14,4], 'CZ')
        bare_meas_circ.add_gate_at([0], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')


        # time step 6
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([5], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        bare_meas_circ.add_gate_at([11,1], 'CZ')
        bare_meas_circ.add_gate_at([14,5], 'CZ')
        bare_meas_circ.add_gate_at([16,7], 'CZ')
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([5], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

    
        # time step 7
        bare_meas_circ.add_gate_at([2], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        bare_meas_circ.add_gate_at([6], 'H')
        bare_meas_circ.add_gate_at([8], 'H')
        bare_meas_circ.add_gate_at([9,2], 'CZ')
        bare_meas_circ.add_gate_at([11,4], 'CZ')
        bare_meas_circ.add_gate_at([16,6], 'CZ')
        bare_meas_circ.add_gate_at([14,8], 'CZ')
        bare_meas_circ.add_gate_at([2], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        bare_meas_circ.add_gate_at([6], 'H')
        bare_meas_circ.add_gate_at([8], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')
    

        # time step 8
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([3], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        bare_meas_circ.add_gate_at([9,1], 'CZ')
        bare_meas_circ.add_gate_at([11,3], 'CZ')
        bare_meas_circ.add_gate_at([14,7], 'CZ')
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([3], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')
        

        # time step 9: measurement of the ancillae
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'H')  # later change this for Y rotation
            bare_meas_circ.add_gate_at([i], 'ImZ')
            bare_meas_circ.add_gate_at([i], 'MeasureZ')
        # I_meas on all data qubits to account for memory errors
        # associated to the idling time
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_meas')


    
    bare_meas_circ.to_ancilla(range(n_data, n_data+n_ancilla))

    return bare_meas_circ



def generate_bare_meas_qdot_stabs_onekind(idle_prep=False, kind='Z'):
    '''
    Generates stabilizer measurements with bare ancilla, no cat states,
    for the solid-state-specific schedule, sequentially

    idle_prep: True = the ancillae state prep takes time 
               False = the ancillae state prep is instantaneous
               (no memory errors on data qubits) 
    kind: Z or X
    ''' 

    n_data = 9
    n_ancilla = 8
    
    bare_meas_circ = cir.Circuit()

    # time step 0: preparation of the ancillae
    # I_meas on all data qubits to account for memory errors
    # associated to the idling time
    
    if idle_prep:
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_prep')
    
    if kind == 'X':    
        anc_indexes, idle_indexes = [9,11,14,16], [10,12,13,15]
    elif kind == 'Z':
        anc_indexes, idle_indexes = [10,12,13,15], [9,11,14,16]

    #for i in anc_indexes:
    #    bare_meas_circ.add_gate_at([i], 'PrepareZPlus')
    #    bare_meas_circ.add_gate_at([i], 'H')  # later change this for Y rotation
    #for i in idle_indexes:
    #    bare_meas_circ.add_gate_at([i], 'I')

    for i in range(n_data, n_data+n_ancilla):
        bare_meas_circ.add_gate_at([i], 'PrepareZPlus')
        bare_meas_circ.add_gate_at([i], 'H')  # later change this for Y rotation

    if kind == 'X':
    
        # time step 1
        bare_meas_circ.add_gate_at([0], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        bare_meas_circ.add_gate_at([11,0], 'CZ')
        bare_meas_circ.add_gate_at([14,4], 'CZ')
        bare_meas_circ.add_gate_at([0], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')


        # time step 2
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([5], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        bare_meas_circ.add_gate_at([11,1], 'CZ')
        bare_meas_circ.add_gate_at([14,5], 'CZ')
        bare_meas_circ.add_gate_at([16,7], 'CZ')
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([5], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

    
        # time step 3
        bare_meas_circ.add_gate_at([2], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        bare_meas_circ.add_gate_at([6], 'H')
        bare_meas_circ.add_gate_at([8], 'H')
        bare_meas_circ.add_gate_at([9,2], 'CZ')
        bare_meas_circ.add_gate_at([11,4], 'CZ')
        bare_meas_circ.add_gate_at([16,6], 'CZ')
        bare_meas_circ.add_gate_at([14,8], 'CZ')
        bare_meas_circ.add_gate_at([2], 'H')
        bare_meas_circ.add_gate_at([4], 'H')
        bare_meas_circ.add_gate_at([6], 'H')
        bare_meas_circ.add_gate_at([8], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')
    

        # time step 4
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([3], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        bare_meas_circ.add_gate_at([9,1], 'CZ')
        bare_meas_circ.add_gate_at([11,3], 'CZ')
        bare_meas_circ.add_gate_at([14,7], 'CZ')
        bare_meas_circ.add_gate_at([1], 'H')
        bare_meas_circ.add_gate_at([3], 'H')
        bare_meas_circ.add_gate_at([7], 'H')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')



    elif kind == 'Z':

        # time step 1
        bare_meas_circ.add_gate_at([10,3], 'CZ')
        bare_meas_circ.add_gate_at([12,5], 'CZ')
        bare_meas_circ.add_gate_at([13,7], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

        # time step 2
        bare_meas_circ.add_gate_at([10,0], 'CZ')
        bare_meas_circ.add_gate_at([12,2], 'CZ')
        bare_meas_circ.add_gate_at([13,4], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')
    
        # time step 3
        bare_meas_circ.add_gate_at([12,1], 'CZ')
        bare_meas_circ.add_gate_at([15,5], 'CZ')
        bare_meas_circ.add_gate_at([13,3], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

        # time step 4
        bare_meas_circ.add_gate_at([12,4], 'CZ')
        bare_meas_circ.add_gate_at([13,6], 'CZ')
        bare_meas_circ.add_gate_at([15,8], 'CZ')
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            bare_meas_circ.add_gate_at([i], 'I_gate_data')
        for i in range(n_data, n_data+n_ancilla):
            bare_meas_circ.add_gate_at([i], 'I_gate_anc')

    
    # time step 5: measurement of the ancillae
    for i in range(n_data, n_data+n_ancilla):
        if i in anc_indexes:
            bare_meas_circ.add_gate_at([i], 'H')  # later change this for Y rotation
            bare_meas_circ.add_gate_at([i], 'ImZ')
        bare_meas_circ.add_gate_at([i], 'MeasureZ')
        # I_meas on all data qubits to account for memory errors
    # associated to the idling time
    for i in range(n_data):
        bare_meas_circ.add_gate_at([i], 'I_meas')

    
    bare_meas_circ.to_ancilla(range(n_data, n_data+n_ancilla))

    return bare_meas_circ



def generate_rep_bare_meas_qdot(n_data, n_rounds, all_stabs_parallel=True, even_spaced=True):
    '''
    n_rounds = 2 or 3
    all_stabs = True if we want all the stabs together
    all_stabs = False if we want them sequentially (first X and then Z)
    '''

    rep_meas_circ = cir.Circuit()
    circ_I = generate_wait_circ(n_data)
    circ_I = cir.Encoded_Gate('WAIT', [circ_I]).circuit_wrap()
    rep_meas_circ.join_circuit(circ_I, False)


    if all_stabs_parallel:  circ_func = generate_bare_meas_qdot_all_stabs
    else:  circ_func = generate_bare_meas_qdot_all_stabs_sequential

    # idle_prep is True for the first round and False for the other ones.
    idle_prep = True
    for i in range(n_rounds):
        gate_name = 'S_%i'%i
        stab_circ = circ_func(idle_prep)
        stab_circ = cir.Encoded_Gate(gate_name, [stab_circ]).circuit_wrap()
        rep_meas_circ.join_circuit(stab_circ, False)

        #if even_spaced:
        #    circ_I = generate_wait_circ(n_data)
        #    circ_I = cir.Encoded_Gate('WAIT', [circ_I]).circuit_wrap()
        #    rep_meas_circ.join_circuit(circ_I, False)

        idle_prep = False

        if not even_spaced:
            pass
            # write this later

    circ_I = generate_wait_circ(n_data)
    circ_I = cir.Encoded_Gate('WAIT', [circ_I]).circuit_wrap()
    rep_meas_circ.join_circuit(circ_I, False)

    return rep_meas_circ
    


def generate_logical_state_prep_circ(logical_state='Z', n_data=9):
    '''
    '''

    state_prep_circ = cir.Circuit()

    # Prepare the data qubits in |0> or |+>
    circ_prep = cir.Circuit()
    for i in range(n_data):
        circ_prep.add_gate_at([i], 'PrepareZPlus')
    
    if logical_state == 'Z':
        first_stabs = 'X'
    elif logical_state == 'X':
        first_stabs = 'Z'
        for i in range(n_data):
            circ_prep.add_gate_at([i], 'H')

    circ_prep = cir.Encoded_Gate('Data_qubits_prep', [circ_prep]).circuit_wrap()
    state_prep_circ.join_circuit(circ_prep, False)
    

    # Now add the stabilizers
    two_stab_circ = generate_bare_meas_qdot_all_stabs_sequential
    one_stab_circ = generate_bare_meas_qdot_stabs_onekind

    # We will not insert dephasing errors during the first prep because
    # we are assuming that all the preparations (data+ancilla) occur at 
    # the same time
    gate_name = 'S1'
    stab_circ = two_stab_circ(False, first_stabs)
    stab_circ = cir.Encoded_Gate(gate_name, [stab_circ]).circuit_wrap()
    state_prep_circ.join_circuit(stab_circ, False)
        
    gate_name = 'S2'
    stab_circ = two_stab_circ(False, first_stabs)
    stab_circ = cir.Encoded_Gate(gate_name, [stab_circ]).circuit_wrap()
    state_prep_circ.join_circuit(stab_circ, False)
        
    gate_name = 'S2%s' %first_stabs
    stab_circ = one_stab_circ(False, first_stabs)
    stab_circ = cir.Encoded_Gate(gate_name, [stab_circ]).circuit_wrap()
    state_prep_circ.join_circuit(stab_circ, False)
        
    gate_name = 'S3%s' %first_stabs
    stab_circ = one_stab_circ(False, first_stabs)
    stab_circ = cir.Encoded_Gate(gate_name, [stab_circ]).circuit_wrap()
    state_prep_circ.join_circuit(stab_circ, False)
        
    return state_prep_circ



def generate_logical_state_prep_circ_minimal(logical_state='Z', n_data=9):
    '''
    Minimal version of the logical state preparation by stabilizer measurement.
    It involves measuring both X and Z stabilizers 1 time and possibly measuring
    the corresponding stabilizers (Z for |0> or X for |+>) a second time.
    This minimal construction is based on the fact that if we are trying to prepare
    |0>, then Z errors don't matter, and likewise, if we're trying to prepare |+>,
    then X errors don't matter.  

    MGA: Need to check this doesn't cause any issues if we're using the logical 
    states to do Steane EC.
    '''

    state_prep_circ = cir.Circuit()

    # Prepare the data qubits in |0> or |+>
    circ_prep = cir.Circuit()
    for i in range(n_data):
        circ_prep.add_gate_at([i], 'PrepareZPlus')
    
    if logical_state == 'Z':
        first_stabs = 'X'
    elif logical_state == 'X':
        first_stabs = 'Z'
        for i in range(n_data):
            circ_prep.add_gate_at([i], 'H')

    circ_prep = cir.Encoded_Gate('Data_qubits_prep', [circ_prep]).circuit_wrap()
    state_prep_circ.join_circuit(circ_prep, False)
    

    # Now add the stabilizers
    two_stab_circ = generate_bare_meas_qdot_all_stabs_sequential
    one_stab_circ = generate_bare_meas_qdot_stabs_onekind

    # We will not insert dephasing errors during the first prep because
    # we are assuming that all the preparations (data+ancilla) occur at 
    # the same time
    gate_name = 'S1'
    stab_circ = two_stab_circ(False, first_stabs)
    stab_circ = cir.Encoded_Gate(gate_name, [stab_circ]).circuit_wrap()
    state_prep_circ.join_circuit(stab_circ, False)
        
    gate_name = 'S2%s' %logical_state
    stab_circ = one_stab_circ(False, logical_state)
    stab_circ = cir.Encoded_Gate(gate_name, [stab_circ]).circuit_wrap()
    state_prep_circ.join_circuit(stab_circ, False)
        
    return state_prep_circ



def generate_logical_state_prep_BS(logical_state='Z', n_data=9):
    '''
    Logical state preparation for the Bacon-Shor d=3 code.
    '''

    circ_prep = cir.Circuit()
    for i in range(n_data):
        circ_prep.add_gate_at([i], 'PrepareZPlus')
        circ_prep.add_gate_at([i], 'H')

    if logical_state == 'Z':
        circ_prep.add_gate_at([0,1], 'CZ')
        circ_prep.add_gate_at([3,4], 'CZ')
        circ_prep.add_gate_at([6,7], 'CZ')
        
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            circ_prep.add_gate_at([i], 'I_gate_data')
        
        circ_prep.add_gate_at([1,2], 'CZ')
        circ_prep.add_gate_at([4,5], 'CZ')
        circ_prep.add_gate_at([7,8], 'CZ')
        
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            circ_prep.add_gate_at([i], 'I_gate_data')
        
        circ_prep.add_gate_at([1], 'H')
        circ_prep.add_gate_at([4], 'H')
        circ_prep.add_gate_at([7], 'H')
    
    elif logical_state == 'X':
        circ_prep.add_gate_at([0,3], 'CZ')
        circ_prep.add_gate_at([1,4], 'CZ')
        circ_prep.add_gate_at([2,5], 'CZ')
        
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            circ_prep.add_gate_at([i], 'I_gate_data')
        
        circ_prep.add_gate_at([3,6], 'CZ')
        circ_prep.add_gate_at([4,7], 'CZ')
        circ_prep.add_gate_at([5,8], 'CZ')
        
        # I_gate on all qubits to account for memory errors
        for i in range(n_data):
            circ_prep.add_gate_at([i], 'I_gate_data')
        
        circ_prep.add_gate_at([0], 'H')
        circ_prep.add_gate_at([6], 'H')
        circ_prep.add_gate_at([1], 'H')
        circ_prep.add_gate_at([7], 'H')
        circ_prep.add_gate_at([2], 'H')
        circ_prep.add_gate_at([8], 'H')

    return circ_prep












def run_QEC_d3(init_state, QEC_circ_list, QEC_kind):
    '''
    '''
    QEC_object = qwrap.QEC_d3(init_state, QEC_circ_list[:], chp_loc)
    #print 'init state', init_state
    #print 'state', state
    #brow.from_circuit(QEC_circ_list[0], True)
    #sys.exit(0)
    if QEC_kind == 'surface17':
        sim_output = QEC_object.run_prep_surface17_min_sequential('surface17', state)
    elif QEC_kind == 'surface17min':
        sim_output = QEC_object.run_prep_surface17_min_sequential_minimal(state)
    elif QEC_kind == 'BS17':
        sim_output = QEC_object.run_one_circ(0) 


    if QEC_kind[:9] == 'surface17':
        n_stabs, X_syns, Z_syns, Z_corr, X_corr = sim_output
        n_supra_gates = n_stabs


    
    final_stabs, final_destabs = QEC_object.stabs[:], QEC_object.destabs[:]
    
    # Determine if there is an error (both failures and correctable errors)
    final_error = False
    for stab in final_stabs:
        if stab[0] != '+':
            final_error = True
            break

    # do perfect EC
    surface17_stabs = surf17.Code.stabilizers[:]
    corr_circ = cor.Bare_Correct.generate_rep_bare_meas(9, surface17_stabs, 2, False, True,
                                                            False, False, False, True)
    corr_circ_list = []
    for supra_gate in corr_circ.gates:
        corr_circ_list += [supra_gate.circuit_list[0]]

    corr_object = qwrap.QEC_d3([final_stabs[:],final_destabs[:]], corr_circ_list[:], chp_loc) 
    # don't matter 1 and don't matter 2. The others also don't matter.
    dm1, dm2, X_stab, Z_stab, blahZ, blahX, blah_stab, blah_destab = corr_object.run_fullQEC_CSS_d3('surface17', True, False)
    corr_stabs = corr_object.stabs[:]



    # Determine if a failure has occured (for the lookup table decoder).
    fail = False
    for stab in corr_stabs:
        if stab[0] != '+':
            fail = True
            break

    
    return final_error, fail, n_supra_gates, X_syns, Z_syns, Z_corr, X_corr





#i = 0
#g = QEC_circ_list[0].gates[i]
#new_g = QEC_circ_list[0].insert_gate(g, g.qubits, '', 'X', False)
#new_g.is_error = True
#i = 2
#g = QEC_circ_list[0].gates[i]
#new_g = QEC_circ_list[0].insert_gate(g, g.qubits, '', 'X', False)
#new_g.is_error = True
#brow.from_circuit(QEC_circ_list[0], True)
#run_QEC_d3(init_state, QEC_circ_list, QEC_kind)
#sys.exit(0)

#i = -14
#g = QEC_circ_list[1].gates[i]
#new_g = QEC_circ_list[1].insert_gate(g, g.qubits, '', 'X', False)
#new_g.is_error = True
#brow.from_circuit(QEC_circ_list[1], True)
#run_QEC_d3(init_state, QEC_circ_list, QEC_kind)
#sys.exit(0)



#errors_dict, carry_run, faulty_circs = wrapper.add_errors_fast_sampler_ion(list_faulty_gates, 
#                                                                           n_errors, 
#                                                                           QEC_circ_list, 
#                                                                           error_info)
#brow.from_circuit(faulty_circs[0], True)
#time.sleep(5)
#brow.from_circuit(faulty_circs[1], True)
#time.sleep(5)
#brow.from_circuit(faulty_circs[2], True)
#time.sleep(5)
#brow.from_circuit(faulty_circs[3], True)
#time.sleep(5)
#print errors_dict, carry_run
#sys.exit(0)



def run_QEC_d3_BS(init_state, QEC_circ_list, init_state_Pauli):
    '''
    '''
    QEC_object = qwrap.QEC_d3(init_state, QEC_circ_list[:], chp_loc)
    sim_output = QEC_object.run_one_circ(0)

    final_stabs, final_destabs = QEC_object.stabs[:], QEC_object.destabs[:]
    
    # Determine if there is an error (both failures and correctable errors)
    final_error = False
    for stab in final_stabs:
        if stab[0] != '+':
            final_error = True
            break
 

    # do perfect EC
    code_stabs = BS17.Code.stabilizers[:]

    #corr_circ = cor.Bare_Correct.generate_rep_bare_meas(9, surface17_stabs, 2, False, True,
    #                                                    False, False, False, True)
    corr_circ = cor.Bare_Correct.generate_rep_bare_meas(9, code_stabs, 1, False, False,
                                                        False, False, False, True)
    corr_circ_list = []
    for supra_gate in corr_circ.gates:
        corr_circ_list += [supra_gate.circuit_list[0]]

    corr_object = qwrap.QEC_d3([final_stabs[:],final_destabs[:]], corr_circ_list[:], chp_loc) 
    # don't matter 1 and don't matter 2. The others also don't matter.
    #dm1, dm2, X_stab, Z_stab, blahZ, blahX, blah_stab, blah_destab = corr_object.run_fullQEC_CSS_d3('surface17', True, False)
    dm1, dm2, X_stab, Z_stab, blahZ, blahX, blah_stab, blah_destab = corr_object.run_fullQEC_CSS_perfect(QEC_kind)
    corr_stabs = corr_object.stabs[:]
    corr_destabs = corr_object.destabs[:]
    


    log_oper = BS17.Code.logical_opers[init_state_Pauli]
    log_meas_circ = cor.Bare_Correct.generate_bare_meas(9, [log_oper], False, False)
    log_meas_object = qwrap.Quantum_Operation([corr_stabs[:],corr_destabs[:]], 
                                                  [log_meas_circ], chp_loc)
    final_dict = log_meas_object.run_one_circ(0)
    log_outcome, log_random = final_dict.values()[0][0], final_dict.values()[0][1]

    fail = False
    if log_outcome == 1:  fail = True


    return final_error, fail, log_random



def run_several_QEC_fast(error_info, n_runs_total, init_state, QEC_kind, QEC_circ_list,
                         init_state_Pauli):
    '''
    '''

    did_run = 0
    n_final_errors = 0
    n_fails = 0
    n_fails_NN = 0
    n_supra_gates = 0
    errors_added = []
    X_stab_outcomes, Z_stab_outcomes = [], []
    Z_corrections, X_corrections = [], []
    final_errors, failings, failings_NN = [], [], []

    for n_run in xrange(n_runs_total):

        if QEC_kind[:9] == 'surface17':
            
            #fraction_of_circ = 4
            
            QEC_circ_list_copy = []
            for subcirc in QEC_circ_list:
                QEC_circ_list_copy += [copy.deepcopy(subcirc)]


            # Add the errors and decide to run
            errors_dict, carry_run, faulty_circs = wrapper.add_errors_fast_sampler_ion(
                                                        list_faulty_gates,
                                                        n_errors,
                                                        QEC_circ_list_copy,
                                                        error_info)

            
            # MGA 12/23/19: just for now in order to test NN decoder.
            carry_run = True
            #errors_added += [err_add_circ]
        



        # Run
        if carry_run:
            did_run += 1
            final_error, fail, n_supra_local, X_out, Z_out, Z_correct, X_correct = run_QEC_d3(
                                                                                     init_state, 
                                                                                     faulty_circs,
                                                                                     QEC_kind)
            X_stab_outcomes += [X_out]
            Z_stab_outcomes += [Z_out]
            Z_corrections += [Z_correct]
            X_corrections += [X_correct]
            n_supra_gates += n_supra_local
            final_errors += [final_error]
            failings += [fail]
            if final_error:
                n_final_errors += 1
            
            #print did_run
            #print 'init state', init_state

            if fail:  
                n_fails += 1
                #print errors_dict
                #for key in errors_dict:
                #    if errors_dict[key] != {}:
                #        brow.from_circuit(faulty_circs[key], True)
                #for 

                #break



    return n_final_errors, n_fails, n_supra_gates, errors_added, X_stab_outcomes, Z_stab_outcomes, Z_corrections, X_corrections, final_errors, failings


#run_several_QEC_fast(error_info, 100, init_state, QEC_kind, QEC_circ_list)
#sys.exit(0)


def run_several_QEC_fast_BS(error_info, n_runs_total, init_state, QEC_kind, QEC_circ_list,
                            init_state_Pauli):
    '''
    '''

    did_run = 0
    n_final_errors = 0
    n_fails = 0
    n_log_random = 0
    X_stab_outcomes, Z_stab_outcomes = [], []
    Z_corrections, X_corrections = [], []
    final_errors, failings, failings_NN, log_randoms = [], [], [], []

    for n_run in xrange(n_runs_total):

        QEC_circ_list_copy = []
        for subcirc in QEC_circ_list:
            QEC_circ_list_copy += [copy.deepcopy(subcirc)]


        # Add the errors and decide to run
        errors_dict, carry_run, faulty_circs = wrapper.add_errors_fast_sampler_ion(
                                                       list_faulty_gates,
                                                       n_errors,
                                                       QEC_circ_list_copy,
                                                       error_info)

            
        # MGA 12/23/19: just for now in order to test NN decoder.
        carry_run = True
        #errors_added += [err_add_circ]
        

        # Run
        if carry_run:
            did_run += 1
            final_error, fail, log_random = run_QEC_d3_BS(init_state, faulty_circs, 
                                                            init_state_Pauli)
            final_errors += [final_error]
            failings += [fail]
            log_randoms += [log_random]
            if final_error:
                n_final_errors += 1            
            if fail:  
                n_fails += 1
            if log_random:
                n_log_random += 1

    return n_final_errors, n_fails, n_log_random, final_errors, failings, log_randoms



#run_several_QEC_fast_BS(error_info, 100, init_state, QEC_kind, QEC_circ_list, state)
#sys.exit(0)



def run_parallel_QEC(error_info, n_runs_per_proc, n_proc, init_state, QEC_kind, QEC_circ_list,
                     init_state_Pauli):
    '''
    '''
    if QEC_kind[:9] == 'surface17':
        sim_func = run_several_QEC_fast
    elif QEC_kind == 'BS17':
        sim_func = run_several_QEC_fast_BS
    pool = mp.Pool()
    results = [pool.apply_async(sim_func, (error_info, n_runs_per_proc, 
                                           init_state, QEC_kind, QEC_circ_list[:],
                                           init_state_Pauli))
                    for proc in range(n_proc)]
    pool.close()
    pool.join()
    dicts = [r.get() for r in results]

    return dicts





counting_i = 1
n_subsets = len(subset_dict)
initial_t_global = time.time()

for subset_i in subset_dict:

    initial_t_local = time.time()

    n_errors = subset_dict[subset_i]['subset']

    print 'Currently sampling subset', n_errors, '(%i of %i)'%(counting_i,n_subsets)

    if sum(n_errors) == 0:
        print 'We dont sample this one :)'
        continue

    # number of samples for the current subset
    n_samples = subset_dict[subset_i]['n_samples']
    # number of samples to be run on each processor
    n_per_proc = int(n_samples/n_proc)

    print 'Number of samples = %i'%n_samples

    # Define the circuit and the circuit_list
    if QEC_kind == 'surface17':
        surface17_stabs = surf17.Code.stabilizers[:]
        QEC_circ = generate_logical_state_prep_circ(state, 9)
    elif QEC_kind == 'surface17min':    
        surface17_stabs = surf17.Code.stabilizers[:]
        QEC_circ = generate_logical_state_prep_circ_minimal(state, 9)
    elif QEC_kind == 'BS17':
        QEC_circ = generate_logical_state_prep_BS(state, 9)


    if QEC_kind == 'BS17':
        QEC_circ_list = [QEC_circ]
    else:
        QEC_circ_list = []
        for supra_gate in QEC_circ.gates:
            QEC_circ_list += [supra_gate.circuit_list[0]]


    # Define the list of error-prone 1-q and 2-q gates
    faulty_gates_grouped = [['PrepareZPlus'], ['ImZ'], ['H'], ['CZ'], ['I_prep'], 
                            ['I_gate_data'], ['I_gate_anc'], ['I_meas']]
    list_faulty_gates = list(wrapper.gates_list_general(QEC_circ_list, faulty_gates_grouped))


    #for gate in list_faulty_gates:
    #    print len(gate)
    #sys.exit(0)


    # Define the number of all the 2-q gates, 1-q gates, and measurements
    # for resource counting purposes
    n_2q_gates, n_1q_gates, n_meas = [], [], []
    for subcirc in QEC_circ_list:
        two_q, one_q, meas = 0, 0, 0
        for phys_gate in subcirc.gates:
            if len(phys_gate.qubits) > 1:
                two_q += 1
            else:
                if phys_gate.gate_name[0] != 'I':
                    one_q += 1
                if phys_gate.gate_name[:4] == 'Meas':
                    meas += 1
        n_2q_gates += [two_q]
        n_1q_gates += [one_q]
        n_meas += [meas]


    # Run the circuit
    out_list = run_parallel_QEC(error_info, n_per_proc, n_proc, init_state, 
                                QEC_kind, QEC_circ_list, state)

    # compile the results
    n_total = n_per_proc*n_proc

    n_final_errors = sum([event[0] for event in out_list])
    n_fail = sum([event[1] for event in out_list])
    if QEC_kind[:9] == 'surface17':
        n_supra_gates = sum([event[2] for event in out_list])
    elif QEC_kind == 'BS17':
        n_log_random= sum([event[2] for event in out_list])

    n_correctable = n_final_errors - n_fail
    p_correctable = float(n_correctable)/float(n_total)
    p_fail = float(n_fail)/float(n_total)
    if QEC_kind[:9] == 'surface17':
        p_supra_gates = float(n_supra_gates)/float(n_total)
        out_dict = {'n_total': n_total, 
                    'n_correctable': n_correctable,
                    'p_correctable': p_correctable,
                    'n_fail': n_fail, 
                    'p_fail': p_fail,
                    'n_supra_gates': n_supra_gates,
                    'p_supra_gates': p_supra_gates
                    }
    elif QEC_kind == 'BS17':
        p_log_random = float(n_log_random)/float(n_total)
        out_dict = {'n_total': n_total, 
                    'n_correctable': n_correctable,
                    'p_correctable': p_correctable,
                    'n_fail': n_fail, 
                    'p_fail': p_fail,
                    'n_log_random': n_log_random,
                    'p_log_random': p_log_random
                    }
    #print out_dict
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    json_filename = '_'.join(map(str,n_errors)) + '.json'
    abs_filename = output_folder + json_filename
    json_file = open(abs_filename, 'w')
    json.dump(out_dict, json_file, indent=4, separators=(',', ':'), sort_keys=True)
    json_file.close()

    final_t = time.time()
    subset_duration = (final_t - initial_t_local)/60.
    total_duration = (final_t - initial_t_global)/60.
    print 'This subset took %f min'%subset_duration
    print 'Total duration so far = %f min'%total_duration

    counting_i += 1



