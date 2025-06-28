import sys
import json
import math
import chper_wrapper as wrapper


QEC_code = sys.argv[1]
state = sys.argv[2]
process_kind = sys.argv[3] # either QEC, prep, prepmin
pmST_constant = bool(int(sys.argv[4]))  # whether or not we want pmST to be constant
plot_integration_t = bool(int(sys.argv[5]))  # whether or not we want to plot the integration t
ramping_t = float(sys.argv[6])    # the ramping time in microseconds.  This is the part of
                                  # the total measurement time that is not integration.
                                  # We will use the value of 0.4 microseconds.
ramping_t_s = ramping_t*1.e-6   # ramping time in seconds                                    


if pmST_constant:
    print "pmST constant"
else:
    print "pmST variable with tmST"

if plot_integration_t:
    print "x axis will be the integration time"
else:
    print "x axis will be the total measurement time"


error_model = 'qdot1'

if QEC_code == 'surface17':
    if process_kind == 'QEC':
        # this is for the qdot1 error model with 2 rounds of QEC
        n_gates = [16, 16, 80, 48, 9, 144, 128, 18]  
    elif process_kind == 'prep':
        # this is for the qdot1 error model logical state prep
        n_gates = [41, 24, 113, 72, 0, 216, 192, 36]  
    elif process_kind == 'prepmin':    
        # this is for the qdot1 error model minimalistic logical state prep
        n_gates = [25, 12, 85, 36, 0, 108, 96, 18]



elif QEC_code == 'BS17':
    if process_kind == 'QEC':
        # this is for the qdot1 error model with 2 rounds of QEC
        n_gates = [16, 16, 80, 48, 9, 144, 128, 18]  
    elif process_kind == 'prep':
        # this is for the qdot1 error model logical state prep
        n_gates = [9, 0, 15, 6, 0, 18, 0, 0] 
 

list_errors = []
errors_filename = './MC_results/QECd3_BS17/qdot1/prep/subset_dictLD.json'
errors_file = open(errors_filename, 'r')
errors_dict = json.load(errors_file)
errors_file.close()

for subset_i in errors_dict:
    list_errors += [errors_dict[subset_i]['subset']]


# Create the output dat file
if process_kind == 'QEC':
    summary_folder = './MC_results/QECd3_' + QEC_code + '/' + error_model + '/2/' + state + '/'
else:
    summary_folder = './MC_results/QECd3_' + QEC_code + '/' + error_model + '/' + process_kind + '/' + state + '/'


summary_filename = summary_folder + 'summary_lookupdecoder.json'
summary_file = open(summary_filename, 'r')
local_dict = json.load(summary_file)
summary_file.close()



# Error rates and durations

# state prep error rate
p_prepLD, p_prepST = 6.5e-3, 4.0e-3    # new value from Juan

# measurement error rate
p_measLD, p_measST = 2.4e-3, 4.e-4    # new value from Juan

# 1-q (H) error rate
p_1qLD, p_1qST = 4.e-4, 4.e-3    # new values from Juan

# 2-q (CZ) error rate
p_CZLD, p_CZST = 2.e-3, 4.e-3

# duration of state prep
t_prepLD, t_prepST = 0., 0.

# duration of CZ
t_CZLD, t_CZST = 4.e-8, 4.e-8    # new values from Juan

# duration of measurement
t_measLD, t_measST = 2.4e-5, 2.4e-6      # new values from Juan
ratio_meas_times = t_measLD/t_measST


# T2 times
T2_LD, T2_ST = 2.1e-5, (2.1/math.sqrt(2))*1.e-5  
# According to Juan, T2_TS is half of T2_DL in the worst case.
# In the average case, it is divided over sqrt(2).



# Inside the exponential, it should be squared because of the 
# characteristics of noise.
# dephasing during LD-LD CZ gate

p_Igate_LDLD = 0.5*(1. - math.exp(-(t_CZLD/T2_LD)**2))  
p_Igate_LDST_data = 0.5*(1. - math.exp(-(t_CZST/T2_LD)**2))  
p_Igate_LDST_anc = 0.5*(1. - math.exp(-(t_CZST/T2_ST)**2))  
p_IprepLD = 0.5*(1. - math.exp(-(t_prepLD/T2_LD)**2))
p_IprepST = 0.5*(1. - math.exp(-(t_prepST/T2_LD)**2))



def err_func_readout_Tplus(int_t):
    '''
    Function to obtain the ST readout infidelity from the integration time.
    Obtained from a polynomial fit to the Tplustotal (red) curve from RIKEN's paper
    The integration time (int_t) is assumed to be in microseconds.
    '''
    if int_t <= 1.43:
        readout_err = (0.108253 - 0.536722*int_t + 1.18519*int_t**2 - 1.45935*int_t**3 + 
                       1.03857*int_t**4 - 0.3994*int_t**5 + 0.0642018*int_t**6)
    else:
        readout_err = (1.6711e-5 + (2.98899e-4)*int_t + (4.7596e-7)*int_t**2 - 
                       (9.6605e-9)*int_t**3)

    return readout_err






# The next lines are to generate the dat file for the logical preparation error rate (BS17)
list_prets = [(i/250. - 8) for i in range(1000)]
list_ts = [10**i for i in list_prets]


output_string = 't p_prepLD p_prepST p_lowerLD p_upperLD t_lowerLD t_upperLD\n'
for t in list_ts:
    p_occurrence_total_LD, p_occurrence_total_ST = 0., 0.
    p_lower_LD = 0.
    t_lower_LD = 0.
    
    #print 'time =', t, list_ts.index(t)

    if plot_integration_t:
        total_meas_t = t + ramping_t_s
        integration_t = t
    else:
        total_meas_t = t
        integration_t = t - ramping_t_s


    if not pmST_constant:
        # We have to take into account that for the ST qubit, readout infidelity is a
        # function of readout time.
        
        p_measST = err_func_readout_Tplus(integration_t*10**6)
     

    p_ImeasLD = 0.5*(1. - math.exp(-(ratio_meas_times*total_meas_t/T2_LD)**2))


    #ps_DL = [p, p_measDL, p_IgateDL, p_ImeasDL, 0]
    #ps_TS = [p, p_measTS, p_IgateTS, p_ImeasTS, 0]


    ps_LD1 = [p_prepLD, p_measLD, p_1qLD, p_CZLD] 
    ps_LD2 = [p_IprepLD, p_Igate_LDLD, p_Igate_LDLD, p_ImeasLD]
    ps_LD = ps_LD1 + ps_LD2

    
    # Total duration of the QEC process
    # We changed this calculation to the original one because now the prep time
    # and the measurement time are independent.
    t_QEC1_LD = t_prepLD + 8*t_CZLD + ratio_meas_times*total_meas_t
    t_QEC2_LD = 8*t_CZLD + ratio_meas_times*total_meas_t
    t_QEC1_ST = t_prepST + 8*t_CZST + total_meas_t
    t_QEC2_ST = 8*t_CZST + total_meas_t


    for subset in list_errors:

        #print 'subset =', list_errors

        p_occurrence_LD = wrapper.prob_for_subset_general(n_gates, subset, ps_LD[:])
        
        p_occurrence_total_LD += p_occurrence_LD
        
        p_fail_local = local_dict[str(tuple(subset))]['p_fail']
        p_supra_gates_local = local_dict[str(tuple(subset))]['p_supra_gates']

        p_fail_LD = p_fail_local*p_occurrence_LD
        p_lower_LD += p_fail_LD

        # total time
        t_LD = t_QEC1_LD + t_QEC2_LD*(p_supra_gates_local - 1)

        t_lower_LD += (t_LD*p_occurrence_LD)



    p_upper_LD = p_lower_LD + (1.-p_occurrence_total_LD)
    
    t_upper_LD = t_QEC1_LD + t_QEC2_LD






    output_string += '%.15f 0.0065 0.004 %.15f %.15f %.15f %.15f\n' %(t, p_lower_LD, p_upper_LD, t_lower_LD, t_upper_LD) 

data_filename = summary_folder + 'resultsQECd3_Imeas' + str(int(ratio_meas_times)) + 'prep_BS17.dat'




data_file = open(data_filename, 'w')
data_file.write(output_string)
data_file.close()

