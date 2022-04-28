import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from pytrackunit.trackunit import TrackUnit
import json
import asyncio

async def get_errors_data(settings,_type):
    tu = TrackUnit()

    veh_list = await tu.async_get_unitlist(_type=" "+str(_type))
    print("Got {} Vehicles".format(len(veh_list)))

    if len(veh_list) == 0:
        return None, None

    input_list = [veh_list[i]['id'] for i in range(len(veh_list))]

    spn_fmi_cnt = {}
    id_spn_fmi_cnt = {}
    data = []

    async for x,id in tu.get_multi_faults( input_list, 30 ):
        assert 'id' not in x or (x['id'] == id)
        x['id'] = id
        data.append(x)
        key_1 = (x["spn"],x["fmi"])
        key_2 = (id,x["spn"],x["fmi"])
        if key_1 in spn_fmi_cnt:
            spn_fmi_cnt[key_1] += 1
        else:
            spn_fmi_cnt[key_1] = 1
        if key_2 in id_spn_fmi_cnt:
            id_spn_fmi_cnt[key_2] += 1
        else:
            id_spn_fmi_cnt[key_2] = 1 

    fmi_spn_cnt_keys_sorted = list(spn_fmi_cnt)
    fmi_spn_cnt_keys_sorted.sort(key=lambda k:spn_fmi_cnt[k],reverse=True)

    top_keys = fmi_spn_cnt_keys_sorted[0:5]

    filtered_data = list(filter(lambda l: next(filter(lambda tk: tk[0] == l['spn'] and tk[1] == l['fmi'],top_keys),None) is not None,data))

    dataset = pd.DataFrame(data={
        #'id': list(map(lambda x: str(x['id']),filtered_data)),
        'spnfmi': list(map(lambda x: f"{x['spn']}-{x['fmi']}",filtered_data)),
        'oc': list(map(lambda x: int(spn_fmi_cnt[(x['spn'],x['fmi'])]),filtered_data)),
        'desc': list(map(lambda x: x['description'],filtered_data))})

    order = list(map(lambda x: f"{x[0]}-{x[1]}",top_keys))

    return dataset, order

def do_plot(dataset,order,_type,as_file=False):
    sns.set_theme(style="ticks")
    f, ax = plt.subplots(figsize=(9,4))
    sns.boxplot(x="oc",y="spnfmi", data=dataset, order=order)
    if as_file:
        f.savefig(f"errors_{_type}.png")
    else:
        plt.show()

async def get_errors_img(_type,as_file=False):
    settings = json.load(open("config.json"))
    dataset,order = await get_errors_data(settings,_type)
    print(dataset)
    if dataset is None:
        return False
    do_plot(dataset,order,_type,as_file)
    return True

def profile_get_errors_img(_type):
    import yappi
    settings = json.load(open("config.json"))

    yappi.set_clock_type("WALL")
    with yappi.run():
        dataset,order = asyncio.run(get_errors_data(settings,_type))
    yappi.get_func_stats().print_all()
    
    print(dataset)
    #do_plot(dataset,order,_type)

if __name__ == "__main__":
    _type = "WNK358"
    asyncio.run(get_errors_img(_type))
    #profile_get_errors_img(_type)
    