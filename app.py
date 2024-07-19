from bson import ObjectId
from pymongo import MongoClient
from flask import Flask,render_template,request,session,redirect


cluster=MongoClient('mongodb://127.0.0.1:27017')
db=cluster['donations']
users=db['users']
donation=db['donations']
queue=db['queue']
ad=db['admin']
requests=db['requests']

app=Flask(__name__)

app.secret_key='5000'

@app.route('/')
def land():
    return render_template('land.html')

@app.route('/log')
def log():
    return render_template('login.html')

@app.route('/reg')
def reg():
    return render_template('register.html')

@app.route('/register',methods=['post','get'])
def register():
    username=request.form['username']
    email=request.form['email']
    password=request.form['password']
    confirmpass=request.form['cpassword']
    k={}
    k['username']=username
    k['mail']=email
    k['password']=password 
    k['donations']={}
    res=users.find_one({"username":username})
    mail=users.find_one({"email":email})
    if res:
        return render_template('register.html',status="Username already exists")
    else:
        if mail:
            return render_template('register.html',status='Email already exists')
        elif password != confirmpass:
            return render_template('register.html',status='Passwords do not match')
        elif len(password)<8:
            return render_template('register.html',status="Password must be greater than 7 characters")
        else:
            users.insert_one(k)
            return render_template('register.html',stat="Registration successful")



@app.route('/login',methods=['post','get'])
def login():
    user=request.form['username']
    password=request.form['password']
    res=users.find_one({"username":user})
    if res and dict(res)['password']==password:
        session['name']=user
        return render_template('index.html')
    else:
        return render_template('login.html',status='User does not exist or wrong password')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/ahome')
def ahome():
    return render_template('land.html')

@app.route('/myrequests')
def myrequests():
    data=requests.find({"name":session['name']})
    return render_template('myrequests.html',data=data)

@app.route('/mydonations')
def mydonations():
    data=donation.find({"name":session['name']})
    return render_template('mydonations.html',data=data)

@app.route('/donations')
def donations():
    data=donation.find({"distributed":1})
    return render_template('donations.html',data=data)

@app.route('/donate',methods=['get','post'])
def donate():
    name=request.form['name']
    phone=request.form['phone']
    don=request.form['donation']
    address=request.form['address']
    message=request.form['text']
    donation.insert_one({"name":name,"phone":phone,"donation":don,"address":address,"message":message,"distributed":0,"to":{}})
    return render_template('index.html',status="Thanks for your donation.Our team will collect the donations ASAP")

@app.route('/donationqueue')
def donationqueue():
    data=donation.find({"distributed":0})  
    print(data)  
    return render_template('donationqueue.html',data=data)

@app.route('/dist')
def distr():
    data=request.args['id']
    return render_template('distribute.html',data=data)

@app.route('/distribute',methods=['get','post'])
def dist():
    name=request.args['name']
    phone=request.args['phone']
    don=request.args['donation']
    address=request.args['address']
    id=request.args['id']
    donation.update_one({'_id':ObjectId(id)},{'$set' :{"distributed":1}})
    donation.update_one({'_id':ObjectId(id)},{'$set' :{"to":{"name":name,"phone":phone,"donations":don,"address":address}}})
    return render_template('distribute.html',stat="Distribution successful")

@app.route('/admin')
def admi():
    return render_template('adminlogin.html')

@app.route('/adlog',methods=['get','post'])
def adlog():
    username=request.form['username']
    password=request.form['password']
    res=ad.find_one({"username":username})
    if res and res['password']==password:
        return render_template('adminindex.html')
    else:
        return render_template('adminlogin.html',status='User does not exist or wrong password')


@app.route('/logout')
def logout():
    session['name']=''
    return render_template('land.html')

@app.route('/alogout')
def logou():
    return render_template('land.html')

@app.route('/request',methods=['get','post'])
def req():
    name=request.form['name']
    phone=request.form['phone']
    don=request.form['donation']
    address=request.form['address']
    message=request.form['text']
    requests.insert_one({"name":name,"phone":phone,"donation":don,"address":address,"message":message})
    return render_template('index.html',status="Your request has been submitted successfully")

@app.route('/showrequests')
def showrequests():
    data=requests.find()
    return render_template('requests.html',data=data)

@app.route('/userdonations')
def userdon():
    data=donation.find({"distributed":1})
    return render_template('/userdonations.html',data=data)

@app.route('/adminhome')
def adminhome():
    return render_template('adminindex.html')

@app.route('/admindonations')
def admindonations():
    data=donation.find({"distributed":1})
    return render_template('admindonations.html',data=data)

if __name__=="__main__":
    app.run(debug=True)