#  First run the following command on your c-lightning node:
#  lncli listforwards > forwards.json

from collections import Counter
import json

FORWARDS_FILE = "forwards.json"

# TODO: parse that dict from c-lightning's output as well 
scid_to_alias_dict = {
    "713363x185x0"   : "example_node_alias",
}

def scid_to_alias(scid):
    if scid not in scid_to_alias_dict:
        return scid
    else:
        return scid_to_alias_dict[scid]

def sum_msats_to_Msats(msats_list):
    return sum(msats_list) / 1000000000.0

def sum_msats_to_sats(msats_list):
    return sum(msats_list) / 1000.0

def create_stats_json(forwards, output = f"forward_stats.json"):

    stats = {}

    for forward_status in ['settled', 'failed']:

        filtered_by_status = [i for i in forwards if i['status']== forward_status]
        
        inner_stats = {}
        inner_stats['count'] = len(filtered_by_status)
        inner_stats['total_Msat'] = sum_msats_to_Msats([i['out_msatoshi'] for i in filtered_by_status])
        inner_stats['total_fees_Msat'] = sum_msats_to_Msats([i['fee'] for i in filtered_by_status])
        
        in_count = Counter([i['in_channel'] for i in filtered_by_status])
        out_count = Counter([i['out_channel'] for i in filtered_by_status])
        in_out_count = Counter([(i['in_channel'], i['out_channel']) for i in filtered_by_status])

        in_amount = {j : sum_msats_to_Msats([i['in_msatoshi'] for i in filtered_by_status if i['in_channel'] == j]) for j in in_count}
        out_amount = {j : sum_msats_to_Msats([i['out_msatoshi'] for i in filtered_by_status if i['out_channel'] == j]) for j in out_count}
        in_out_amount = {(j_in, j_out) : sum_msats_to_Msats([i['out_msatoshi'] for i in filtered_by_status if i['in_channel'] == j_in and i['out_channel'] == j_out]) for j_in, j_out in in_out_count}

        inner_stats['{}_from'.format(forward_status)] = {scid_to_alias(j) : {'count' : in_count[j], 'total_Msats' : in_amount[j]} for j, _ in in_count.most_common()}
        inner_stats['{}_to'.format(forward_status)] = {scid_to_alias(j) : {'count' : out_count[j], 'total_Msats' : out_amount[j]} for j, _ in out_count.most_common()}
        inner_stats['{}_from_to'.format(forward_status)] = {str((scid_to_alias(j[0]), scid_to_alias(j[1]))) : {'count' : in_out_count[j], 'total_Msats' : in_out_amount[j]} for j, _ in in_out_count.most_common()}
        stats[forward_status] = inner_stats


    with open(output, 'w') as f:
        print("[*] Output saved to file {}".format(output))
        json.dump(stats, f, indent=4)


if __name__ == "__main__":
    with open(FORWARDS_FILE, 'r') as f:
        data = json.load(f)
        create_stats_json(data['forwards'])


