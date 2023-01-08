import subprocess
import sys
import json


with open('dataset.json') as file:
    dataset = json.load(file)

"""
dataset = {
        '2018':
            {
                'string' : '*20UL18NanoAODv9*',
                'samples': {
                    'zjj': {
                        'query': 'EWK_LLJJ*dipole*'
                        }
                    }
                }
            }
"""

def exit():
    print('Now exiting')
#    print(json.dumps(dataset, indent=4))
    with open('dataset.json', 'w') as file:
        json.dump(dataset, file, indent=4)
    sys.exit()

for year in dataset.keys():
    for sample in dataset[year]['samples'].keys():
        yearString = dataset[year]['samples'][sample].get('queryYear', dataset[year]['string'])
        sampleString = dataset[year]['samples'][sample]['query']
        if len(dataset[year]['samples'][sample].get('files', [])) != 0:
            continue
        print(f'Searching {sample} for year {year} with dataset=/{sampleString}/{yearString}/NANOAODSIM')
        procString = f'dasgoclient --query="dataset=/{sampleString}/{yearString}/NANOAODSIM"'
        proc = subprocess.Popen(procString, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        err = err.decode('utf-8')
        if len(err) != 0:
            print('There were some errors:')
            print(err)
            exit()
        out = out.decode('utf-8')
        out = out.split('\n')
        out = list(filter(lambda k: k.strip() != '', out))
        if len(out) == 1:
            # search files for the sample
            process = out[0]
            print(f'Searching files for {sample} for year {year} with "file dataset={process}"')
            procString = f'dasgoclient --query="file dataset={process}"'
            proc = subprocess.Popen(procString, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out1, err1 = proc.communicate()
            out1 = out1.decode('utf-8')
            out1 = out1.split('\n')
            out1 = list(filter(lambda k: k.strip() != '', out1))
            print(out1, len(out1))
            err1 = err1.decode('utf-8')
            if len(err1) != 0:
                print('There were some errors:')
                print(err1)
                exit()
            dataset[year]['samples'][sample]['files'] = out1

            

        else:
            print(f'Sample {sample} does not uniquely define a sample, please choose from the followings and update the query')
            print('\n'.join(out))
            exit()

exit()
