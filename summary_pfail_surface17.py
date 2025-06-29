import sys
import json



QEC_code = sys.argv[1]
state = sys.argv[2]
process_kind = sys.argv[3]  # either QEC, prep, prepmin
error_model = sys.argv[4]  # for now qdot0 or qdot1

if process_kind == 'QEC':
    json_folder = './MC_results/QECd3_' + QEC_code + '/' + error_model + '/2/' + state + '/'
else:
    json_folder = './MC_results/QECd3_' + QEC_code + '/' + error_model + '/' + process_kind + '/' + state + '/'

output_filename = 'summary_lookupdecoder.json'
output_dict = {}

list_errors = []
# For now the last error (waiting between QEC steps) is always 0


if error_model == 'qdot0':
    max_weight = int(sys.argv[5])
    
    if (QEC_code == 'BS17') and (process_kind == 'prep'): 
        for i in range(max_weight+1):
            for j in range(max_weight+1-i):
                for k in range(max_weight+1-i-j):
                    list_errors += [[i,j,k,0,0]]
    else:
        for i in range(max_weight+1):
            for j in range(max_weight+1-i):
                for k in range(max_weight+1-i-j):
                    for l in range(max_weight+1-i-j-k):
                        for m in range(max_weight+1-i-j-k-l):
                            list_errors += [[i,j,k,l,m]]


        #max_weight2 = int(sys.argv[6])
        #for i in range(max_weight2 + 1):
        #    for j in range(max_weight2 + 1-i):
        #        for k in range(max_weight2 + 1-i-j):
        #            for l in range(8,28):
        #                list_errors += [[i,j,k,l,0]]



elif error_model == 'qdot1':
    #errors_filename = './MC_results/QECd3_surface17/qdot1/2/subset_dictST.json'
    #errors_filename = './MC_results/QECd3_surface17/qdot1/2/subset_dictSTunion.json'
    #errors_filename = './MC_results/QECd3_surface17/qdot1/2/subset_dictLDunion.json'
    #errors_filename = './MC_results/QECd3_surface17/qdot1/prep/subset_dictLDunion.json'
    errors_filename = './MC_results/QECd3_BS17/qdot1/prep/subset_dictLD.json'
    errors_file = open(errors_filename, 'r')
    errors_dict = json.load(errors_file)
    errors_file.close()

    i = 0
    for subset_i in errors_dict:
        list_errors += [errors_dict[subset_i]['subset']]
        i += 1
    
    print i



n_total = 0
for error_subset in list_errors:
    #print error_subset

    if sum(error_subset) == 0: 
        p_fail = 0.
        p_log_random = 0.
        p_supra_gates = 0.
    else: 
        error_string = '_'.join(map(str,error_subset))
        json_filename = json_folder + error_string + '.json'
        json_file = open(json_filename, 'r')
        local_dict = json.load(json_file)
        json_file.close()
        p_fail = local_dict['p_fail']
        try:
            p_log_random = local_dict['p_log_random']
        except(KeyError):
            p_log_random = 0.
        
        try:
            p_supra_gates = local_dict['p_supra_gates']
        except(KeyError):
            p_supra_gates = 1.


    if p_log_random > 0.0:
        print error_subset, p_log_random
    mini_output_dict = {'p_fail': p_fail, 
                        'p_log_random': p_log_random,
                        'p_supra_gates': p_supra_gates}
    output_dict[str(tuple(error_subset))] = mini_output_dict
    #output_dict[str(tuple(error_subset))] = p_fail
    #print(p_fail)

    n_total += 1

output_json_file = open(json_folder+output_filename, 'w')
json.dump(output_dict, output_json_file)
output_json_file.close()
#print n_total



