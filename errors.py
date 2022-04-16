import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from pytrackunit.trackunit import TrackUnit
from pytrackunit.sqlcache import SqlCache
from datetime import datetime
import json

def get_errors_img(_type=357):

    tu = TrackUnit(verbose=False)
    with open("config.json") as f:
        output_path = json.load(f)["output-location"]
    #tu.cache.tdelta_end = datetime(2022,2,21,10,0,0,0)
    veh_list = tu.get_unitlist(_type=" "+str(_type))
    #self.veh_list += tu.get_unitlist(_type=" 349")
    print("Got {} Vehicles".format(len(veh_list)))

    # Use sqlcache for this
    tu.cache = SqlCache(auth=('API',open('api.key').read()))

    input_list = [veh_list[i]['id'] for i in range(len(veh_list))]

    def process_slice( data, meta):
        if data is None:
            return []
        _slice_dict = {}
        for d in data:
            _day = d['time'].split('T')[0]
            _spn_fmi = (d['spn'],d['fmi'])
            if _day in _slice_dict:
                if not (_spn_fmi in _slice_dict[_day]):
                    _slice_dict[_day].append(_spn_fmi)
            else:
                _slice_dict[_day] = [_spn_fmi]
        _data = []
        for d in _slice_dict:
            for s in _slice_dict[d]:
                _data.append((meta['id'],d,str(s[0]),str(s[1])))
        return _data

    _data = list((tu.get_multi_faults( input_list, 30, process_slice)))

    lines = _data

    data = {}

    fmi_spn_cnt = {}

    for l in lines:
        fmi_spn_cnt[(l[2],l[3])] = 0
        data[(l[0],l[2],l[3])] = 0

    for l in lines:
        fmi_spn_cnt[(l[2],l[3])] += 1
        data[(l[0],l[2],l[3])] += 1


    fmi_spn_cnt_keys_sorted = list(fmi_spn_cnt)
    fmi_spn_cnt_keys_sorted.sort(key=lambda k:fmi_spn_cnt[k],reverse=True)

    top_keys = fmi_spn_cnt_keys_sorted[0:10]

    #print(top_keys)

    filtered_data = list(filter(lambda l: next(filter(lambda tk: tk[0] == l[2] and tk[1] == l[3],top_keys),None) is not None,lines))

    dataset = pd.DataFrame(data={
        'id': list(map(lambda x: x[0],filtered_data)),
        'spnfmi': list(map(lambda x: f"{x[2]}-{x[3]}",filtered_data)),
        'oc': list(map(lambda x: data[(x[0],x[2],x[3])],filtered_data))})

    #print(dataset)

    sns.set_theme(style="ticks")

    f, ax = plt.subplots(figsize=(9,4))

    sns.boxplot(x="oc",y="spnfmi", data=dataset, order=list(map(lambda x: f"{x[0]}-{x[1]}",top_keys)))

    f.savefig(f"errors_{_type}.png")

if __name__ == "__main__":
    get_errors_img("WNK355")