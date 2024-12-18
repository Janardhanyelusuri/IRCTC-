from flask import Flask,render_template,request,flash,session,redirect,url_for
import mysql.connector
from otp import genotp
from cmail import sendmail
import os
import razorpay

RAZORPAY_KEY_ID = 'rzp_test_x3klII7JCQkyBJ'
RAZORPAY_KEY_SECRET ='T4zPh7WIKk8UxEkzWOSW4azc'
client = razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))

mydb=mysql.connector.connect(
    host='localhost',
    user='root',
    password='Frds@1234',
    database='ticket_booking'
)
app=Flask(__name__)
app.secret_key='hfbfe78hjefk'



@app.route('/')
def homepage():
    return render_template('index.html')

#admin------------

@app.route('/adminpage')
def adminpage():
    username=session.get('admin')
    if username:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM signup")
        users = cursor.fetchall()
        return render_template('adminpage.html',username=username,users=users)
    return render_template('adminlogin.html')

@app.route('/adminregister',methods=['GET','POST'])
def adminregister():
    if request.method=="POST":
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        password=request.form['password'] 
        cursor=mydb.cursor()
        cursor.execute('select email from admin')
        data=cursor.fetchall()
        cursor.execute('select mobile from admin')
        edata=cursor.fetchall()
        if(mobile,) in edata:
            flash('User already exist')
            return render_template('adminregister.html')
        if(email,)in data:
            flash('Email address already exists')
            return render_template('adminregister.html')
        cursor.close()
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(email,subject,body)
        return render_template('adminotp.html',otp=otp,name=name,mobile=mobile,email=email,password=password)
    else:
        return render_template('adminregister.html')
    
@app.route('/adminotp/<otp>/<name>/<mobile>/<email>/<password>',methods=['GET','POST'])
def adminotp(otp,name,mobile,email,password):
    if request.method=="POST":
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mydb.cursor()
            lst=[name,mobile,email,password]
            query='insert into admin values(%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mydb.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('agentlogin'))
        else:
            flash('Wrong otp')
            return render_template('adminotp.html',otp=otp,name=name,mobile=mobile,email=email,password=password)
@app.route('/agentlogin',methods=['GET','POST'])
def adminlogin():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor()
        cursor.execute('select count(*) from admin where name=%s \
        and password=%s',[username,password])
        count=cursor.fetchone()[0]
        print(count)
        if count==0:
            flash('Invalid email or password')
            return render_template('agentlogin.html')
        else:
            session['admin']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for('adminpage'))
    return render_template('agentlogin.html')

@app.route('/adminlogout')
def adminlogout():
    if session.get('admin'):
        session.pop('admin')
        return redirect(url_for('adminlogin'))
    else:
        flash('already logged out!')
        return redirect(url_for('adminlogin'))



#usrer-----------


@app.route('/userpage')
def userpage():
    username=session.get('email')
    if username:
        cursor = mydb.cursor()
        cursor.execute('select * from addition')
        items = cursor.fetchall()
        session['items']=items
        return render_template('userpage.html')
    return render_template('login.html',loginfirst='* Please login first ')

@app.route('/register',methods=['GET','POST'])

def register():
    if request.method=="POST":
        fname=request.form['fname']
        lname=request.form['lname']
        dob=request.form['dob']
        mobile=request.form['mobile']
        email=request.form['email']
        password=request.form['password'] 
        cursor=mydb.cursor()
        cursor.execute('select email from register')
        data=cursor.fetchall()
        cursor.execute('select mobilenumber from register')
        edata=cursor.fetchall()
        if(mobile,) in edata:
            flash('User already exist')
            return render_template('register.html')
        if(email,)in data:
            flash('Email address already exists')
            return render_template('register.html')
        cursor.close()
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(email,subject,body)
        print(otp)
        return render_template('otp.html',otp=otp,email=email,password=password,lname=lname,fname=fname,mobile=mobile,dob=dob)
    else:
        return render_template('register.html')
@app.route('/otp/<otp>/<fname>/<lname>/<dob>/<mobile>/<email>/<password>',methods=['GET','POST'])

def otp(otp,fname,lname,dob,mobile,email,password):
    if request.method=="POST":
        uotp=request.form['uotp']
        if otp==uotp:
            cursor=mydb.cursor()
            lst=[fname,lname,dob,email,mobile,password]
            query='insert into register (fname,lname,dob,email,mobilenumber,password)values(%s,%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mydb.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,fname=fname,lname=lname,dob=dob,mobile=mobile,email=email,password=password,wrong='entered otp wrong, please renter')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        cursor=mydb.cursor()
        cursor.execute('select count(*) from register where email=%s \
        and password=%s',[email,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid email or password')
            return render_template('login.html',loginfirst='* email or password wrong')
        else:
            session['email']=email
            if not session.get(email):
                session[email]={}
            return render_template('selectdestination.html')
    return render_template('login.html')

@app.route('/selectdestination',methods=["GET",'POST'])

def selectdestination():
    email = session.get('email')
    if email:
        if request.method=="POST":
            frm=request.form.get('frm')
            to=request.form.get('to')
            date = request.form.get('date')
            if frm and to and date:
                print(date)
                frm,to = frm.split(),to.split()
                dest = abs(int(frm[0])-int(to[0]))
                if dest>=1:
                    price = dest*150
                    return render_template('bookconfirm.html',price=price,frm=frm[-1],to=to[-1],date=date)
                else:
                    return render_template('selectdestination.html',wrong='* destination wrong')
            return render_template('selectdestination.html',wrong='* select proper details')
    return render_template('login.html',loginfirst='*login first')

@app.route('/logout')
def logout():
    if session.get('email'):
        session.pop('email',None)
        return redirect(url_for('login'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))
    

        
#payement
        
@app.route('/pay/<frm>/<to>/<date>/<int:price>', methods=['POST'])
def pay(frm,to,date,price):
    try:
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        # Create Razorpay order
        order = client.order.create({
            'amount': price*100,
            'currency': 'INR',
            'payment_capture': '1'
        })

        print(f"Order created: {order}")
        return render_template('pay.html', order=order,frm=frm,to=to,date=date,name=name,age=age,gender=gender,price=price)
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        return str(e), 400



@app.route('/success',methods=['POST'])

def success():
    email = session.get('email')
    if email:
        payment_id=request.form.get('razorpay_payment_id')
        order_id=request.form.get('razorpay_order_id')
        signature=request.form.get('razorpay_signature')
        name=request.form.get('name')
        age=request.form.get('age')
        gender=request.form.get('gender')
        frm =request.form.get('frm')
        to=request.form.get('to')
        price=request.form.get('price')
        date=request.form.get('date')

        params_dict={
            'razorpay_order_id':order_id,
            'razorpay_payment_id':payment_id,
            'razorpay_signature':signature
        }
        try:
            client.utility.verify_payment_signature(params_dict)
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into tickets(email,name,age,gender,frm,destination,travel_date,price) values(%s,%s,%s,%s,%s,%s,%s,%s)',[email,name,age,gender,frm,to,date,price])
            mydb.commit()
            cursor.close()
            subject= "Ticket Booked Successfully"
            body = f"Dear {name},\n\nYour ticket has been booked successfully.\n\nThank you \n\nname : {name}\n\nage : {age}\n\ngender : {gender}\n\ndate : {date}\n\nRoute : {frm}-{to}\n\nprice : ₹ {price} paid "
            sendmail('18072ec057@gmail.com',subject,body)
            sendmail('gnithin2k@yahoo.com',subject,body)
            flash('Order Placed Sucessfully')
            return redirect(url_for('tickets'))
        except razorpay.errors.SignatureVerificationError:
            return 'Payment verification failed!',400
    else:
        return redirect(url_for('login'))
    
@app.route('/tickets')
def tickets():
    if session.get('email'):
        email=session.get('email')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from tickets where email=%s',[email])
        data=cursor.fetchall()
        cursor.close()
        print (data,'qe')
        return render_template('tickets.html',data=data,ticket='Your ticket has been booked successfully,sent to your mail')
        
    else:
        return redirect(url_for('login'))

        
app.run(debug=True,use_reloader=True)