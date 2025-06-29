import BS17
import surface17 as surf17
import correction as corr
import qcircuit_wrapper as qwrap
#from visualizer import browser_vis as brow


chp_loc = './chp_extended'

#surface17_stabs = surf17.Code.stabilizers[:]
#corr_circ = corr.Bare_Correct.generate_rep_bare_meas(9, surface17_stabs, 1, False, False, 
#                                                     False, False, False, True)

#brow.from_circuit(corr_circ, True)


init_state_Pauli = 'Z'
log_oper = BS17.Code.logical_opers[init_state_Pauli]
log_circ = corr.Bare_Correct.generate_bare_meas(9, [log_oper], False, False)

#brow.from_circuit(log_circ, True)

stabs = ['+ZIIIIIIII','+IZIIIIIII','+IIZIIIIII','+IIIZIIIII','+IIIIZIIII',
         '+IIIIIZIII','+IIIIIIZII','+IIIIIIIZI','+IIIIIIIIZ']
destabs = ['+XIIIIIIII','+IXIIIIIII','+IIXIIIIII','+IIIXIIIII','+IIIIXIIII',
           '+IIIIIXIII','+IIIIIIXII','+IIIIIIIXI','+IIIIIIIIX']

init_stabs = surf17.Code.stabilizers_CHP[init_state_Pauli]
init_destabs = surf17.Code.destabilizers_CHP[init_state_Pauli]
log_meas_object = qwrap.Quantum_Operation([stabs[:], destabs[:]],
                                                  [log_circ], chp_loc)
final_dict = log_meas_object.run_one_circ(0)
log_outcome, log_randomness = final_dict.values()[0][0], final_dict.values()[0][1]
print log_outcome
print log_randomness
