import os
from flask import Flask
from flask import request
from flaskr import First_ga
from flaskr import Second_ga
from flaskr import Test
import json
#import Generate_ga

from flask import Flask
app = Flask(__name__)

@app.route('/first_ga', methods = ['POST'])
def first_ga():

    if request.method == 'POST':
        #enviar tiempo actual al constructor de la clase para sumarlo
        formdata = request.form
        fga = First_ga.First_ga(formdata)
        data = fga.createGA()
        del fga
        return json.dumps(data)
    else:
        return json.dumps('method not allowed!')

@app.route('/second_ga', methods = ['POST'])
def second_ga():
    #ejecutar segundo caso AG
    if request.method == 'POST':
        formdata = request.form
        sga = Second_ga.Second_ga(formdata)
        data = sga.createGA()
        del sga
        return json.dumps(data)
    else:
        return json.dumps('method not allowed!')
'''
@app.route('/test', methods = ['GET'])
def test():
    #ejecutar segundo caso AG
    if request.method == 'GET':
        test = Test.Test()
        data = test.main()
        del test
        return json.dumps(data)
    else:
        return json.dumps('method not allowed!')
'''
app.run(debug=True)