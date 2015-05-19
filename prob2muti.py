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
        probSenzList = params['probSenzList']
        strategy = params['strategy']
        mutiSenzList_max_num = params.get('maxNum' ,500) 
    except KeyError, err_msg:
        #app.logger.error("[KeyError] can't find key=%s in params=%s" % (err_msg, params))
        result['message'] = "Params content Error: cant't find key=%s"
        return json.dumps(result)
    
    # TODO: 不同策略不同处理
    #if strategy == 'SELECT_MAX_PROB':
    result['code'] = 0
    result['message'] = 'success'
    mutiSenzList = prob2muti(probSenzList, log(1e-30))
    mutiSenzList = sorted(mutiSenzList, key=lambda elem: elem['prob'], reverse=True)
    result['result'] = mutiSenzList[:mutiSenzList_max_num]

    return json.dumps(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
