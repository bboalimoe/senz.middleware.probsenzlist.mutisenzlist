"""Provide an API to convert probsenzlist to mutisenzlist."""

__author__ = 'jiaying.lu'

from flask import Flask
from flask import json, abort
from numpy import log

app = Flask(__name__)

def prob2muti(probSenzList, lower_bound=log(1e-8)):
    """
    Convert probSenzList to mutiSenzList

    Args:
        probSenzList: list
        lower_bound: float, should return senz list whose probability is 
                     greater than lower_bound
    Returns:
        mutiSenzList: list
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
