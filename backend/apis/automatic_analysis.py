from __future__ import print_function

import timeit

import re
import pandas as pd

from datetime import datetime, timedelta
from flask_restplus import Namespace, Resource
from pymongo import MongoClient

api = Namespace('automatic_analysis', description='automatic_analysis')

uri = "mongodb://localhost:27017/gcm_gisaid"
client = MongoClient(uri)
db = client.gcm_gisaid

# collection_db = db.seq_2021_08_26_2
collection_db = db.seq_test_1
collection_update_date = db.db_meta
collection_result_variant_db = db.prova_results_variant


PATTERN = re.compile("([a-zA-Z0-9]+)_([a-zA-Z~@#$^*()_+=[\]{}|\\,.?: -]+)([\d]+)([a-zA-Z~@#$^*()_+=[\]{}|\\,.?: -]+)")


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


def get_all_mutation_not_characteristics(lineage, location_0, location_1, location_2, today_date, location_granularity,):

    last_week_date = today_date.replace(day=today_date.day) - timedelta(days=7)
    previous_week_date = last_week_date.replace(day=last_week_date.day) - timedelta(days=7)

    query_count = {
            'c_coll_date_prec': {
                '$eq': 2
            },
            'collection_date': {
                '$lt': today_date,
                '$gte': previous_week_date
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

    denominator_lineage = collection_db.count_documents(query_count)

    pipeline = [
        {"$match": {
            'c_coll_date_prec': {
                '$eq': 2
            },
            'collection_date': {
                '$lt': today_date,
                '$gte': previous_week_date
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
    results = (x['_id'] for x in results if 0.75 > x['count'] / denominator_lineage > 0.01)

    result_array = []
    for x in results:
        ch = f"{x['pro']}_{x['org']}{x['loc']}{x['alt']}"
        result_array.append(ch)

    return result_array


all_geo_last_week_dict = {}


def get_all_geo_last_week(location_granularity, today_date):
    print("inizio request geo last week")

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
    get_all_lineage_for_each_geo(location_granularity, today_date)


all_lineage_for_geo_last_week = {}


def get_all_lineage_for_each_geo(location_granularity, today_date):
    print("inizio request all_lineages")
    last_week_date = today_date.replace(day=today_date.day) - timedelta(days=7)

    geo_dict = all_geo_last_week_dict['all_geo_last_week']
    for geo in geo_dict:
        location_0 = geo[f'{location_granularity[0]}']
        location_1 = geo[f'{location_granularity[1]}']
        location_2 = geo[f'{location_granularity[2]}']
        # if(location_0 == 'Europe' and location_1 == 'Italy' and (location_2 == 'Abruzzo' or location_2 == 'Lombardia')
        #         or (location_0 == 'North America' and location_1 == 'Canada' and location_2 == 'Alberta')):
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
    get_all_mutation_for_lineage_for_each_geo_previous_week(location_granularity, today_date)


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


def get_all_mutation_for_lineage_for_each_geo_previous_week(location_granularity, today_date):
    print("inizio request all_mutation all_lineages previous week")
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
        print("GEO: ", i, " / ", total_num_of_geo, '_time_: ', start)
        location_0 = geo[f'{location_granularity[0]}']
        location_1 = geo[f'{location_granularity[1]}']
        location_2 = geo[f'{location_granularity[2]}']
        # if(location_0 == 'Europe' and location_1 == 'Italy' and (location_2 == 'Abruzzo' or location_2 == 'Lombardia')
        #          or (location_0 == 'North America' and location_1 == 'Canada' and location_2 == 'Alberta')):
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
                                                                      today_date, location_granularity,)
            mut_dict = all_mutations_dict
            for mut in mut_dict:
                if '*' not in mut and '_-' not in mut:      # and 'Spike' in mut:

                    m = PATTERN.fullmatch(mut)
                    if m:
                        protein, orig, loc, alt = m.groups()
                        orig = orig.replace('stop', '*')
                        alt = alt.replace('stop', '*')

                        loc = int(loc)
                        if orig == 'ins':
                            orig = '-' * len(alt)
                            t = 'INS'
                        elif alt == 'del':
                            alt = '-'
                            t = 'DEL'
                        else:
                            t = 'SUB'

                        length = len(alt)
                        new_mut = {'pro': protein, 'org': orig,
                                   'loc': loc, 'alt': alt,
                                   'typ': t, 'len': length}

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
                            'muts': {'$elemMatch': {
                                'pro': new_mut['pro'],
                                'loc': new_mut['loc'],
                                'alt': new_mut['alt'],
                                'org': new_mut['org'],
                            }
                            },
                        }
                        # 'covsurver_prot_mutations': {
                        #     '$regex': mut, '$options': 'i'
                        # },
                        query_this_week = query.copy()
                        query_prev_week = query.copy()
                        query_this_week['collection_date'] = {'$lt': today_date, '$gte': last_week_date}
                        query_prev_week['collection_date'] = {'$lt': last_week_date, '$gte': previous_week_date}
                        results_this_week = collection_db.count_documents(query_this_week)
                        results_prev_week = collection_db.count_documents(query_prev_week)
                        if denominator_prev_week != 0:
                            perc_prev_week = (results_prev_week / denominator_prev_week) * 100
                        else:
                            perc_prev_week = 0
                        if denominator_this_week != 0:
                            perc_this_week = (results_this_week / denominator_this_week) * 100
                        else:
                            perc_this_week = 0
                        diff_perc = abs(perc_this_week - perc_prev_week)

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

                        populate_aggregate_place_dict(full_object, location_granularity, today_date,
                                                      granularity=1)
                        populate_aggregate_place_dict(full_object, location_granularity, today_date,
                                                      granularity=0)
                        populate_aggregate_place_dict(full_object, location_granularity, today_date,
                                                      granularity=-1)

                    # name_csv = lineage + '.csv'
                    # directory = f'CSV_examples/{location_0}/{location_1}/{location_2}'
                    # if not os.path.exists(directory):
                    #     os.makedirs(directory)
                    # table = pd.DataFrame(all_mutation_for_lineage_for_geo_previous_week)
                    # table.to_csv(rf'{directory}/{name_csv}',
                    #              index=False, header=True)
                    else:
                        print('======> ERROR', mut)

    for aggregated_loc in dict_aggregated_place:
        single_obj = dict_aggregated_place[aggregated_loc].copy()
        final_obj = get_final_object_aggregated_place(single_obj)
        all_all_mut_for_lineage_for_geo.append(final_obj)

    table2 = pd.DataFrame(all_all_mut_for_lineage_for_geo)
    file_name = 'database_variants_' + today_date.strftime("%Y-%m-%d") + '.json'
    table2.to_json(f'{file_name}', orient='records', lines=True)
    end = timeit.default_timer()
    print("TIMER ", end - start)
    print("fine request all_mutation all_lineages")


def prova_query():
    date1 = datetime.strptime('2021-08-08', '%Y-%m-%d')
    date2 = date1.replace(day=date1.day) - timedelta(days=7)

    query = [
        {"$match": {
            'c_coll_date_prec': {
                '$eq': 2
            },
            'collection_date': {
                '$lt': date1,
                '$gte': date2
            },
            f'location.geo_group': {
                '$eq': 'Europe'
            },
            f'location.country': {
                '$eq': 'United Kingdom'
            },
            f'location.region': {
                '$eq': 'England'
            },
            'covv_lineage': {
                '$eq': 'B.1.617.2'
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

    # query = [
    #     {
    #         '$match': {
    #               'c_coll_date_prec': {
    #                 '$eq': 2
    #               },
    #               'collection_date': {
    #                 '$lt': date1,
    #                 '$gte': date2
    #               },
    #               'location.region':{
    #                 '$eq': 'England'
    #               },
    #             'muts': {'$elemMatch':
    #                          {'pro': 'NS8',
    #                           'loc': 86,
    #                           'alt': '-',
    #                           'org': 'F',
    #                           }
    #                      },
    #             }
    #     }, {
    #         '$group': {
    #             '_id': {},
    #             'count': {
    #                 '$sum': 1
    #             }
    #         }
    #     }
    # ]

    res = collection_db.aggregate(query, allowDiskUse=True)
    print("prova results: ", list(res))


all_geo_granularity = ['geo_group', 'country', 'region']

# prova_query()
# array_date = ['2021-08-08', ..., '2021-10-31']
array_date = ['2021-10-24']
for single_date in array_date:
    start = timeit.default_timer()
    date = datetime.strptime(single_date, '%Y-%m-%d')
    get_all_geo_last_week(location_granularity=all_geo_granularity, today_date=date)

#######################################################


@api.route('/getAllGeo')
class FieldList(Resource):
    @api.doc('get_all_geo')
    def get(self):
        # today_date = datetime.strptime("2021-08-08", '%Y-%m-%d')
        # {
        #     "$match": {
        #         'analysis_date': {
        #             '$eq': today_date
        #         },
        #     },
        # },

        query = [
            {"$group": {"_id": {'geo_group': '$geo_group',
                                'country': "$country",
                                'region': "$region",
                                },
                        }
             },
            ]

        results = collection_result_variant_db.aggregate(query, allowDiskUse=True)

        array_continent = []
        array_country = []
        array_region = []
        for single_item in results:
            if single_item['_id']['geo_group'] not in array_continent:
                array_continent.append(single_item['_id']['geo_group'])
            if single_item['_id']['country'] not in array_country:
                array_country.append(single_item['_id']['country'])
            if single_item['_id']['region'] not in array_region:
                array_region.append(single_item['_id']['region'])
        results = {'continent': array_continent, 'country': array_country, 'region': array_region}

        return results


@api.route('/getStatistics')
class FieldList(Resource):
    @api.doc('get_statistics')
    def post(self):
        payload = api.payload
        granularity = payload['granularity']
        location = payload['value']
        payload_date = payload['date']

        today_date = datetime.strptime(f"{payload_date}", '%Y-%m-%d')
        where_part = {'analysis_date': {'$eq': today_date}}

        real_granularity_1 = 'world'
        real_granularity_2 = 'geo_group'
        if granularity == 'region':
            real_granularity_1 = granularity
            array_conditions = []
            specific_or_1 = {'granularity': {'$eq': real_granularity_1}}
            array_conditions.append(specific_or_1)
            where_part['$or'] = array_conditions
            # where_part['granularity'] = {'$eq': granularity}
            where_part[granularity] = {'$eq': location}
        if granularity == 'country':
            real_granularity_1 = granularity
            real_granularity_2 = 'region'
            array_conditions = []
            specific_or_1 = {'granularity': {'$eq': real_granularity_1}}
            array_conditions.append(specific_or_1)
            specific_or_2 = {'granularity': {'$eq': real_granularity_2}}
            array_conditions.append(specific_or_2)
            where_part['$or'] = array_conditions
            # where_part['granularity'] = {'$eq': granularity}
            where_part[granularity] = {'$eq': location}
        elif granularity == 'continent':
            real_granularity_1 = 'geo_group'
            real_granularity_2 = 'country'
            array_conditions = []
            specific_or_1 = {'granularity': {'$eq': real_granularity_1}}
            array_conditions.append(specific_or_1)
            specific_or_2 = {'granularity': {'$eq': real_granularity_2}}
            array_conditions.append(specific_or_2)
            where_part['$or'] = array_conditions
            # where_part['granularity'] = {'$eq': real_granularity_1}
            where_part['geo_group'] = {'$eq': location}
        else:
            array_conditions = []
            specific_or_1 = {'granularity': {'$eq': real_granularity_1}}
            array_conditions.append(specific_or_1)
            specific_or_2 = {'granularity': {'$eq': real_granularity_2}}
            array_conditions.append(specific_or_2)
            where_part['$or'] = array_conditions
            # where_part['granularity'] = {'$eq': real_granularity}

        match_part = {'$match': where_part}
        query = [match_part]
        results = collection_result_variant_db.aggregate(query, allowDiskUse=True)

        array_results = []
        for res in list(results):
            single_obj = {'location': 'World'}
            for key in res:
                if key == 'analysis_date':
                    single_obj[key] = str(res[key]).split("T")[0]
                else:
                    single_obj[key] = res[key]
            array_results.append(single_obj)

        return array_results
