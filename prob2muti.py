"""Provide an API to convert probsenzlist to mutisenzlist."""

__author__ = 'jiaying.lu'

from flask import Flask
from flask import json, abort
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

def prob2muti(probSenzList, prob_lower_bound=log(1e-8)):
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

    return ['Done']


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
        probSenzList = params['probSenzList']
        strategy = params['strategy']
    except KeyError, err_msg:
        app.logger.error("[KeyError] can't find key=%s in params=%s" % (err_msg, params))
        return abort(400)
    
    mutiSenzList = prob2muti(probSenzList)
    return json.dumps(mutiSenzList)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
