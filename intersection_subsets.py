import json

# Input filenames
#filename1 = 'subset_dictST.json'
#filename1 = 'subset_dictSTunion.json'
#filename1 = 'subset_dictLD.json'
filename1 = 'subset_dictLDunion.json'

#filename2 = 'subset_dictST2.json'
#filename2 = 'subset_dictLD2.json'
filename2 = 'subset_dictST.json'

# Output filenames
output_filename1 = 'subset_dictSTintersection.json'
output_filename2 = 'subset_dictSTunion.json'


# folder
folder = './MC_results/QECd3_surface17/qdot1/prep/'


# Open file 1
subset_filename = folder + filename1
subset_file = open(subset_filename, 'r')
subset_dict1 = json.load(subset_file)
subset_file.close()

# Open file 2
subset_filename = folder + filename2
subset_file = open(subset_filename, 'r')
subset_dict2 = json.load(subset_file)
subset_file.close()

print len(subset_dict1)
print len(subset_dict2)


# Create a list of all the subset in dictionary 1
subsets1 = []
for subset_i in subset_dict1:
    subsets1 += [subset_dict1[subset_i]['subset']]


# Create a dictionary with all the subset in 2 not present in 1
# Also add to dictionary 1 all the elements present in dictionary 2, but not 1 (union)

# intersection is an incorrect term; it's actually not intersection
intersection_subset_dict = {}
i = 0
j = len(subsets1)
for subset_i in subset_dict2:
    if subset_dict2[subset_i]['subset'] not in subsets1:
        intersection_subset_dict[i] = subset_dict2[subset_i]
        subset_dict1[j] = subset_dict2[subset_i]
        i += 1
        j += 1

print len(intersection_subset_dict)
print len(subset_dict1)


# Save the dictionaries as json files 
subset_filename = folder + output_filename1
subset_file = open(subset_filename, 'w')
json.dump(intersection_subset_dict, subset_file, indent=4, separators=(',', ':'), sort_keys=True)
subset_file.close()

subset_filename = folder + output_filename2
subset_file = open(subset_filename, 'w')
json.dump(subset_dict1, subset_file, indent=4, separators=(',', ':'), sort_keys=True)
subset_file.close()
