#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#####
# Author: Charlene Leong charleneleong84@gmail.com
# Created Date: Monday, November 8th 2021, 8:15:18 pm
# Last Modified: Sunday, November 14th 2021,10:43:36 am
#####

import pytest
import json
from pprint import pprint
import typing
from typing_extensions import get_args

from relevanceai.http_client import Client
from relevanceai.visualise.constants import DIM_REDUCTION, DIM_REDUCTION_DEFAULT_ARGS
from relevanceai.visualise.constants import CLUSTER, CLUSTER_DEFAULT_ARGS


# for cluster_type in get_args(CLUSTER)
# #         if type(cluster_type)==typing._GenericAlias
# #         for c in get_args(cluster_type)
# #         if c is not None

@pytest.fixture(name='dataset_args', 
params =[ 
        { 
        "dataset_id" : "ecommerce-6",
        "vector_field": "product_name_imagetext_vector_",
        "number_of_points_to_render" : 100,
        "random_state" : 0,
        "vector_label" : "product_name",
        "vector_label_char_length"  : 12,
        "hover_label": ["category"],
        },
        { 
        "dataset_id" : "unsplash-images",
        "vector_field": "image_url_vector_",
        "colour_label": "dictionary_label_2",
        "colour_label_char_length" : 20,
        "number_of_points_to_render" : 100,
        "random_state" : 42
        },
        { 
        "dataset_id" : "medium_topics",
        "vector_field": "topics_use_multi_vector_",
        "colour_label": "topics",
        "colour_label_char_length" : 20,
        "number_of_points_to_render" : None,
        "random_state" : 42
        },
    ])
def fixture_dataset_args(request):
    return request.param
    
    
@pytest.fixture(name='dr_args',
params= [
    {"dr": dr,
     "dr_args": {
        **DIM_REDUCTION_DEFAULT_ARGS[dr]   
    }
    } for dr in get_args(DIM_REDUCTION)
])
def fixture_dr_args(request):
    return request.param



# @pytest.fixture(name='cluster_args',
# params= [
#     {"cluster": c,
#      "cluster_args": {
#         **CLUSTER_DEFAULT_ARGS[c]   
#     }
#     } for cluster_type in get_args(CLUSTER)
#         if type(cluster_type)==typing._GenericAlias
#         for c in get_args(cluster_type)
#         if c is not None
# ])
# def fixture_cluster_args(request):
#     return request.param

    
def test_plot(test_client, dataset_args, dr_args):
    """Testing colour plot with cluster"""
    
    pprint(json.dumps({**dataset_args, **dr_args,}, indent=4))
    test_client.projector.plot(**dataset_args, **dr_args, )

    assert True