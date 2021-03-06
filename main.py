from flask import Flask,redirect,url_for,flash,session
from flask import render_template
from flask import request
from flask_session import Session

import fix_path

from models.users import User
from models.machines import Machine
from models.schedules import Schedule
from models import baseModel as bm

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
app.secret_key = 'key'
Session(app)
@app.route('/')
def index():
	incorrectLogin = False
	error = ""
	print(len(request.args))
	if len(request.args) > 0:
		incorrectLogin = request.args['incorrectLogin']
		return render_template("index.html",incorrectLogin=incorrectLogin,error = request.args['error'])
	else:
		return render_template("index.html")

#placeholder function
@app.route('/sign_up',methods=['GET','POST'])
def sign_up():
	if request.method == 'GET':
		return redirect(url_for('index',incorrectLogin=False,error = "Access Denied"))
	error = None
	if request.method == "POST":
		res = None
		
		user = User(request.form["uni"],request.form["email"], request.form["psw"]	)
		res = user.addUser()

		if res != True:
			# print("error")
			# print(res)
			return redirect(url_for("index",error=res,incorrectLogin=True))
		elif res is True:
			# print("added user")

			uid = user.getIDFromName(request.form["uni"])
			session['uid'] = uid
			user.db_close()
			mg = Machine(bm.Base_Model())
			machines = mg.get_all_machines()
			return render_template("LoggedInUsers.html",error=error,machines=machines)
		else:
			user.db_close()
			error = "server error"
			return redirect(url_for("index",error=error,incorrectLogin=False))

@app.route("/login",methods =['POST','GET'])
def login():
	if request.method == 'GET':
		return redirect(url_for('index',incorrectLogin=False,error = "Access Denied"))
	if request.method == 'POST':
		try:
			#print(request.form['uni'])
			user = User(request.form["uni"],None,request.form["psw"])
			res = user.findUser()
			pwd = user.getPwd()
			user.db_close()
		
			if res[0] is True and pwd == request.form['psw']:
				# print("res")
				# print(res[1])
				session['uid'] = res[1]
				
				return redirect(url_for("LoggedInUsers"))
			else:
				error = "invalid username/password"
				return redirect(url_for("index",incorrectLogin=True,error="incorrect username/password"))
		except Exception as e:
			print(e)
			return redirect(url_for("index"))


	#return render_template("login.html",error=error)


@app.route('/machine_schedule')
def machine_schedule():
	#machine = Machine()
	#machine.get_all_machines()
	return render_template("machineDayschedule.html")

@app.route('/overall_schedule')
def overall_schedule():
	return render_template("overallDaySchedule.html")

@app.route('/LoggedInUsers')
def LoggedInUsers():

	if 'uid' not in session:
		return redirect(url_for('index',incorrectLogin=False,error = "please login to access this page"))
	else:
		if(session['uid'] == None):
			return redirect(url_for('index',incorrectLogin=False,error = "please login to access this page"))

	mg = Machine(bm.Base_Model())

	dicts = mg.get_machine_schedule_dictionaries()
	#print(dicts)
	tr11times = ["08:00 - 08:30", "14:30 - 15:00"]
	tr12times = ["08:00 - 08:30", "14:30 - 15:00"]
	tr13times = ["08:00 - 08:30", "14:30 - 15:00"]


	s = Schedule()
	ret = s.get_user_schedule(session["uid"])
	s.db_close()
	mg.db_close()
	print("err")
	print('err' in request.args)
	if 'err' in request.args:
		return render_template("LoggedInUsers.html", machines=dicts, nextWorkout=ret,uid=session['uid'],err=request.args['err'])
	else:
		return render_template("LoggedInUsers.html", machines=dicts, nextWorkout=ret,uid=session['uid'])


@app.route('/incorrectLogin')
def incorrectLogin():
	if request.method == 'GET':
		return redirect(url_for('index',incorrectLogin=False,error = "Access Denied"))
	if request.method == "POST":
		user = User(request.form["uni"],request.form["email"],request.form["psw"])
		res = user.findUser()

		user.db_close()

		if res is 1:
			return render_template("LoggedInUsers.html",error=error)
		else:
			error = "invalid username/password"
			return render_template("incorrectLogin.html",error=error)

@app.route('/scheduleWorkout',methods=['GET','POST'])
def scheduleWorkout():
	if request.method == 'GET':
		return redirect(url_for('index',incorrectLogin=False,error = "Access Denied"))
	if 'uid' not in session:
		return redirect(url_for('index',incorrectLogin=False,error = "please login to access this page"))
	else:
		if(session['uid'] == None):
			return redirect(url_for('index',incorrectLogin=False,error = "please login to access this page"))
	s = Schedule()
	u = User()
	m = Machine(bm.Base_Model())
	try:
		workoutTime = request.form[("time")]
		mid = request.form['optradio']
		mid = int(mid)

		#name = u.getNameFromID(uni)
		uid = session['uid']
		mType = m.getTypeFromID(mid)

		# print(uid)
		# print("w is:")

		success = s.make_reservation(workoutTime,uid,mid)
		if success == True:
			return redirect(url_for("scheduleSuccess",mType=mType,workoutTime=workoutTime,mid=mid))
		else:
			# print("error")
			return redirect(url_for("index",incorrectLogin = False,error = "reservation failed"))
	except Exception as e:
		print(e)
		return redirect(url_for("index",incorrectLogin = False,error = "server error"))
	#s.makeReservation()

@app.route('/gymSchedule',methods=['GET','POST'])
def gymSchedule():
	s = Schedule()
	ret = s.get_all_appointments()
	return render_template("gymSchedule.html",workouts = ret)


@app.route('/cancelSuccess')
def cancelSuccess():
    return render_template("cancelSuccess.html")

@app.route('/scheduleSuccess',methods=['POST','GET'])
def scheduleSuccess():
	if request.method == 'GET':
		
		mType = request.args['mType']
		workoutTime = request.args['workoutTime']
		mid = request.args['mid']
		
		return render_template("scheduleSuccess.html",mType=mType,workoutTime=workoutTime,mid=mid)

	if request.method == 'POST':
		return redirect(url_for('index',incorrectLogin=False,error = "Access Denied"))



@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/cancelWorkout',methods=['GET','POST'])
def cancelWorkout():
	if request.method == 'GET':
		return redirect(url_for('index',incorrectLogin=False,error = "Access Denied"))
	if 'uid' not in session:
		return redirect(url_for('index',incorrectLogin=False,error = "please login to access this page"))
	else:
		if(session['uid'] == None):
			return redirect(url_for('index',incorrectLogin=False,error = "please login to access this page"))
	try:
		s = Schedule()
		u = User()

		uid = session['uid']
		workoutExists = True
		nextWorkout = s.get_user_schedule(uid)#["Treadmill", "tr11", "14:00 - 14:30", "sk4120"]
		print(nextWorkout)
		if nextWorkout == None:
			print("no workouts")
			return redirect(url_for('LoggedInUsers',err="you have no workouts scheduled"))
		nextWorkout = nextWorkout[0]

		print(nextWorkout)
		# nextWorkout.append(uni)
		print(nextWorkout)
		if nextWorkout is not None:
			s.cancel_reservation(uid,nextWorkout[1])

			return render_template("cancelWorkout.html", nextWorkout=nextWorkout,workoutExists = workoutExists)
		else:
			return redirect(url_for('index',incorrectLogin=False,error = "server error. Please try again"))

	except Exception as e:
		print(e)

		return redirect(url_for('index',incorrectLogin=False,error = "server error. Please try again"))
@app.route('/logout')
def logout():
	print("logout")
	session["uid"] = None
	return redirect(url_for("index",error="logged out successfuly",incorrectLogin=True))


if __name__ == '__main__':
	try:
	  import googleclouddebugger
	  googleclouddebugger.enable()
	except ImportError:
	  pass

	app.run(debug=True)
