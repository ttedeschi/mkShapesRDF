import glob


files = glob.glob('condor/new_vbf_16/*/err*')

def parseTime(t):
    m = t.index('m')
    nums = [ t[:m], t[m+1:-1]]
    #nums = t.split('m')
    nums = list(map(lambda k: float(k), nums))
    return round(nums[0]*60 + nums[1], 2)

samples = list(set(list(map(lambda k: k.split('/')[2].split('_')[0], files))))
print(samples)
L = len('condor/new_vbf_16/')
d = {}
for f in files:
    sample = list(filter(lambda k: f[L:].startswith(k), samples))[0]
    with open(f) as file:
        lines = file.read().split('\n')
        lines = list(filter(lambda k : k.startswith('real'), lines))[0]
        t = lines.split('\t')[1]
        if sample in d.keys():
            d[sample].append(parseTime(t))
        else:
            d[sample] = [parseTime(t)]
        print(sample, d[sample][-1])

print('-'*30)
for sample in d.keys():
    print(sample, round(sum(d[sample])/len(d[sample]), 2))



