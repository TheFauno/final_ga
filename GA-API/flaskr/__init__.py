#!/usr/bin/python

import os
from flask import Flask
from flask import request
import Test
import CheckAssignment
import json
from waitress import serve
from flask import Flask

app = Flask(__name__)
print(__name__)
@app.route('/', methods = ['POST'])
def second():
    response = {}
    if request.method == 'POST':
        formdata = request.form
        assignment = CheckAssignment.checkAssignment(formdata['truckName'])
        if assignment:
            response["TruckDestination"] = "Input@"+assignment
        else:
            best_ind = Test.main(formdata['requestedTime'], formdata['truckName'])
            response["TruckDestination"] = "Input@"+best_ind[3]
        print(json.dumps(response))
    else:
        response['TruckDestination'] = 'method not allowed'
    return json.dumps(response)

app.run(debug=True, threaded=True)
serve(app, port=8080, host='127.0.0.1')