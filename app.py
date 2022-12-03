from flask import Flask,render_template,request

app = Flask(__name__)

import recommender_system

@app.route('/', methods = ['POST','GET'])
def home():
    if request.method =="POST":
        song = request.form['song']
        year = request.form['year']
        year=int(year)
        song1 = recommender_system.recommender([{'name':song, 'year': year}])
        return render_template('base.html',song1=song1,year=year)
    else:
        return render_template('base.html')
 
if __name__== "__main__":
    app.run(debug=True)