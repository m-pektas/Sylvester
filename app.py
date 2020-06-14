from flask import Flask,render_template,request
from DataHandling import checkAccount

#DB
charts = { "wordcount": "../static/db/wordcount.png",
           "emotions" : "../static/db/wordcount.png"}

app = Flask('__name__')


@app.route("/")
@app.route("/index/")
def main():
    return render_template('index.html')


@app.route("/personal_analysis/",methods=['POST'])
def personal_analysis():    
    
    Username = request.form['username']
    check, info = checkAccount(username=Username)
    if check:
        return render_template('personal_analysis.html',username=Username,info = info,charts=charts)
    else:
        return render_template('not_found.html')


if __name__ == "__main__":
    app.debug = True
    app.run()
    