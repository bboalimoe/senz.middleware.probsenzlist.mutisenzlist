"""Provide an API to convert probsenzlist to mutisenzlist."""

__author__ = 'jiaying.lu'

from flask import Flask
from flask import json, abort
from numpy import log, array

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
    before_stack = [{'senzList':[e], 'prob':e['prob']} for e in bar[0]]
    after_stack = []
    
    for index in range(1, len(bar)):
        #print('before_stack: ', before_stack)
        #print('after_stack:',  after_stack)
        while before_stack != []:
            stack_elem = before_stack.pop(0)
            for elem in bar[index]:
                stack_elem['senzList'] += [elem]
                stack_elem['prob'] += elem['prob']
                if stack_elem['prob'] > prob_lower_bound:
                    after_stack.append(stack_elem)
        before_stack = after_stack
        after_stack = []

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

    probSenzList_zip = array([_probSenz_zip(elem, prob_lower_bound) for elem in probSenzList])
    #print probSenzList_zip

    mutiSenzList = _ziped2muti(probSenzList_zip, prob_lower_bound)
    # Clean unnecessary elem in mutiSenzList
    for elem in mutiSenzList:
        elem['senzList'].pop('prob')

    return mutiSenzList


@app.route('/mutiSenzList')
@app.route('/mutiSenzList/<params>')
def converter(params=''):
    app.logger.debug('Enter converter(), params: %s' % (params))
    
    # params JSON validate
    try:
        params = json.loads(params)
    except ValueError, err_msg:
        app.logger.error('[ValueError] err_msg: %s, params=%s' % (err_msg, params))
        return abort(400)

    # params key checking
    try:
        probSenzList = array(params['probSenzList'], dtype=float)
        strategy = params['strategy']
    except KeyError, err_msg:
        app.logger.error("[KeyError] can't find key=%s in params=%s" % (err_msg, params))
        return abort(400)
    
    mutiSenzList = prob2muti(probSenzList)
    return json.dumps(mutiSenzList)


if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True)
    """
    probSenzList = [
                       {
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
                        }
                       },
                       {
                        'motion': {'Running':1.29321983128e-8},
                        'location': {'school':3.14},
                        'sound': {'talk': 2.3324e-12},
                       }
                   ]

    prob2muti(probSenzList)
    """
