# coding: utf-8
"""Provide an API to convert probsenzlist to mutisenzlist."""

__author__ = 'jiaying.lu'

from flask import Flask
from flask import json, request
from numpy import log

app = Flask(__name__)

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
    print('probSenzList_zip: ', len(probSenzList_zip))
    before_stack = [{'senzList':[e], 'prob':e['prob']} for e in probSenzList_zip[0]]
    after_stack = []

    for index in range(1, len(probSenzList_zip)):
        print('0 before_stack ', len(before_stack))
        print('0 after_stack ', len(after_stack))
        while before_stack != []:
            stack_elem = before_stack.pop(0)
            for elem in probSenzList_zip[index]:
                after_stack_elem = {}
                after_stack_elem['senzList'] = stack_elem['senzList'] + [elem]
                after_stack_elem['prob'] = stack_elem['prob'] + elem['prob']
                if after_stack_elem['prob'] > prob_lower_bound:
                    after_stack.append(after_stack_elem)
        print('1 before_stack ', len(before_stack))
        print('1 after_stack ', len(after_stack))
        before_stack = after_stack
        after_stack = []
        print('2 before_stack ', len(before_stack))
        print('2 after_stack ', len(after_stack))

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
    #app.logger.debug(probSenzList_zip) # DONE

    mutiSenzList = _ziped2muti(probSenzList_zip, prob_lower_bound)
    #app.logger.debug(mutiSenzList)

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

    for key, value in probSenzList_elem.iteritems():
        if key != 'timestamp':
            probSenzList_elem_processed[key] = dict_sorted(value)

    for i in xrange(top_N):
        senzList_elem_candidate = {'prob': 0.0}
        for key, value in probSenzList_elem_processed.iteritems():
            senzList_elem_candidate[key] = value[i if i<len(value) else len(value)-1][0]
            senzList_elem_candidate['prob'] += log(value[i if i<len(value) else len(value)-1][1])
        # TODO: 看要不要加timestamp
        #senzList_elem_candidate['timestamp'] = probSenzList_elem['timestamp']
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

    #TODO: 完成第二步
    mutiSenzList = _ziped2muti_top_N(probSenzList_zip, top_N, prob_lower_bound)
    #app.logger.debug(mutiSenzList)

    return mutiSenzList


@app.route('/senzlist/prob2muti/', methods=['POST'])
def converter():
    #app.logger.debug('Enter converter(), params: %s' % (request.data))

    result = {'code':1, 'message':''}
    
    # params JSON validate
    try:
        params = json.loads(request.data)
    except ValueError, err_msg:
        #app.logger.error('[ValueError] err_msg: %s, params=%s' % (err_msg, params))
        result['message'] = 'Unvalid params: NOT a JSON Object'
        return json.dumps(result)

    # params key checking
    try:
        prob_senzlist = params['probSenzList']
        strategy = params['strategy']
        mutiSenzList_max_num = params.get('mutiMaxNum', 3) 
    except KeyError, err_msg:
        #app.logger.error("[KeyError] can't find key=%s in params=%s" % (err_msg, params))
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

    return json.dumps(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    """
    probSenzList_elem = {
                         "motion": {
                             "Riding": 9.94268884532027e-11,
                             "Walking": 0.8979591835334749,
                             "Running": 0.08163265323813619,
                             "Driving": 0.02040816312895674,
                             "Sitting": 7.69994010250898e-98
                         },
                         "location": {
                             "restaurant": 0.213423,
                             "resident": 0.235434542,
                         },
                         "sound": {
                             "talk":0.234234523454,
                         },
                         "timestamp": 1297923712
                        }
    #senzList_elem_candidate = [{'motion': 'Walking', 'sound': 'talk', 'prob': -3.0053854503466702, 'location': 'resident'}, {'motion': 'Running', 'sound': 'talk', 'prob': -5.5014375304723426, 'location': 'restaurant'}, {'motion': 'Driving', 'sound': 'talk', 'prob': -6.8877319004405226, 'location': 'restaurant'}]
    result = _probSenz_zip_top_N(probSenzList_elem, 3, log(1e-30))
    print result
    """
    """
    data = {
        "probSenzList": [
            {
                "motion": {
                    "Riding": 0.2457,
                    "Walking": 0.2863,
                    "Running": 0.3112,
                    "Driving": 0.1,
                    "Sitting": 0.0577
                },
                "location": {
                    "restaurant": 0.621,
                    "resident": 0.379
                },
                "sound": {
                    "talk": 0.2342,
                    "shot": 0.4321,
                    "sing": 0.3337
                },
                "timestamp": 1297923712
            },

            {
                "motion": {
                    "Riding": 0.2457,
                    "Walking": 0.2863,
                    "Running": 0.3112,
                    "Driving": 0.1,
                    "Sitting": 0.0577
                },
                "location": {
                    "restaurant": 0.621,
                    "resident": 0.379
                },
                "sound": {
                    "talk": 0.2342,
                    "shot": 0.4321,
                    "sing": 0.3337
                },
                "timestamp": 1297923712
            },

            {
                "motion": {
                    "Riding": 0.2457,
                    "Walking": 0.2863,
                    "Running": 0.3112,
                    "Driving": 0.1,
                    "Sitting": 0.0577
                },
                "location": {
                    "restaurant": 0.621,
                    "resident": 0.379
                },
                "sound": {
                    "talk": 0.2342,
                    "shot": 0.4321,
                    "sing": 0.3337
                },
                "timestamp": 1297923712
            },

            {
                "motion": {
                    "Riding": 0.2457,
                    "Walking": 0.2863,
                    "Running": 0.3112,
                    "Driving": 0.1,
                    "Sitting": 0.0577
                },
                "location": {
                    "restaurant": 0.621,
                    "resident": 0.379
                },
                "sound": {
                    "talk": 0.2342,
                    "shot": 0.4321,
                    "sing": 0.3337
                },
                "timestamp": 1297923712
            },
        ],
        "strategy": "SELECT_MAX_PROB"
    }
    print(prob2muti_quick(data['probSenzList'], 3))
    """