import os
from flask import Flask
from flask import request
from flaskr import Test
import json

from flask import Flask
app = Flask(__name__)

@app.route('/second', methods = ['POST'])
def second():
    if request.method == 'POST':
        formdata = request.form
        best_ind = Test.main(formdata['timeNow'], formdata['truckFullName'])
        print("resultado Algoritmo genetico para el presente")
        print(best_ind)
        return json.dumps(best_ind)
    else:
        return json.dumps('method not allowed!')

app.run(debug=True)