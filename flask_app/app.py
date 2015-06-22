# coding: utf-8
"""Provide an API to convert probsenzlist to mutisenzlist."""

__author__ = 'jiaying.lu'

from flask import Flask
from flask import json, request
from numpy import log
import os

from config import *
import bugsnag
from bugsnag.flask import handle_exceptions
import logging
from logentries import LogentriesHandler

# Configure Logentries
logger = logging.getLogger('logentries')
logger.setLevel(logging.INFO)
test = LogentriesHandler(LOGENTRIES_TOKEN)
logger.addHandler(test)

# Configure Bugsnag
bugsnag.configure(
    api_key=BUGSNAG_TOKEN,
    project_root=os.path.dirname(os.path.realpath(__file__)),
)

app = Flask(__name__)

# Attach Bugsnag to Flask's exception handler
handle_exceptions(app)


def _probSenz_zip(probSenzList_elem, prob_lower_bound):
    """
    Zip one elem of probSenzList
    
    Args:
        probSenzList_elem: dict, one elem of probSenzList
        prob_lower_bound: float
    Returns:
        senzList_elem_candidate: list, like [[], [], []]

    """
    motions = probSenzList_elem['motion']
    locations = probSenzList_elem['location']
    sounds = probSenzList_elem['sound']
    senzList_elem_candidate = [{'motion':motion_key, 'location':location_key, 'sound':sound_key, 'prob':log(motion_prob)+log(location_prob)+log(sound_prob)}
                               for (motion_key, motion_prob) in motions.iteritems()
                               for (location_key, location_prob) in locations.iteritems()
                               for (sound_key, sound_prob) in sounds.iteritems()
                               if log(motion_prob)+log(location_prob)+log(sound_prob) > prob_lower_bound
                              ]
    return senzList_elem_candidate


def _ziped2muti(probSenzList_zip, prob_lower_bound):
    """
    Convert ziped prob list to muti list 
    
    Args:
        probSenzList_zip: list, zipped probSenzList
        prob_lower_bound: float
    Returns:
        mutiSenzList
    """
    # TODO: use collections.deque to replace list if faster removal needed
    logger.debug('[_ziped2muti] probSenzList_zip: ', len(probSenzList_zip))
    before_stack = [{'senzList':[e], 'prob':e['prob']} for e in probSenzList_zip[0]]
    after_stack = []

    for index in range(1, len(probSenzList_zip)):
        #print('0 before_stack ', len(before_stack))
        #print('0 after_stack ', len(after_stack))
        while before_stack != []:
            stack_elem = before_stack.pop(0)
            for elem in probSenzList_zip[index]:
                after_stack_elem = {}
                after_stack_elem['senzList'] = stack_elem['senzList'] + [elem]
                after_stack_elem['prob'] = stack_elem['prob'] + elem['prob']
                if after_stack_elem['prob'] > prob_lower_bound:
                    after_stack.append(after_stack_elem)
        #print('1 before_stack ', len(before_stack))
        #print('1 after_stack ', len(after_stack))
        before_stack = after_stack
        after_stack = []
        #print('2 before_stack ', len(before_stack))
        #print('2 after_stack ', len(after_stack))

    return before_stack


def prob2muti(probSenzList, prob_lower_bound=log(1e-30)):
    """
    Convert probSenzList to mutiSenzList

    Args:
        probSenzList: list
        prob_lower_bound: float, should return senz list whose probability is 
                     greater than lower_bound
    Returns:
        mutiSenzList: list, and its prob has been log(prob)
    """
    if probSenzList == []:
        return []

    probSenzList_zip = [_probSenz_zip(elem, prob_lower_bound) for elem in probSenzList]
    #logger.debug(probSenzList_zip) # DONE

    mutiSenzList = _ziped2muti(probSenzList_zip, prob_lower_bound)
    #logger.debug(mutiSenzList)

    return mutiSenzList


def _probSenz_zip_top_N(probSenzList_elem, top_N, prob_lower_bound):
    """
    Zip one elem of probSenzList, for quick version
    
    Args:
        probSenzList_elem: dict, one elem of probSenzList
        top_N:
        prob_lower_bound: float, should return senz list whose probability is 
                     greater than lower_bound
    Returns:
        senzList_elem_candidates: list, like [{}, {}, {}]

    """
    senzList_elem_candidates = []
    probSenzList_elem_processed = {}
    dict_sorted = lambda dt: sorted(dt.iteritems(), key=lambda d: d[1], reverse=True)

    other_keys = []
    for key, value in probSenzList_elem.iteritems():
        if key in ['motion', 'location', 'sound']:
            probSenzList_elem_processed[key] = dict_sorted(value)
        else:
            other_keys.append(key)

    for i in xrange(top_N):
        senzList_elem_candidate = {'prob': 0.0}
        for key, value in probSenzList_elem_processed.iteritems():
            senzList_elem_candidate[key] = value[i if i<len(value) else len(value)-1][0]
            senzList_elem_candidate['prob'] += log(value[i if i<len(value) else len(value)-1][1])
        # TODO: 看要不要加timestamp
        for key in other_keys:
            senzList_elem_candidate[key] = probSenzList_elem[key]
        if senzList_elem_candidate['prob'] > prob_lower_bound:
            senzList_elem_candidates.append(senzList_elem_candidate)
    
    return senzList_elem_candidates


def _ziped2muti_top_N(probSenzList_zip, top_N, prob_lower_bound):
    """
    Convert ziped prob list to muti list, for quick version
    
    Args:
        probSenzList_zip: list, zipped probSenzList
        top_N: 只算最大的top_N个
        prob_lower_bound: float
    Returns:
        mutiSenzList
    """
    mutiSenzList = []

    for i in xrange(top_N):
        mutiSenzList_elem = {'prob':0.0, 'senzList':[]}
        for elem in probSenzList_zip:
            mutiSenzList_elem['prob'] += elem[i].pop('prob')
            mutiSenzList_elem['senzList'].append(elem[i])
        mutiSenzList.append(mutiSenzList_elem)

    return mutiSenzList


def prob2muti_quick(probSenzList, top_N, prob_lower_bound=log(1e-30)):
    """
    Convert probSenzList to mutiSenList quickly.

    Because prob2mut() which calculate every potential result cost too much resource.

    Args:
        probSenzList: list
        top_N: 只算最大的top_N个
        prob_lower_bound: float, should return senz list whose probability is 
                     greater than lower_bound
    Returns:
        mutiSenzList: list, and its prob has been log(prob)
    """
    if probSenzList == []:
        return []

    probSenzList_zip = [_probSenz_zip_top_N(elem, top_N, prob_lower_bound) for elem in probSenzList]
    #app.logger.debug(probSenzList_zip) # DONE

    mutiSenzList = _ziped2muti_top_N(probSenzList_zip, top_N, prob_lower_bound)
    #app.logger.debug(mutiSenzList)

    return mutiSenzList


@app.before_first_request
def init_before_first_request():
    import datetime

    init_tag = "[Initiation of Service Process]\n"


    log_init_time = "Initiation START at: \t%s\n" % datetime.datetime.now()
    log_app_env = "Environment Variable: \t%s\n" % APP_ENV
    log_bugsnag_token = "Bugsnag Service TOKEN: \t%s\n" % BUGSNAG_TOKEN
    log_logentries_token = "Logentries Service TOKEN: \t%s\n" % LOGENTRIES_TOKEN
    logger.info(init_tag + log_init_time)
    logger.info(init_tag + log_app_env)
    logger.info(init_tag + log_bugsnag_token)
    logger.info(init_tag + log_logentries_token)


@app.route('/', methods=['POST'])
def converter():
    logger.debug('[Enter converter()] params: %s' % (request.data))
    result = {'code':1, 'message':''}

    if request.headers.has_key('X-Request-Id'):
        x_request_id = request.headers['X-Request-Id']
    else:
        x_request_id = ''

    # params JSON validate
    try:
        params = json.loads(request.data)
    except ValueError, err_msg:
        logger.error('%s, [ValueError] err_msg: %s, params=%s' % (x_request_id, err_msg, request.data))
        result['message'] = 'Unvalid params: NOT a JSON Object'
        return json.dumps(result)

    # params key checking
    try:
        prob_senzlist = params['probSenzList']
        strategy = params['strategy']
        mutiSenzList_max_num = params.get('mutiMaxNum', 3) 
    except KeyError, err_msg:
        logger.error("%s, [KeyError] can't find key=%s in params=%s" % (x_request_id, err_msg, params))
        result['message'] = "Params content Error: cant't find key=%s"
        return json.dumps(result)
    
    # TODO: 不同策略不同处理
    if strategy == 'SELECT_MAX_PROB':
        result['code'] = 0
        result['message'] = 'success'
        muti_senzlist = prob2muti(prob_senzlist, log(1e-30))
        muti_senzlist = sorted(muti_senzlist, key=lambda elem: elem['prob'], reverse=True)
        result['result'] = muti_senzlist[:mutiSenzList_max_num]
    if strategy == 'SELECT_MAX_N_PROB':
        result['code'] = 0
        result['message'] = 'success'
        muti_senzlist = prob2muti_quick(prob_senzlist, mutiSenzList_max_num, log(1e-30))
        result['result'] = muti_senzlist
    else:
        result['message'] = 'strategy error'

    logger.info('%s, [converter success] strategy:%s, code:%s, result_len:%s' %(x_request_id, strategy, result['code'], len(result)))
    return json.dumps(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

