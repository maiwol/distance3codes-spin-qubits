import sys
import os
import time
import json
import copy
import math as m
import random as rd
import multiprocessing as mp
import circuit as cir
#import steane
import surface17 as surf17
import BS17
import correction as cor
import chper_wrapper as wrapper
import MC_functions as mc
import qcircuit_functions as qfun
import qcircuit_wrapper as qwrap
#from visualizer import browser_vis as brow



def generate_wait_circ(n_data):
    '''
    '''

    circ_I = cir.Circuit()
    for i in range(n_data):
        circ_I.add_gate_at([i], 'I_idle')

    return circ_I



def generate_bare_meas_qdot_all_stabs_sequential(idle_prep):
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
    for i in range(n_data, n_data+n_ancilla):
        bare_meas_circ.add_gate_at([i], 'PrepareZPlus')
        bare_meas_circ.add_gate_at([i], 'H')  # later change this for Y rotation
        


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
    



# Define the circuit and the circuit list
QEC_circ = generate_rep_bare_meas_qdot(9, 2, False, True)
QEC_circ_list = []
for supra_gate in QEC_circ.gates:
    QEC_circ_list += [supra_gate.circuit_list[0]]
        
        
# Define the list of error-prone 1-q and 2-q gates
# For now we won't add H into our list of faulty gates
faulty_gates_grouped = [['PrepareZPlus'], ['ImZ'], ['H'], ['CZ'], ['I_prep'], 
                        ['I_gate_data'], ['I_gate_anc'], ['I_meas']]
list_faulty_gates = list(wrapper.gates_list_general(QEC_circ_list, faulty_gates_grouped))
n_gates = []
for gate in list_faulty_gates:
    n_gates += [len(gate)]


# Error rates and durations
	
# state prep error rate
p_prepLD, p_prepST = 3.e-2, 1.5e-2
# measurement error rate
p_measLD, p_measST = 3.e-2, 1.9e-3
# 1-q (H) error rate
p_1qLD, p_1qST = 4.e-4, 4.e-4
# 2-1 (CZ) error rate
p_CZLD, p_CZST = 1.e-3, 1.e-3

# duration of state prep
#t_prepLD, t_prepST = 2.e-4, 2.e-5
t_prepLD, t_prepST = 0., 0.
# duration of CZ
t_CZLD, t_CZST = 5.e-8, 5.e-8
# duration of measurement
t_measLD, t_measST = 1.e-6, 3.e-5

# T2 times
T2_LD, T2_ST = 2.1e-5, 1.05e-5

# dephasing associated with waiting times
# waiting during state prep on ancillae
p_IprepLD, p_IprepST = 0.5*(1. - m.exp(-(t_prepLD/T2_LD)**2)), 0.5*(1. - m.exp(-(t_prepST/T2_ST)**2))
# waiting during CZ
p_Igate_LDLD = 0.5*(1. - m.exp(-(t_CZLD/T2_LD)**2))
p_Igate_LDST_data = 0.5*(1. - m.exp(-(t_CZST/T2_LD)**2))
p_Igate_LDST_anc = 0.5*(1. - m.exp(-(t_CZST/T2_ST)**2))
# waiting during measurement on ancillae
p_ImeasLD = 0.5*(1. - m.exp(-(t_measLD/T2_LD)**2))
p_ImeasST = 0.5*(1. - m.exp(-(t_measST/T2_LD)**2))


ps_LD = [p_prepLD, p_measLD, p_1qLD, p_CZLD, p_IprepLD, p_Igate_LDLD, p_Igate_LDLD, p_ImeasLD]
ps_ST = [p_prepST, p_measST, p_1qST, p_CZST, p_IprepST, p_Igate_LDST_data, p_Igate_LDST_anc, p_ImeasST]



mx = 25
cutoff_p = 1.e-6
n_subsets = 0
n_total = 0


def subset_cardinality(n_gates_list, n_errors_list):
    '''
    calculates the number of elements in a given error subset
    '''
    subset_c = 1.

    for i in range(len(n_gates_list)):
        subset_c *= wrapper.combinatorial_factor(n_gates_list[i], n_errors_list[i])

    return subset_c




t_per_run = 5./84000.
total_t_first = 0


total_subset_dict = {}



mx_first = 3
n_total_first = 0

counting_i = 0
for x1 in range(mx_first+1):
    for x2 in range(mx_first+1-x1):
        for x3 in range(mx_first+1-x1-x2):
            for x4 in range(mx_first+1-x1-x2-x3):
                for x5 in range(mx_first+1-x1-x2-x3-x4):
                    for x6 in range(mx_first+1-x1-x2-x3-x4-x5):
                        for x7 in range(mx_first+1-x1-x2-x3-x4-x5-x6):
                            for x8 in range(mx_first+1-x1-x2-x3-x4-x5-x6-x7):
                                subset = [x1,x2,x3,x4,x5,x6,x7,x8]
                                n_total_first += 1
                                p_occurrence = wrapper.prob_for_subset_general(n_gates, subset, ps_LD)
                                
                                subset_c = subset_cardinality(n_gates, subset)
                                
                                if subset_c <= 10000:
                                    total_t_first += t_per_run*10000
                                    n_samples = 10000
                                    print subset, p_occurrence, subset_c, t_per_run*10000
                                elif subset_c <= 200000.:
                                    total_t_first += t_per_run*subset_c
                                    n_samples = subset_cardinality(n_gates, subset)
                                    print subset, p_occurrence, subset_c, t_per_run*subset_c
                                else:
                                    total_t_first += t_per_run*84000
                                    n_samples = 84000
                                    print subset, p_occurrence, subset_c, t_per_run*84000


                                #subset_tuple = tuple(subset)
                                local_dict = {'subset': subset,
                                              'p_occurrence': p_occurrence,
                                              'cardinality': subset_c,
                                              'n_samples': n_samples,
                                              'fraction_sampled': float(n_samples)/float(subset_c)
                                             }
                                
                                total_subset_dict[counting_i] = local_dict
                                counting_i += 1


print n_total_first, total_t_first


total_t_second = 0

for x1 in range(mx+1):
    for x2 in range(mx+1-x1):
        for x3 in range(mx+1-x1-x2):
            for x4 in range(mx+1-x1-x2-x3):
                for x5 in range(mx+1-x1-x2-x3-x4):
                    for x6 in range(mx+1-x1-x2-x3-x4-x5):
                        for x7 in range(mx+1-x1-x2-x3-x4-x5-x6):
                            for x8 in range(mx+1-x1-x2-x3-x4-x5-x6-x7):
                                subset = [x1,x2,x3,x4,x5,x6,x7,x8]
                                p_occurrence = wrapper.prob_for_subset_general(n_gates, subset, ps_LD)
                                n_total += 1

                                #if tuple(subset) in total_subset_dict.keys():
                                #    continue

                                if p_occurrence > cutoff_p:
                                    n_subsets += 1

                                    # calculate the cardinality of the subset
                                    subset_c = subset_cardinality(n_gates, subset) 
                                    
                                    if subset_c <= 10000:
                                        n_samples = 10000
                                        total_t_second += t_per_run*10000
                                    elif subset_c <= 200000.:
                                        n_samples = subset_cardinality(n_gates, subset)
                                        total_t_second += t_per_run*subset_c
                                        print subset, p_occurrence, subset_c, t_per_run*subset_c
                                    else:
                                        n_samples = 84000
                                        total_t_second += t_per_run*84000
                                        print subset, p_occurrence, subset_c, t_per_run*84000

                                    #subset_tuple = tuple(subset)
                                    local_dict = {'subset': subset,
                                                  'p_occurrence': p_occurrence,
                                                  'cardinality': subset_c,
                                                  'n_samples': n_samples,
                                                  'fraction_sampled': float(n_samples)/float(subset_c)
                                                }
                                
                                    total_subset_dict[counting_i] = local_dict
                                    counting_i += 1


output_folder = './MC_results/QECd3_surface17/qdot1/2/'


if not os.path.exists(output_folder):
    os.makedirs(output_folder)


json_filename = 'subset_dictLD2.json'
abs_filename = output_folder + json_filename
json_file = open(abs_filename, 'w')
json.dump(total_subset_dict, json_file, indent=4, separators=(',', ':'), sort_keys=True)
json_file.close()

print n_subsets, n_total, total_t_second
total_t = total_t_first + total_t_second
print total_t, 'minutes'
print total_t/60., 'hours'


