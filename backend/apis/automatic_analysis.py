from __future__ import print_function

import timeit

import pandas as pd

from datetime import datetime, timedelta
from flask_restplus import Namespace
from pymongo import MongoClient

api = Namespace('analyze', description='analyze')

uri = "mongodb://localhost:27017/gcm_gisaid"
client = MongoClient(uri)
db = client.gcm_gisaid

collection_db = db.seq_2021_08_26_2
collection_update_date = db.db_meta


world_growth_obj = {}


def world_growth(today_date, location_granularity):
    last_week_date = today_date.replace(day=today_date.day) - timedelta(days=7)
    previous_week_date = last_week_date.replace(day=last_week_date.day) - timedelta(days=7)
    query = {
        'c_coll_date_prec': {
            '$eq': 2
        },
    }
    query_this_week = query.copy()
    query_prev_week = query.copy()
    query_this_week['collection_date'] = {'$lt': today_date, '$gte': last_week_date}
    query_prev_week['collection_date'] = {'$lt': last_week_date, '$gte': previous_week_date}
    results_this_week = collection_db.count_documents(query_this_week)
    results_prev_week = collection_db.count_documents(query_prev_week)

    world_growth_obj['world_growth'] = {f'{location_granularity[0]}': None,
                                        f'{location_granularity[1]}': None,
                                        f'{location_granularity[2]}': None,
                                        'lineage': None,
                                        'mut': None,
                                        'total_seq_world_prev_week': results_prev_week,
                                        'total_seq_world_this_week': results_this_week,
                                        'total_seq_pop_prev_week': results_prev_week,
                                        'total_seq_pop_this_week': results_this_week,
                                        'count_prev_week': results_prev_week,
                                        'count_this_week': results_this_week,
                                        'perc_prev_week': None,
                                        'perc_this_week': None,
                                        'diff_perc': None,
                                        'date': today_date.strftime("%Y-%m-%d"),
                                        'granularity': location_granularity[0]
                                        }


count_all_sequences_for_geo = {'total': 0}


def lineage_growth(today_date, location_granularity, location_0, location_1, location_2, lineage):
    last_week_date = today_date.replace(day=today_date.day) - timedelta(days=7)
    previous_week_date = last_week_date.replace(day=last_week_date.day) - timedelta(days=7)
    query = {
        'c_coll_date_prec': {
            '$eq': 2
        },
        f'location.{location_granularity[0]}': {
            '$eq': location_0
        },
        f'location.{location_granularity[1]}': {
            '$eq': location_1
        },
        f'location.{location_granularity[2]}': {
            '$eq': location_2
        },
        'covv_lineage': {
            '$eq': lineage
        },
    }
    query_this_week = query.copy()
    query_prev_week = query.copy()
    query_this_week['collection_date'] = {'$lt': today_date, '$gte': last_week_date}
    query_prev_week['collection_date'] = {'$lt': last_week_date, '$gte': previous_week_date}
    results_this_week = collection_db.count_documents(query_this_week)
    results_prev_week = collection_db.count_documents(query_prev_week)

    denominator_world_prev_week = world_growth_obj['world_growth']['count_prev_week']
    denominator_world_this_week = world_growth_obj['world_growth']['count_this_week']

    result = {f'{location_granularity[0]}': location_0,
              f'{location_granularity[1]}': location_1,
              f'{location_granularity[2]}': location_2,
              'lineage': lineage,
              'mut': None,
              'total_seq_world_prev_week': denominator_world_prev_week,
              'total_seq_world_this_week': denominator_world_this_week,
              'total_seq_pop_prev_week': results_prev_week,
              'total_seq_pop_this_week': results_this_week,
              'count_prev_week': results_prev_week,
              'count_this_week': results_this_week,
              'perc_prev_week': None,
              'perc_this_week': None,
              'diff_perc': None,
              'date': today_date.strftime("%Y-%m-%d"),
              'granularity': location_granularity[2]
              }

    # count_all_sequences_for_geo['total'] = count_all_sequences_for_geo['total'] + results_this_week
    # if location_0 not in count_all_sequences_for_geo:
    #     count_all_sequences_for_geo[location_0] = results_this_week
    # else:
    #     count_all_sequences_for_geo[location_0] = count_all_sequences_for_geo[location_0] + results_this_week
    # print("count", count_all_sequences_for_geo)

    return result


def get_all_mutation_not_characteristics(lineage, location_0, location_1, location_2, today_date, location_granularity):
    all_mutation_not_characteristics_dict = {}

    last_week_date = today_date.replace(day=today_date.day) - timedelta(days=7)
    previous_week_date = last_week_date.replace(day=last_week_date.day) - timedelta(days=7)

    pipeline = [
        {"$match": {
            'c_coll_date_prec': {
                '$eq': 2
            },
            'collection_date': {
                '$lt': today_date,
                '$gt': previous_week_date
            },
            f'location.{location_granularity[0]}': {
                '$eq': location_0
            },
            f'location.{location_granularity[1]}': {
                '$eq': location_1
            },
            f'location.{location_granularity[2]}': {
                '$eq': location_2
            },
        }},
        {"$group": {"_id": '$covv_lineage', "count": {"$sum": 1}}},
    ]

    lin_info = {x['_id']: (x['count'], []) for x in collection_db.aggregate(pipeline, allowDiskUse=True)}

    pipeline = [
        {"$match": {
            'c_coll_date_prec': {
                '$eq': 2
            },
            'collection_date': {
                '$lt': today_date,
                '$gt': previous_week_date
            },
            f'location.{location_granularity[0]}': {
                '$eq': location_0
            },
            f'location.{location_granularity[1]}': {
                '$eq': location_1
            },
            f'location.{location_granularity[2]}': {
                '$eq': location_2
            },
            'covv_lineage': {
                '$eq': lineage
            },
        }},
        {"$unwind": "$muts"},
        {"$group": {"_id": {'lin': '$covv_lineage',
                            'pro': "$muts.pro",
                            'org': "$muts.org",
                            'loc': "$muts.loc",
                            'alt': "$muts.alt",
                            },
                    "count": {"$sum": 1}}},
    ]

    results = collection_db.aggregate(pipeline, allowDiskUse=True)

    results = (x['_id'] for x in results if 0.75 > x['count'] / lin_info[x['_id']['lin']][0] > 0.01)

    for x in results:
        ch = f"{x['pro']}_{x['org']}{x['loc']}{x['alt']}"
        lin_info[x['lin']][1].append(ch)

    lin_info = {x: [c, sorted(arr)] for x, (c, arr) in lin_info.items()}

    for lin in lin_info:
        all_mutation_not_characteristics_dict[lin] = lin_info[lin]

    return all_mutation_not_characteristics_dict


all_geo_last_week_dict = {}


def get_all_geo_last_week(location_granularity):
    print("inizio request geo last week")
    today_date = datetime.strptime("2021-08-08", '%Y-%m-%d')

    world_growth(today_date, location_granularity)

    last_week_date = today_date.replace(day=today_date.day) - timedelta(days=7)
    query = [
        {
            "$match": {
                'collection_date': {
                    '$lt': today_date,
                    '$gte': last_week_date
                },
                'c_coll_date_prec': {
                    '$eq': 2
                },
            },
        },
        {
            "$group": {"_id": {f''
                               f'{location_granularity[0]}': f'$location.{location_granularity[0]}',
                               f'{location_granularity[1]}': f'$location.{location_granularity[1]}',
                               f'{location_granularity[2]}': f'$location.{location_granularity[2]}',
                               },
                       "count": {"$sum": 1}
                       }
        },
        {"$sort":
            {"count": -1}
         }
    ]

    results = collection_db.aggregate(query, allowDiskUse=True)
    list_geo_dict = []
    for single_item in results:
        single_item_remodel = {f'{location_granularity[0]}': single_item['_id'][f'{location_granularity[0]}'],
                               f'{location_granularity[1]}': single_item['_id'][f'{location_granularity[1]}'],
                               f'{location_granularity[2]}': single_item['_id'][f'{location_granularity[2]}'],
                               'count': single_item['count']}
        list_geo_dict.append(single_item_remodel)
    all_geo_last_week_dict['all_geo_last_week'] = list_geo_dict
    print("fine request geo last week")
    get_all_lineage_for_each_geo(location_granularity)


all_lineage_for_geo_last_week = {}


def get_all_lineage_for_each_geo(location_granularity):
    print("inizio request all_lineages")
    today_date = datetime.strptime("2021-08-08", '%Y-%m-%d')
    last_week_date = today_date.replace(day=today_date.day) - timedelta(days=7)

    geo_dict = all_geo_last_week_dict['all_geo_last_week']
    for geo in geo_dict:
        location_0 = geo[f'{location_granularity[0]}']
        location_1 = geo[f'{location_granularity[1]}']
        location_2 = geo[f'{location_granularity[2]}']
        query = [
            {
                "$match": {
                    'collection_date': {
                        '$lt': today_date,
                        '$gte': last_week_date
                    },
                    'c_coll_date_prec': {
                        '$eq': 2
                    },
                    f'location.{location_granularity[0]}': {
                        '$eq': location_0
                    },
                    f'location.{location_granularity[1]}': {
                        '$eq': location_1
                    },
                    f'location.{location_granularity[2]}': {
                        '$eq': location_2
                    }
                },
            },
            {
                "$group": {"_id": {'lineage': '$covv_lineage'},
                           "count": {"$sum": 1}
                           }
            },
            {"$sort":
                {"count": -1}
             }
        ]
        results = collection_db.aggregate(query, allowDiskUse=True)
        list_geo_lineage_dict = []
        for single_item in results:
            geo_list = all_geo_last_week_dict['all_geo_last_week']
            total_sequences = 0
            for loc_geo in geo_list:
                if loc_geo[f'{location_granularity[0]}'] == location_0 \
                        and loc_geo[f'{location_granularity[1]}'] == location_1 \
                        and loc_geo[f'{location_granularity[2]}'] == location_2:
                    total_sequences = loc_geo['count']
            # print("qui", single_item['_id']['lineage'], location, single_item['count'], total_sequences)
            if single_item['count'] / total_sequences > 0.01:
                single_item_remodel = {f'{location_granularity[0]}': location_0,
                                       f'{location_granularity[1]}': location_1,
                                       f'{location_granularity[2]}': location_2,
                                       'lineage': single_item['_id']['lineage'],
                                       'count': single_item['count']}
                list_geo_lineage_dict.append(single_item_remodel)
        name = str(location_0) + '_' + str(location_1) + '_' + str(location_2)
        all_lineage_for_geo_last_week[name] = list_geo_lineage_dict
    print("fine request all_lineages")
    get_all_mutation_for_lineage_for_each_geo_previous_week(location_granularity)


dict_count_aggregated_place = {}
dict_aggregated_place = {}


def populate_aggregate_place_dict(full_object, location_granularity, today_date, granularity):
    location_0 = full_object[f'{location_granularity[0]}']
    location_1 = full_object[f'{location_granularity[1]}']
    location_2 = full_object[f'{location_granularity[2]}']
    lineage = full_object['lineage']
    mut = full_object['mut']
    denominator_world_prev_week = full_object['total_seq_world_prev_week']
    denominator_world_this_week = full_object['total_seq_world_this_week']
    results_prev_week = full_object['count_prev_week']
    results_this_week = full_object['count_this_week']
    denominator_prev_week = full_object['total_seq_pop_prev_week']
    denominator_this_week = full_object['total_seq_pop_this_week']

    if granularity == 1:
        distinct_name_granularity = location_1 + lineage + mut
    elif granularity == 0:
        distinct_name_granularity = location_0 + lineage + mut
    else:
        distinct_name_granularity = lineage + mut

    if distinct_name_granularity not in dict_aggregated_place:
        specific_object_granularity = \
            {'lineage': lineage,
             'mut': mut,
             'total_seq_world_prev_week': denominator_world_prev_week,
             'total_seq_world_this_week': denominator_world_this_week,
             'total_seq_pop_prev_week': 0,
             'total_seq_pop_this_week': 0,
             'count_prev_week': results_prev_week,
             'count_this_week': results_this_week,
             'perc_prev_week': 0,
             'perc_this_week': 0,
             'diff_perc': 0,
             'date': today_date.strftime("%Y-%m-%d"),
             }
        if granularity == 1:
            specific_object_granularity[f'{location_granularity[0]}'] = location_0
            specific_object_granularity[f'{location_granularity[1]}'] = location_1
            specific_object_granularity[f'{location_granularity[2]}'] = None
            specific_object_granularity['granularity'] = location_granularity[granularity]
        elif granularity == 0:
            specific_object_granularity[f'{location_granularity[0]}'] = location_0
            specific_object_granularity[f'{location_granularity[1]}'] = None
            specific_object_granularity[f'{location_granularity[2]}'] = None
            specific_object_granularity['granularity'] = location_granularity[granularity]
        else:
            specific_object_granularity[f'{location_granularity[0]}'] = None
            specific_object_granularity[f'{location_granularity[1]}'] = None
            specific_object_granularity[f'{location_granularity[2]}'] = None
            specific_object_granularity['granularity'] = 'world'
        dict_aggregated_place[distinct_name_granularity] = specific_object_granularity
    else:
        dict_aggregated_place[distinct_name_granularity]['count_prev_week'] = \
            dict_aggregated_place[distinct_name_granularity]['count_prev_week'] \
            + results_prev_week
        dict_aggregated_place[distinct_name_granularity]['count_this_week'] = \
            dict_aggregated_place[distinct_name_granularity]['count_this_week'] \
            + results_this_week

    if granularity == 1:
        distinct_nm_count_granularity = location_1 + lineage
    elif granularity == 0:
        distinct_nm_count_granularity = location_0 + lineage
    else:
        distinct_nm_count_granularity = lineage
    if distinct_nm_count_granularity not in dict_count_aggregated_place:
        dict_count_aggregated_place[distinct_nm_count_granularity] = {}
        dict_count_aggregated_place[distinct_nm_count_granularity]['array_sub_place'] \
            = [location_2]
        dict_count_aggregated_place[distinct_nm_count_granularity]['total_seq_pop_prev_week'] \
            = denominator_prev_week
        dict_count_aggregated_place[distinct_nm_count_granularity]['total_seq_pop_this_week'] \
            = denominator_this_week
    else:
        if location_2 not in \
                dict_count_aggregated_place[distinct_nm_count_granularity]['array_sub_place']:
            dict_count_aggregated_place[distinct_nm_count_granularity][
                'total_seq_pop_prev_week'] = \
                dict_count_aggregated_place[distinct_nm_count_granularity][
                    'total_seq_pop_prev_week'] + denominator_prev_week
            dict_count_aggregated_place[distinct_nm_count_granularity][
                'total_seq_pop_this_week'] = \
                dict_count_aggregated_place[distinct_nm_count_granularity][
                    'total_seq_pop_this_week'] + denominator_this_week
            dict_count_aggregated_place[distinct_nm_count_granularity][
                'array_sub_place'].append(location_2)


def get_final_object_aggregated_place(single_obj):
    final_obj = single_obj
    granularity = final_obj['granularity']

    if granularity != 'world':
        name_granularity_granularity = final_obj[f'{granularity}'] + final_obj['lineage']
    else:
        name_granularity_granularity = final_obj['lineage']
    denominator_prev_week_granularity = \
        dict_count_aggregated_place[name_granularity_granularity]['total_seq_pop_prev_week']
    denominator_this_week_granularity = \
        dict_count_aggregated_place[name_granularity_granularity]['total_seq_pop_this_week']
    final_obj['total_seq_pop_prev_week'] = denominator_prev_week_granularity
    final_obj['total_seq_pop_this_week'] = denominator_this_week_granularity
    if final_obj['total_seq_pop_prev_week'] != 0:
        final_obj['perc_prev_week'] = (final_obj['count_prev_week'] / final_obj['total_seq_pop_prev_week']) * 100
    else:
        final_obj['perc_prev_week'] = 0
    if final_obj['total_seq_pop_this_week'] != 0:
        final_obj['perc_this_week'] = (final_obj['count_this_week'] / final_obj['total_seq_pop_this_week']) * 100
    else:
        final_obj['perc_this_week'] = 0
    final_obj['diff_perc'] = abs(final_obj['perc_prev_week'] - final_obj['perc_this_week'])
    return final_obj


def get_all_mutation_for_lineage_for_each_geo_previous_week(location_granularity):
    print("inizio request all_mutation all_lineages previous week")
    today_date = datetime.strptime("2021-08-08", '%Y-%m-%d')
    last_week_date = today_date.replace(day=today_date.day) - timedelta(days=7)
    previous_week_date = last_week_date.replace(day=last_week_date.day) - timedelta(days=7)

    geo_dict = all_geo_last_week_dict['all_geo_last_week']
    all_all_mut_for_lineage_for_geo = []
    denominator_world_prev_week = world_growth_obj['world_growth']['count_prev_week']
    denominator_world_this_week = world_growth_obj['world_growth']['count_this_week']
    # all_all_mut_for_lineage_for_geo = [world_growth_obj['world_growth']]
    i = 0
    total_num_of_geo = len(geo_dict)
    for geo in geo_dict:
        i = i + 1
        print("GEO: ", i, " / ", total_num_of_geo)
        location_0 = geo[f'{location_granularity[0]}']
        location_1 = geo[f'{location_granularity[1]}']
        location_2 = geo[f'{location_granularity[2]}']
        name = str(location_0) + '_' + str(location_1) + '_' + str(location_2)
        for lineage_obj in all_lineage_for_geo_last_week[name]:
            lineage = lineage_obj['lineage']
            # print("mut", location_0, location_1, location_2, lineage)
            all_mutation_for_lineage_for_geo_previous_week = [world_growth_obj['world_growth']]
            lineage_growth_result = lineage_growth(today_date, location_granularity,
                                                   location_0, location_1, location_2, lineage)
            all_mutation_for_lineage_for_geo_previous_week.append(lineage_growth_result)
            # all_all_mut_for_lineage_for_geo.append(lineage_growth_result)

            denominator_prev_week = lineage_growth_result['count_prev_week']
            denominator_this_week = lineage_growth_result['count_this_week']

            # if lineage == 'B.1.617.2':
            all_mutations_dict = get_all_mutation_not_characteristics(lineage,
                                                                      location_0, location_1, location_2,
                                                                      today_date, location_granularity)
            mut_dict = all_mutations_dict[lineage]
            for mut in mut_dict[1]:
                if '*' not in mut and '_-' not in mut:      # and 'Spike' in mut:
                    query = {
                                'c_coll_date_prec': {
                                    '$eq': 2
                                },
                                f'location.{location_granularity[0]}': {
                                    '$eq': location_0
                                },
                                f'location.{location_granularity[1]}': {
                                    '$eq': location_1
                                },
                                f'location.{location_granularity[2]}': {
                                    '$eq': location_2
                                },
                                'covv_lineage': {
                                    '$eq': lineage
                                },
                                'covsurver_prot_mutations': {
                                    '$regex': mut, '$options': 'i'
                                }
                            }
                    query_this_week = query.copy()
                    query_prev_week = query.copy()
                    query_this_week['collection_date'] = {'$lt': today_date, '$gte': last_week_date}
                    query_prev_week['collection_date'] = {'$lt': last_week_date, '$gte': previous_week_date}
                    results_this_week = collection_db.count_documents(query_this_week)
                    results_prev_week = collection_db.count_documents(query_prev_week)
                    if denominator_prev_week != 0:
                        perc_prev_week = (results_prev_week/denominator_prev_week)*100
                    else:
                        perc_prev_week = 0
                    if denominator_this_week != 0:
                        perc_this_week = (results_this_week/denominator_this_week)*100
                    else:
                        perc_this_week = 0
                    diff_perc = abs(perc_this_week-perc_prev_week)

                    full_object = {f'{location_granularity[0]}': location_0,
                                   f'{location_granularity[1]}': location_1,
                                   f'{location_granularity[2]}': location_2,
                                   'lineage': lineage,
                                   'mut': mut,
                                   'total_seq_world_prev_week': denominator_world_prev_week,
                                   'total_seq_world_this_week': denominator_world_this_week,
                                   'total_seq_pop_prev_week': denominator_prev_week,
                                   'total_seq_pop_this_week': denominator_this_week,
                                   'count_prev_week': results_prev_week,
                                   'count_this_week': results_this_week,
                                   'perc_prev_week': perc_prev_week,
                                   'perc_this_week': perc_this_week,
                                   'diff_perc': diff_perc,
                                   'date': today_date.strftime("%Y-%m-%d"),
                                   'granularity': location_granularity[2]
                                   }

                    # all_mutation_for_lineage_for_geo_previous_week.append(full_object)
                    all_all_mut_for_lineage_for_geo.append(full_object)

                    populate_aggregate_place_dict(full_object, location_granularity, today_date, granularity=1)
                    populate_aggregate_place_dict(full_object, location_granularity, today_date, granularity=0)
                    populate_aggregate_place_dict(full_object, location_granularity, today_date, granularity=-1)

            # name_csv = lineage + '.csv'
            # directory = f'CSV_examples/{location_0}/{location_1}/{location_2}'
            # if not os.path.exists(directory):
            #     os.makedirs(directory)
            # table = pd.DataFrame(all_mutation_for_lineage_for_geo_previous_week)
            # table.to_csv(rf'{directory}/{name_csv}',
            #              index=False, header=True)

    for aggregated_loc in dict_aggregated_place:
        single_obj = dict_aggregated_place[aggregated_loc].copy()
        final_obj = get_final_object_aggregated_place(single_obj)
        all_all_mut_for_lineage_for_geo.append(final_obj)

    table2 = pd.DataFrame(all_all_mut_for_lineage_for_geo)
    table2.to_json('database.json', orient='records', lines=True)
    end = timeit.default_timer()
    print("TIMER ", end - start)
    print("fine request all_mutation all_lineages")


all_geo_granularity = ['geo_group', 'country', 'region']
start = timeit.default_timer()
get_all_geo_last_week(location_granularity=all_geo_granularity)
