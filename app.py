# -*- coding: utf-8 -*-
from mimic import *     #mimic定义了需要使用的class
@app.route('/') # 首页
def Index():
    if session.get("username"):
        return render_template("index.html", username=session.get("username"))
    else:
        return render_template('index.html')
@app.route('/exit') #退出登录
def Exit():
    session.clear()
    return redirect('/')
@app.errorhandler(404)  #404错误时自动导航至首页并报错
def error(error_no):
    flash('您访问的页面不存在！')
    return redirect(url_for('Index'))
@app.route('/home') # 个人中心首页
def Home():
    if session.get("username"):
        now = datetime.utcnow()
        modifyNow = datetime(now.year+150,now.month,now.day,now.hour,now.minute,now.second)
        ts = pd.date_range(end=modifyNow.strftime("%Y-%m-%d"), periods=14)
        tsRange = pd.Series(ts.format())
        psRange = []    #当日在院患者总数
        for i in range(0,14):
            psRange.append(Patients.query.filter().join(Admissions, Admissions.subject_id == Patients.subject_id).filter(
            Admissions.admittime <= tsRange[i],Admissions.dischtime >= tsRange[i]).count())
        patientNow = Patients.query.filter().join(Admissions, Admissions.subject_id == Patients.subject_id).filter(
            Admissions.admittime <= modifyNow,Admissions.dischtime >= modifyNow)
        argsToTrans = {
            'time':modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
            'totalPatientsNum':Patients.query.filter().count(),
            'patientsNow':patientNow,
            'totalPatientsNowNum': patientNow.count(),
            'totalUserNum':User.query.filter().count(),
            'totalDrugNum':Drug.query.filter().count(),
            'username':session.get("username"),
            'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
            'name': User.query.filter(User.username == session.get("username")).first().name,
            'tsRange':tsRange,
            'psRange':psRange
        }
        return render_template('home.html', **argsToTrans)
    else:
        flash('您还未登陆，请登陆后进入个人中心！')
        return redirect('/')

@app.route('/visualize')    #可视化
def Visualize():
    if session.get("username"):
        name = request.args.get('name')
        gender = request.args.get('gender')
        age = request.args.get('age')
        diagnosis = request.args.get('diagnosis')
        now = datetime.utcnow()
        modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
        patientNow = Patients.query.filter().join(Admissions, Admissions.subject_id == Patients.subject_id).filter(Admissions.admittime <= modifyNow, Admissions.dischtime >= modifyNow)
        patientQuery = Patients.query.filter()
        nowYear = datetime.utcnow().year + 150
        if name is None and gender is None and age is None and diagnosis is None:
            pass
        else:
            if name != '':
                patientQuery = Patients.query.filter(Patients.name.like('%' + name + '%'))
            if gender == 'M' or gender == 'F':
                patientQuery = patientQuery.filter_by(gender=gender)
            if age != '':
                patientQuery = patientQuery.filter(or_(
                    and_(
                        Patients.expire_flag == 1,
                        extract('year', Patients.dod) - extract('year', Patients.dob) == int(age)
                    ),
                    and_(
                        Patients.expire_flag == 0,
                        extract('year', Patients.dob) == nowYear - int(age)
                    )
                ))
            if diagnosis != '':
                patientQueryTemp = patientQuery.join(Admissions, Admissions.subject_id == Patients.subject_id).filter(
                    Admissions.diagnosis.like('%' + diagnosis + '%')).all()
                patientQueryList = []
                for patient in patientQueryTemp:
                    patientQueryList.append(patient.subject_id)
                patientQuery = Patients.query.filter(Patients.subject_id.in_(patientQueryList))
        try:
            femalePercent = patientQuery.filter(Patients.gender=='F').count()/patientQuery.count()*100
        except:
            femalePercent = 0 #if patientQuery.count() !=0 else -1
        if patientQuery.count() !=0:
            ageCount = []
            monthCount = []
            for i in list(range(0,16))+list(range(20,31)):
                ageCount.append(patientQuery.filter(or_(
                        and_(
                            Patients.expire_flag == 1,
                            extract('year', Patients.dod) - extract('year', Patients.dob) >= i*10,
                            extract('year', Patients.dod) - extract('year', Patients.dob) < (i + 1) * 10
                        ),
                        and_(
                            Patients.expire_flag == 0,
                            nowYear - extract('year', Patients.dob) >= i*10,
                            nowYear - extract('year', Patients.dob) < (i + 1) * 10
                        )
                    )).count())
            AdmissionsReLoad = aliased(Admissions)
            for i in range(12):
                monthCount.append(patientQuery.join(AdmissionsReLoad, AdmissionsReLoad.subject_id == Patients.subject_id).filter(
                        extract('month', AdmissionsReLoad.admittime)==i+1).count())
            argsToTrans = {
                'time':modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'totalPatientsNum':Patients.query.filter().count(),
                'patientsNow':patientNow,
                'totalPatientsNowNum': patientNow.count(),
                'totalUserNum':User.query.filter().count(),
                'totalDrugNum':Drug.query.filter().count(),
                'username':session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'name': User.query.filter(User.username == session.get("username")).first().name,
                'femalePercent':femalePercent,
                'ageCount':ageCount,
                'monthCount':monthCount
            }
            return render_template('visualize.html', **argsToTrans)
        else:
            flash("由于没有患者符合筛选条件，因此无法进行患者信息可视化统计!")
            return redirect(url_for('Index'))
    else:
        flash('您还未登陆，请登陆后进入个人中心！')
        return redirect('/')
@app.route('/search/user/info')
def SearchUserInfo():
    if session.get("username"):
        now = datetime.utcnow()
        modifyNow = datetime(now.year+150,now.month,now.day,now.hour,now.minute,now.second)
        argsToTrans = {
            'time':modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
            'username':session.get("username"),
            'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
            'userToCheckInfo': User.query.filter(User.username == session.get("username")).first()
        }
        return render_template('search_user_info.html', **argsToTrans)
    else:
        flash('您还未登陆，请登陆后进入个人中心！')
        return redirect('/')
# 用户登录功能
@app.route('/login',methods=['GET','POST'])
def Login():
    if request.method == 'GET':
        # 通过检查session中是否有用户信息判断当前是否登陆
        if 'username' in session:
            return redirect('/')    # 若当前已经登录用户，则去往首页
        else:   # 若没有登录，则判断cookie
            return render_template('login.html')
    else:   # POST method
        username = request.form.get('username')
        password = request.form.get('password')     # 从前端获得用户名及密码信息
        crypto = hashlib.md5()
        crypto.update(password.encode(encoding='utf-8'))
        passwordCrypto = crypto.hexdigest()
        userToLogin = User.query.filter_by(username = username, password = passwordCrypto).first()    # 查询数据库中用户信息
        if userToLogin is not None:    # 如果查询到对应用户信息，则输入正确
            # 声明重定向到首页的对象
            isAdmin = '管理员账户' if userToLogin.isAdmin == 1 else '普通医生账户'
            # 登录成功：先将数据保存进session
            session['username'] = username
            # 判断是否要记住密码
            flash('%s，您好，您已登录成功,您的账户类型为 %s'%(userToLogin.name, isAdmin))
            return redirect(url_for("Index"))
        else:   # 登录失败，则提示用户信息有误，并请用户重新输入
            flash('上次登录时输入的用户名不存在或密码与用户名不匹配，请重新输入信息并登录')
            return redirect(url_for("Index"))

# 搜索药品，路由：localhost:5000/search/drug
@app.route('/search/drug',methods=['GET','POST'])
def SearchDrug(): # 搜索页面展示
    page = int(request.args.get('page', 1))
    drug = request.args.get('drug')
    if request.method == 'POST':
        drug = request.form.get('drug')
        return redirect(url_for('.SearchDrug', drug=drug))
    elif drug is None:
        if session.get("username"):
            paginate = Drug.query.paginate(page, 10)
            drug = paginate.items
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'pagination': paginate,
                'drugs': drug,
                'name': User.query.filter(User.username == session.get("username")).first().name
            }
            return render_template('search_drug.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:
        if session.get("username"):
            page = int(request.args.get('page', 1))
            paginate = Drug.query.filter(Drug.drug.like('%'+drug+'%')).paginate(page, 10)
            drug = paginate.items
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'pagination': paginate,
                'drugs': drug,
                'name': User.query.filter(User.username == session.get("username")).first().name
            }
            return render_template('search_drug.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')

# 管理员后台增加一条药品记录：路由localhost:5000/add/drug,
@app.route('/add/drug',methods=['GET','POST'])
def AddDrug():
    if request.method == 'GET':
        if session.get("username"):
            if User.query.filter(User.username == session.get("username")).first().isAdmin:
                now = datetime.utcnow()
                modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
                argsToTrans = {
                    'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                    'username': session.get("username"),
                    'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                    'name': User.query.filter(User.username == session.get("username")).first().name
                }
                return render_template('add_drug.html', **argsToTrans)
            else:
                flash('非管理员账户只能查询药品信息，不能新增药品信息！')
                return redirect('/')
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:
        drug = request.form.get('drug')
        drug_name_poe = request.form.get('drug_name_poe')
        drug_type = request.form.get('drug_type')
        inventory = request.form.get('inventory')
        drug = Drug(drug=drug, drug_name_poe=drug_name_poe, drug_type=drug_type, inventory=inventory)
        db.session.add(drug)
        db.session.commit()
        return redirect(url_for('SearchDrug'))

# # 搜索医生账户，路由：localhost:5000/search/user
@app.route('/search/user',methods=['GET','POST'])
def SearchUser(): # 搜索页面展示
    if request.method == 'GET':
        if session.get("username"):
            if User.query.filter(User.username == session.get("username")).first().isAdmin:
                page = int(request.args.get('page', 1))
                paginate = User.query.paginate(page, 5)
                user = paginate.items
                now = datetime.utcnow()
                modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
                argsToTrans = {
                    'users': user,
                    'pagination':paginate,
                    'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                    'username': session.get("username"),
                    'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                    'name': User.query.filter(User.username == session.get("username")).first().name
                }
                return render_template('search_user.html', **argsToTrans)
            else:
                flash('非管理员账户不能查询及管理其他医生账户信息！')
                return redirect('/')
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:
        name = request.form.get('name')
        page = int(request.args.get('page', 1))
        userQuery = User.query.filter(User.name.like('%'+name+'%')).paginate(page, 5)
        user = userQuery.items
        now = datetime.utcnow()
        modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
        argsToTrans = {
            'users': user,
            'pagination': userQuery,
            'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
            'username': session.get("username"),
            'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
            'name': User.query.filter(User.username == session.get("username")).first().name
        }
        return render_template('search_user.html', **argsToTrans)
# 搜索患者基本信息，路由：localhost:5000/search/patient
@app.route('/search/patient',methods=['GET','POST'])
def SearchPatient():    # 搜索页面展示
    page = int(request.args.get('page', 1))
    name = request.args.get('name')
    gender = request.args.get('gender')
    age = request.args.get('age')
    diagnosis = request.args.get('diagnosis')
    if request.method == 'POST':
        name = request.form.get('name')
        gender = request.form.get('gender')
        age = request.form.get('age')
        diagnosis = request.form.get('diagnosis')
        return redirect(url_for('.SearchPatient', name=name, gender=gender,age=age,diagnosis=diagnosis))
    elif (name == '' and gender == '' and age == '' and diagnosis == '') or (name is None and gender is None and age is None and diagnosis is None):
        if session.get("username"):
            patientQuery = Patients.query.filter().paginate(page, 10)
            patient = patientQuery.items
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'pagination': patientQuery,
                'patients': patient,
                'Lname': User.query.filter(User.username == session.get("username")).first().name
            }
            return render_template('search_patient.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:
        if session.get("username"):
            page = int(request.args.get('page', 1))
            patientQuery = Patients.query.filter()
            if name != '':
                patientQuery = patientQuery.filter(Patients.name.like('%'+name+'%'))
            if gender == 'M' or gender == 'F':
                patientQuery = patientQuery.filter_by(gender=gender)
            if age != '':
                nowYear = datetime.utcnow().year
                patientQuery = patientQuery.filter(or_(
                    and_(
                        Patients.expire_flag == 1,
                        extract('year', Patients.dod) - extract('year', Patients.dob) == int(age)
                    ),
                    and_(
                        Patients.expire_flag == 0,
                        extract('year', Patients.dob) == nowYear - int(age) + 150
                    )
                ) )
            if diagnosis != '':
                patientQuery = patientQuery.join(Admissions, Admissions.subject_id == Patients.subject_id).filter(Admissions.diagnosis.like('%'+diagnosis+'%'))
                patientQueryList = []
                for patient in patientQuery:
                    patientQueryList.append(patient.subject_id)
                patientQuery = Patients.query.filter(Patients.subject_id.in_(patientQueryList))
            paginate = patientQuery.paginate(page, 10)
            patient = paginate.items
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'timetime': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'pagination': paginate,
                'patients': patient,
                'Lname': User.query.filter(User.username == session.get("username")).first().name
            }
            return render_template('search_patient.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')

# 管理员后台增加一条患者记录：路由localhost:5000/add/patient,
@app.route('/add/patient',methods=['GET','POST'])
def AddPatient():
    if request.method == 'GET':
        if session.get("username"):
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'name': User.query.filter(User.username == session.get("username")).first().name
            }
            return render_template('add_patient.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:
        row_id = Patients.query.filter().count() + 45564
        subject_id = request.form.get('subject_id')
        name = request.form.get('name')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        dod = request.form.get('dod')
        expire_flag = request.form.get('expire_flag')
        patient = Patients(row_id=row_id, subject_id=subject_id, name=name, gender=gender, dob=dob, dod=dod, dod_hosp=dod, dod_ssn=dod, expire_flag=expire_flag)
        db.session.add(patient)
        db.session.commit()
        return redirect(url_for('SearchPatient'))

# 管理员后台增加一条医生账户记录：路由localhost:5000/add/user,
@app.route('/add/user',methods=['GET','POST'])
def AddUser():
    if request.method == 'GET':
        if session.get("username"):
            if User.query.filter(User.username == session.get("username")).first().isAdmin:
                now = datetime.utcnow()
                modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
                argsToTrans = {
                    'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                    'username': session.get("username"),
                    'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                    'name': User.query.filter(User.username == session.get("username")).first().name
                }
                return render_template('add_user.html', **argsToTrans)
            else:
                flash('非管理员账户只能查询药品信息，不能新增药品信息！')
                return redirect('/')
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:
        row_id = User.query.filter().count() + 1
        id = request.form.get('id')
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        passwordConfirm = request.form.get('passwordConfirm')
        if password != passwordConfirm:  # 两次新密码输入不一致
            flash('新密码与确认新密码不一致，请重新输入')
            return redirect(url_for("AddUser"))
        if User.query.filter_by(username=username).first() is not None:
            flash('用户名已存在，请重新输入或前往登录')
            return redirect(url_for("AddUser"))
        if User.query.filter_by(id=id).first() is not None:
            flash('该医生编号已被注册账户，请重新输入或前往登录')
            return redirect(url_for("AddUser"))
        else:
            crypto = hashlib.md5()
            crypto.update(password.encode(encoding='utf-8'))
            passwordCrypto = crypto.hexdigest()
            isAdmin = request.form.get('isAdmin')
            jobTitle = request.form.get('jobTitle')
            sex = request.form.get('sex')
            birthday = request.form.get('birthday')
            user = User(row_id=row_id, id=id, name=name, username=username, password=passwordCrypto, isAdmin=isAdmin, jobTitle=jobTitle, sex=sex, birthday=birthday, telephoneNum=None, wechat=None, mail=None, qq=None)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('SearchUser'))
# 新用户注册
@app.route('/register',methods=['GET','POST'])
def Register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        row_id = User.query.filter().count() + 1
        id = request.form.get('id')
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        passwordConfirm = request.form.get('passwordConfirm')  # 从前端获得用户名及密码信息
        if password != passwordConfirm:  # 两次新密码输入不一致
            flash('新密码与确认新密码不一致，请重新输入')
            return redirect(url_for("Index"))
        if User.query.filter_by(username=username).first() is not None:
            flash('用户名已存在，请重新输入或前往登录')
            return redirect(url_for("Index"))
        if User.query.filter_by(id=id).first() is not None:
            flash('该医生编号已被注册账户，请重新输入或前往登录')
            return redirect(url_for("Index"))
        else:
            crypto = hashlib.md5()
            crypto.update(password.encode(encoding='utf-8'))
            passwordCrypto = crypto.hexdigest()
            jobTitle = request.form.get('jobTitle')
            sex = request.form.get('sex')
            birthday = request.form.get('birthday')
            user = User(row_id=row_id, id=id, name=name, username=username, password=passwordCrypto, isAdmin=0, jobTitle=jobTitle, sex=sex, birthday=birthday, telephoneNum=None, wechat=None, mail=None, qq=None)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            flash('新用户注册成功，快去个人中心看看吧！')
            return redirect(url_for("Index"))
# 用户密码修改功能
@app.route('/modify/user/password',methods=['GET','POST'])
def ChangePassword():
    if request.method == 'GET':
        if session.get("username"):
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'userToCheckInfo': User.query.filter(User.username == session.get("username")).first()
            }
            return render_template('modify_user_password.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:   # POST method
        username = session.get("username")
        oldPassword = request.form.get('oldPassword')
        newPassword = request.form.get('newPassword')
        newPasswordConfirm = request.form.get('newPasswordConfirm')  # 从前端获得用户名及密码信息
        crypto = hashlib.md5()
        crypto.update(oldPassword.encode(encoding='utf-8'))
        oldPasswordCrypto = crypto.hexdigest()
        userToChangePassword = User.query.filter_by(username = username, password = oldPasswordCrypto).first()    # 查询数据库中用户信息
        if userToChangePassword is not None:    # 如果查询到对应用户信息，则输入正确
            if newPassword != newPasswordConfirm:  # 两次新密码输入不一致
                flash('新密码与确认新密码不一致，请重新输入')
                return redirect('/modify/user/password')
            else:
                cryptoNew = hashlib.md5()
                cryptoNew.update(newPassword.encode(encoding='utf-8'))
                newPasswordCrypto = cryptoNew.hexdigest()
                userToChangePassword.password = newPasswordCrypto
                db.session.commit()
                return redirect(url_for('SearchUserInfo'))
        else:   # 验证失败，则提示用户信息有误，并请用户重新输入
            flash('用户名或密码错误，请重新输入')
            return redirect('/modify/user/password')
@app.route('/reset/user/<int:row_id>')
def ResetPassword(row_id):
    userToResetPassword = User.query.filter_by(row_id = row_id).first()
    userToResetPassword.password = 'e10adc3949ba59abbe56e057f20f883e'
    db.session.commit()
    return redirect(url_for('SearchUser'))
# 药品修改功能
@app.route('/modify/drug/<int:id>',methods=['GET','POST'])
def ModifyDrug(id):
    if request.method == 'GET':
        if session.get("username"):
            if User.query.filter(User.username == session.get("username")).first().isAdmin:
                now = datetime.utcnow()
                modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
                argsToTrans = {
                    'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                    'username': session.get("username"),
                    'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                    'drugToCheckInfo': Drug.query.filter(Drug.id == id).first()
                }
                return render_template('modify_drug.html', **argsToTrans)
            else:
                flash('非管理员账户不可使用此功能！')
                return redirect('/')
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:   # POST method
        drugToModify = Drug.query.filter_by(id=id).first()
        drugToModify.drug = request.form.get('drug')
        drugToModify.drug_name_poe = request.form.get('drug_name_poe')
        drugToModify.drug_type = request.form.get('drug_type')
        drugToModify.inventory = request.form.get('inventory')
        db.session.commit()
        return redirect('/modify/drug/'+str(id))

# 账户修改功能
@app.route('/modify/user',methods=['GET','POST'])
def ModifyUser():
    if request.method == 'GET':
        if session.get("username"):
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'userToCheckInfo': User.query.filter(User.username == session.get("username")).first()
            }
            return render_template('modify_user.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:   # POST method
        username = session.get("username")
        userToModify = User.query.filter_by(username=username).first()
        userToModify.name = request.form.get('name')
        userToModify.sex = request.form.get('sex')
        userToModify.birthday = request.form.get('birthday')
        userToModify.telephoneNum = request.form.get('telephoneNum')
        userToModify.wechat = request.form.get('wechat')
        userToModify.mail = request.form.get('mail')
        userToModify.qq = request.form.get('qq')
        db.session.commit()
        return redirect(url_for('SearchUserInfo'))

@app.route('/modify/user/<int:row_id>',methods=['GET','POST'])
def ModifyUserByAdmin(row_id):
    if request.method == 'GET':
        if session.get("username"):
            if User.query.filter(User.username == session.get("username")).first().isAdmin:
                now = datetime.utcnow()
                modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
                argsToTrans = {
                    'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                    'username': session.get("username"),
                    'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                    'userToCheckInfo': User.query.filter(User.row_id == row_id).first()
                }
                return render_template('modify_user_admin.html', **argsToTrans)
            else:
                flash('非管理员账户不可使用此功能！')
                return redirect('/')
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:   # POST method
        userToModify = User.query.filter_by(row_id=row_id).first()
        if request.form.get('name') != userToModify.name and User.query.filter_by(username=request.form.get('name')).first() is not None:
            flash('用户名已存在，请尝试其它用户名')
            return redirect('/modify/user/'+str(row_id))
        if int(request.form.get('id')) != userToModify.id and User.query.filter_by(id=request.form.get('id')).first() is not None:
            flash('医生编号已存在，请尝试分配其它编号')
            return redirect('/modify/user/'+str(row_id))
        userToModify.name = request.form.get('name')
        userToModify.id = request.form.get('id')
        userToModify.username = request.form.get('username')
        userToModify.isAdmin = request.form.get('isAdmin')
        userToModify.jobTitle = request.form.get('jobTitle')
        userToModify.sex = request.form.get('sex')
        userToModify.birthday = request.form.get('birthday')
        userToModify.telephoneNum = request.form.get('telephoneNum')
        userToModify.wechat = request.form.get('wechat')
        userToModify.mail = request.form.get('mail')
        userToModify.qq = request.form.get('qq')
        db.session.commit()
        return redirect('/modify/user/'+str(row_id))

# 删除账户记录
@app.route('/delete/user/<int:row_id>')
def DeleteUser(row_id):
    if session.get("username"):
        if User.query.filter(User.username == session.get("username")).first().isAdmin:
            userToDelete = User.query.filter_by(row_id=row_id).first()
            if userToDelete.username==session.get("username"):
                db.session.delete(userToDelete)
                db.session.commit()
                session.clear()
                flash('您已将之前登陆的账户删除，所以您已经退出系统，请重新登录！')
                return redirect('/')
            else:
                db.session.delete(userToDelete)
                db.session.commit()
                return redirect(url_for('SearchUser'))
        else:
            flash('非管理员账户不可使用此功能！')
            return redirect('/')
    else:
        flash('您还未登陆，请登陆后进入个人中心！')
        return redirect('/')

# 删除药品信息
@app.route('/delete/drug/<int:id>')
def DeleteDrug(id):
    drugToDelete = Drug.query.filter_by(id = id).first()
    db.session.delete(drugToDelete)
    db.session.commit()
    return redirect(url_for('SearchDrug'))

# 患者住院信息搜索
@app.route('/search/patient/admissions/<int:subject_id>')
def SearchPatientAdmissions(subject_id):    # 搜索页面展示
    if session.get("username"):
        now = datetime.utcnow()
        modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)

        patientToSearchAdmissions = db.session.query(Patients.name, Patients.subject_id, Admissions.hadm_id,Admissions.admittime, Admissions.dischtime \
                                                     , Admissions.deathtime, Admissions.admission_type,Admissions.admission_location, Admissions.discharge_location \
                                                     , Admissions.insurance, Admissions.language, Admissions.religion,Admissions.marital_status \
                                                     , Admissions.ethnicity, Admissions.edregtime, Admissions.edouttime,Admissions.diagnosis \
                                                     , Admissions.hospital_expire_flag,Admissions.has_chartevents_data).outerjoin(Patients, Admissions \
                                                                                                .subject_id == Patients.subject_id).filter(
            Admissions.subject_id == '%d' % subject_id)
        nowYear = datetime.utcnow().year + 150
        patientsToShow = Patients.query.filter_by(subject_id=subject_id).first()
        if patientsToShow.expire_flag == '1':
            age = patientsToShow.dod.year - patientsToShow.dob.year
        else:
            age = nowYear - patientsToShow.dob.year
        argsToTrans = {
            'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
            'username': session.get("username"),
            'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
            'name': User.query.filter(User.username == session.get("username")).first().name,
            'patients':patientToSearchAdmissions,
            'patientInfo':Patients.query.filter_by(subject_id=subject_id).first(),
            'age':age,
            'drugs':Drug.query.filter()
        }
        return render_template('search_patient_admissions.html', **argsToTrans)
    else:
        flash('您还未登陆，请登陆后进入个人中心！')
        return redirect('/')

# 患者就诊信息修改
@app.route('/modify/patient/admissions/<int:subject_id>/<int:hadm_id>',methods=['GET','POST'])
def ModifyPatientAdmissions(subject_id,hadm_id):
    if request.method == 'GET':
        if session.get("username"):
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'patientToModify': Admissions.query.filter_by(subject_id=subject_id,hadm_id=hadm_id).first()
            }
            return render_template('modify_patient_admissions.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:   # POST method
        patientToModify = Admissions.query.filter_by(subject_id=subject_id,hadm_id=hadm_id).first()
        patientToModify.admittime = request.form.get('admittime')
        patientToModify.dischtime = request.form.get('dischtime')
        patientToModify.deathtime = request.form.get('deathtime')
        patientToModify.admission_type = request.form.get('admission_type')
        patientToModify.admission_location = request.form.get('admission_location')
        patientToModify.discharge_location = request.form.get('discharge_location')
        patientToModify.insurance = request.form.get('insurance')
        patientToModify.language = request.form.get('language')
        patientToModify.religion = request.form.get('religion')
        patientToModify.marital_status = request.form.get('marital_status')
        patientToModify.ethnicity = request.form.get('ethnicity')
        patientToModify.edregtime = request.form.get('edregtime')
        patientToModify.edouttime = request.form.get('edouttime')
        patientToModify.diagnosis = request.form.get('diagnosis')
        patientToModify.hospital_expire_flag = request.form.get('hospital_expire_flag')
        patientToModify.has_chartevents_data = request.form.get('has_chartevents_data')
        db.session.commit()
        return redirect('/search/patient/admissions/' + str(subject_id))

# 患者基本信息修改
@app.route('/modify/patient/<int:subject_id>',methods=['GET','POST'])
def ModifyPatient(subject_id):
    if request.method == 'GET':
        return render_template('modify_patient.html')
    else:   # POST method
        patientToModify = Patients.query.filter_by(subject_id=subject_id).first()
        if request.form.get('name') != '':
            patientToModify.name = request.form.get('name')
        if request.form.get('gender') != '':
            patientToModify.gender = request.form.get('gender')
        if request.form.get('dob') != '':
            patientToModify.dob = request.form.get('dob')
        if request.form.get('dod') != '' and request.form.get('dod') != 'None':
            patientToModify.dod = request.form.get('dod')
        if request.form.get('dod_hosp') != '':
            patientToModify.dod_hosp = request.form.get('dod_hosp')
        if request.form.get('dod_ssn') != '':
            patientToModify.dod_ssn = request.form.get('dod_ssn')
        if request.form.get('expire_flag') != '':
            patientToModify.expire_flag = request.form.get('expire_flag')
        db.session.commit()
        return redirect('/search/patient/admissions/' + str(subject_id))

# 删除患者信息-级联删除
@app.route('/delete/patient/<int:subject_id>')
def DeletePatient(subject_id):
    patientToDelete = Patients.query.filter_by(subject_id = subject_id).first()
    patientToSearchAdmissions = db.session.query(Patients.subject_id, Admissions.hadm_id).outerjoin(Patients, Admissions.subject_id == Patients.subject_id).filter(
        Admissions.subject_id == '%d' % subject_id)
    for admission in patientToSearchAdmissions.all():
        DeletePatientAdmissions(subject_id, int(admission.hadm_id))
    db.session.delete(patientToDelete)
    db.session.commit()
    return redirect(url_for('SearchPatient'))

# 删除患者接诊信息-级联删除
@app.route('/delete/patient/admissions/<int:subject_id>/<int:hadm_id>')
def DeletePatientAdmissions(subject_id,hadm_id):
    patientAdmissionsToDelete = Admissions.query.filter_by(subject_id = subject_id,hadm_id=hadm_id).first()
    patientToSearchPrescription = db.session.query(Admissions.subject_id, Admissions.hadm_id, Prescription.row_id).outerjoin(Prescription, Admissions \
                                                                                          .hadm_id == Prescription.hadm_id).filter(Prescription.hadm_id == '%d' % hadm_id)
    for prescription in patientToSearchPrescription.all():
        DeletePatientPrescription(subject_id, hadm_id, prescription.row_id)
    patientToSearchLabevents = db.session.query(Admissions.subject_id, Admissions.hadm_id, Labevents.row_id).outerjoin(Labevents,Admissions.hadm_id == Labevents.hadm_id) \
        .filter(Labevents.hadm_id == '%d' % hadm_id)
    for labevent in patientToSearchLabevents.all():
        DeletePatientLabevents(subject_id, hadm_id, labevent.row_id)
    patientToSearchDatatimeevent = db.session.query(Admissions.subject_id, Admissions.hadm_id, Datatimeevent.row_id).outerjoin(Datatimeevent, Admissions \
                                                                                          .hadm_id == Datatimeevent.hadm_id).filter(Datatimeevent.hadm_id == '%d' % hadm_id)
    for datatimeevent in patientToSearchDatatimeevent.all():
        DeletePatientDatatimeevent(subject_id, hadm_id, datatimeevent.row_id)
    patientToSearchCpt = db.session.query(Admissions.subject_id, Admissions.hadm_id,Cpt.row_id).outerjoin(Cpt, Admissions \
                                                                                    .hadm_id == Cpt.hadm_id).filter(Cpt.hadm_id == '%d' % hadm_id)
    for cpt in patientToSearchCpt.all():
        DeletePatientCpt(subject_id, hadm_id, cpt.row_id)
    db.session.delete(patientAdmissionsToDelete)
    db.session.commit()
    return redirect('/search/patient/admissions/' + str(subject_id))

@app.route('/add/patient/admissions/<int:subject_id>',methods=['GET','POST'])
def AddPatientAdmissions(subject_id):
    if request.method == 'GET':
        return render_template('add_patient_admissions.html',subject_id=subject_id)
    else:
        row_id = Admissions.query.filter().count() + 58000
        hadm_id = request.form.get('hadm_id')
        admittime = request.form.get('admittime')
        dischtime = request.form.get('dischtime')
        deathtime = request.form.get('deathtime')
        admission_type = request.form.get('admission_type')
        admission_location = request.form.get('admission_location')
        discharge_location = request.form.get('sedischarge_locationx')
        insurance = request.form.get('insurance')
        language = request.form.get('language')
        religion = request.form.get('religion')
        marital_status = request.form.get('marital_status')
        ethnicity = request.form.get('ethnicity')
        edregtime = request.form.get('edregtime')
        edouttime = request.form.get('edouttime')
        diagnosis = request.form.get('diagnosis')
        hospital_expire_flag = request.form.get('hospital_expire_flag')
        admission = Admissions(row_id=row_id, subject_id=subject_id,hadm_id=hadm_id, admittime=admittime, dischtime=dischtime, deathtime=deathtime, admission_type=admission_type, admission_location=admission_location, discharge_location=discharge_location, insurance=insurance, language=language, religion=religion, marital_status=marital_status, ethnicity=ethnicity, edregtime=edregtime, edouttime=edouttime,diagnosis=diagnosis,hospital_expire_flag=hospital_expire_flag,has_chartevents_data=0)
        db.session.add(admission)
        db.session.commit()
        return redirect('/search/patient/admissions/' + str(subject_id))

# 患者处方信息搜索
@app.route('/search/patient/prescription/<int:subject_id>/<int:hadm_id>')
def SearchPatientPrescription(subject_id, hadm_id):    # 搜索页面展示
    if session.get("username"):
        page = int(request.args.get('page', 1))
        now = datetime.utcnow()
        modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
        patientToSearchPrescription = db.session.query(Admissions.subject_id, Admissions.hadm_id, Prescription.row_id,Prescription.icustay_id \
                                                       , Prescription.startdate, Prescription.enddate,Prescription.drug, Prescription.drug_type \
                                                       , Prescription.drug_name_poe, Prescription.prod_strength,Prescription.dose_val_rx \
                                                       , Prescription.dose_unit_rx, Prescription.form_val_disp,Prescription.form_unit_disp).outerjoin(Prescription, Admissions \
                                                                                              .hadm_id == Prescription.hadm_id).filter(
            Prescription.hadm_id == '%d' % hadm_id).paginate(page, 15)
        patient = patientToSearchPrescription.items
        nowYear = datetime.utcnow().year + 150
        patientsToShow = Patients.query.filter_by(subject_id=subject_id).first()
        if patientsToShow.expire_flag == '1':
            age = patientsToShow.dod.year - patientsToShow.dob.year
        else:
            age = nowYear - patientsToShow.dob.year
        argsToTrans = {
            'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
            'username': session.get("username"),
            'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
            'name': User.query.filter(User.username == session.get("username")).first().name,
            'patients':patient,
            'patientInfo':Patients.query.filter_by(subject_id=subject_id).first(),
            'age':age,
            'pagination': patientToSearchPrescription,
            'hadm_id':hadm_id,
            'subject_id':subject_id
        }
        return render_template('search_patient_admissions_prescription.html', **argsToTrans)
    else:
        flash('您还未登陆，请登陆后进入个人中心！')
        return redirect('/')

@app.route('/add/patient/prescription/<int:subject_id>/<int:hadm_id>',methods=['GET','POST'])
def AddPatientPrescription(subject_id, hadm_id):
    if request.method == 'GET':
        return render_template('add_patient_admissions_prescription.html',hadm_id=hadm_id,subject_id=subject_id)
    else:
        row_id = Prescription.query.filter().count() + 8918924
        icustay_id = request.form.get('icustay_id')
        startdate = request.form.get('startdate')
        enddate = request.form.get('enddate')
        drug = request.form.get('drug')
        drug_type = Drug.query.filter_by(drug=drug).first().drug_type
        drug_name_poe = Drug.query.filter_by(drug=drug).first().drug_name_poe
        Drug.query.filter_by(drug=drug).first().inventory -=1
        drug_name_generic = request.form.get('drug_name_generic')
        formulary_drug_cd = request.form.get('formulary_drug_cd')
        gsn = request.form.get('gsn')
        ndc = request.form.get('ndc')
        prod_strength = request.form.get('prod_strength')
        dose_val_rx = request.form.get('dose_val_rx')
        dose_unit_rx = request.form.get('dose_unit_rx')
        form_val_disp = request.form.get('form_val_disp')
        form_unit_disp = request.form.get('form_unit_disp')
        route = request.form.get('route')
        prescription = Prescription(row_id=row_id, subject_id=subject_id,hadm_id=hadm_id, icustay_id=icustay_id, startdate=startdate, enddate=enddate, drug=drug, drug_type=drug_type, drug_name_poe=drug_name_poe, drug_name_generic=drug_name_generic, formulary_drug_cd=formulary_drug_cd, gsn=gsn, ndc=ndc, prod_strength=prod_strength, dose_val_rx=dose_val_rx, dose_unit_rx=dose_unit_rx,form_val_disp=form_val_disp,form_unit_disp=form_unit_disp,route=route)
        db.session.add(prescription)
        db.session.commit()
        return redirect('/search/patient/prescription/' + str(subject_id) + '/' + str(hadm_id))

@app.route('/modify/patient/prescription/<int:subject_id>/<int:hadm_id>/<int:row_id>',methods=['GET','POST'])
def ModifyPatientPrescription(subject_id,hadm_id,row_id):
    if request.method == 'GET':
        if session.get("username"):
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'prescriptionToCheckInfo': Prescription.query.filter(Prescription.row_id == row_id).first()
            }
            return render_template('modify_patient_admissions_prescription.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:   # POST method
        precriptionToModify = Prescription.query.filter_by(row_id=row_id).first()
        precriptionToModify.icustay_id = request.form.get('icustay_id')
        precriptionToModify.startdate = request.form.get('startdate')
        precriptionToModify.enddate = request.form.get('enddate')
        if request.form.get('drug') != precriptionToModify.drug:
            Drug.query.filter_by(drug=precriptionToModify.drug).first().inventory += 1
            precriptionToModify.drug = request.form.get('drug')
            precriptionToModify.drug_type = Drug.query.filter_by(drug=precriptionToModify.drug).first().drug_type
            precriptionToModify.drug_name_poe = Drug.query.filter_by(drug=precriptionToModify.drug).first().drug_name_poe
            Drug.query.filter_by(drug=precriptionToModify.drug).first().inventory -= 1
        precriptionToModify.drug_name_generic = request.form.get('drug_name_generic')
        precriptionToModify.formulary_drug_cd = request.form.get('formulary_drug_cd')
        precriptionToModify.gsn = request.form.get('gsn')
        precriptionToModify.ndc = request.form.get('ndc')
        precriptionToModify.prod_strength = request.form.get('prod_strength')
        precriptionToModify.dose_val_rx = request.form.get('dose_val_rx')
        precriptionToModify.dose_unit_rx = request.form.get('dose_unit_rx')
        precriptionToModify.form_val_disp = request.form.get('form_val_disp')
        precriptionToModify.form_unit_disp = request.form.get('form_unit_disp')
        precriptionToModify.route = request.form.get('route')
        db.session.commit()
        return redirect('/search/patient/prescription/' + str(subject_id) + '/' + str(hadm_id))

@app.route('/delete/patient/prescription/<int:subject_id>/<int:hadm_id>/<int:row_id>')
def DeletePatientPrescription(subject_id,hadm_id,row_id):
    patientPrescriptionToDelete = Prescription.query.filter_by(row_id = row_id).first()
    Drug.query.filter_by(drug=patientPrescriptionToDelete.drug).first().inventory += 1
    db.session.delete(patientPrescriptionToDelete)
    db.session.commit()
    return redirect('/search/patient/prescription/' + str(subject_id) + '/' + str(hadm_id))

# 患者labevent信息搜索
@app.route('/search/patient/labevents/<int:subject_id>/<int:hadm_id>')
def SearchPatientLabevents(subject_id, hadm_id):    # 搜索页面展示
    if session.get("username"):
        page = int(request.args.get('page', 1))
        now = datetime.utcnow()
        modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
        patientToSearchLabevents = db.session.query(Admissions.subject_id, Admissions.hadm_id, Labevents.row_id,Labevents.itemid \
                                                    , Labevents.charttime, Labevents.value, Labevents.valuenum,Labevents.valueuom \
                                                    , Labevents.flag, DLabitems.label,DLabitems.fluid, DLabitems.category).outerjoin\
            (Labevents,Admissions.hadm_id == Labevents.hadm_id).outerjoin(DLabitems,DLabitems.itemid == Labevents.itemid) \
            .filter(Labevents.hadm_id == '%d' % hadm_id).paginate(page, 15)
        patient = patientToSearchLabevents.items
        nowYear = datetime.utcnow().year + 150
        patientsToShow = Patients.query.filter_by(subject_id=subject_id).first()
        if patientsToShow.expire_flag == '1':
            age = patientsToShow.dod.year - patientsToShow.dob.year
        else:
            age = nowYear - patientsToShow.dob.year
        argsToTrans = {
            'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
            'username': session.get("username"),
            'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
            'name': User.query.filter(User.username == session.get("username")).first().name,
            'patients':patient,
            'patientInfo':Patients.query.filter_by(subject_id=subject_id).first(),
            'age':age,
            'pagination': patientToSearchLabevents,
            'hadm_id':hadm_id,
            'subject_id':subject_id
        }
        return render_template('search_patient_admissions_labevents.html', **argsToTrans)
    else:
        flash('您还未登陆，请登陆后进入个人中心！')
        return redirect('/')

@app.route('/delete/patient/labevents/<int:subject_id>/<int:hadm_id>/<int:row_id>')
def DeletePatientLabevents(subject_id,hadm_id,row_id):
    patientLabeventsToDelete = Labevents.query.filter_by(row_id = row_id).first()
    db.session.delete(patientLabeventsToDelete)
    db.session.commit()
    return redirect('/search/patient/labevents/' + str(subject_id) + '/' + str(hadm_id))

@app.route('/modify/patient/labevents/<int:subject_id>/<int:hadm_id>/<int:row_id>',methods=['GET','POST'])
def ModifyPatientLabevents(subject_id,hadm_id,row_id):
    if request.method == 'GET':
        if session.get("username"):
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'labeventsToCheckInfo': Labevents.query.filter(Labevents.row_id == row_id).first()
            }
            return render_template('modify_patient_admissions_labevents.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:   # POST method
        labeventsToModify = Labevents.query.filter_by(row_id=row_id).first()
        labeventsToModify.itemid = request.form.get('itemid')
        labeventsToModify.charttime = request.form.get('charttime')
        labeventsToModify.value = request.form.get('value')
        try:
            valuenum = float(labeventsToModify.value)
        except:
            labeventsToModify.valuenum = None
        else:
            labeventsToModify.valuenum = valuenum
        labeventsToModify.valueuom = request.form.get('valueuom')
        labeventsToModify.flag = request.form.get('flag')
        db.session.commit()
        return redirect('/search/patient/labevents/' + str(subject_id) + '/' + str(hadm_id))

@app.route('/add/patient/labevents/<int:subject_id>/<int:hadm_id>',methods=['GET','POST'])
def AddPatientLabevents(subject_id, hadm_id):
    if request.method == 'GET':
        return render_template('add_patient_admissions_labevents.html',hadm_id=hadm_id,subject_id=subject_id)
    else:
        row_id = Labevents.query.filter().count() + 39068806
        itemid = request.form.get('itemid')
        charttime = request.form.get('charttime')
        value = request.form.get('value')
        try:
            valueToFloat = float(value)
        except:
            valuenum = None
        else:
            valuenum = valueToFloat
        valueuom = request.form.get('valueuom')
        flag = request.form.get('flag')
        labevents = Labevents(row_id=row_id, subject_id=subject_id,hadm_id=hadm_id, itemid=itemid, charttime=charttime, value=value, valuenum=valuenum, valueuom=valueuom, flag=flag)
        db.session.add(labevents)
        db.session.commit()
        return redirect('/search/patient/labevents/' + str(subject_id) + '/' + str(hadm_id))

# 患者date信息搜索
@app.route('/search/patient/datatimeevent/<int:subject_id>/<int:hadm_id>')
def SearchPatientDatatimeevent(subject_id, hadm_id):    # 搜索页面展示
    if session.get("username"):
        page = int(request.args.get('page', 1))
        now = datetime.utcnow()
        modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
        patientToSearchDatatimeevent = db.session.query(Admissions.subject_id, Admissions.hadm_id, Datatimeevent.row_id,Datatimeevent.icustay_id \
                                                        , Datatimeevent.itemid, Datatimeevent.charttime,Datatimeevent.storetime, Datatimeevent.cgid \
                                                        , Datatimeevent.value, Datatimeevent.valueuom,Datatimeevent.warning \
                                                        , Datatimeevent.error, Datatimeevent.stopped,Datatimeevent.resultstatus).outerjoin(Datatimeevent, Admissions \
                                                                                              .hadm_id == Datatimeevent.hadm_id).filter(Datatimeevent.hadm_id == '%d' % hadm_id).paginate(page, 15)
        patient = patientToSearchDatatimeevent.items
        nowYear = datetime.utcnow().year + 150
        patientsToShow = Patients.query.filter_by(subject_id=subject_id).first()
        if patientsToShow.expire_flag == '1':
            age = patientsToShow.dod.year - patientsToShow.dob.year
        else:
            age = nowYear - patientsToShow.dob.year
        argsToTrans = {
            'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
            'username': session.get("username"),
            'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
            'name': User.query.filter(User.username == session.get("username")).first().name,
            'patients':patient,
            'patientInfo':Patients.query.filter_by(subject_id=subject_id).first(),
            'age':age,
            'pagination': patientToSearchDatatimeevent,
            'hadm_id':hadm_id,
            'subject_id':subject_id
        }
        return render_template('search_patient_admissions_datatimeevent.html', **argsToTrans)
    else:
        flash('您还未登陆，请登陆后进入个人中心！')
        return redirect('/')
@app.route('/add/patient/datatimeevent/<int:subject_id>/<int:hadm_id>',methods=['GET','POST'])
def AddPatientDatatimeevent(subject_id, hadm_id):
    if request.method == 'GET':
        return render_template('add_patient_admissions_datatimeevent.html',hadm_id=hadm_id,subject_id=subject_id)
    else:
        row_id = Prescription.query.filter().count() + 4820591
        itemid = request.form.get('itemid')
        icustay_id = request.form.get('icustay_id')
        charttime = request.form.get('charttime')
        # valueuom = request.form.get('valueuom')
        storetime = request.form.get('storetime')
        cgid = User.query.filter(User.username == session.get("username")).first().id
        # value = request.form.get('value')
        warning = request.form.get('warning')
        error = request.form.get('error')
        stopped = request.form.get('stopped')
        resultstatus = request.form.get('resultstatus')
        datatimeevent = Datatimeevent(row_id=row_id, subject_id=subject_id,hadm_id=hadm_id, itemid=itemid, charttime=charttime, value=charttime, icustay_id=icustay_id, valueuom='Date', storetime=storetime, cgid=cgid, warning=warning, error=error, stopped=stopped, resultstatus=resultstatus)
        db.session.add(datatimeevent)
        db.session.commit()
        return redirect('/search/patient/datatimeevent/' + str(subject_id) + '/' + str(hadm_id))
@app.route('/modify/patient/datatimeevent/<int:subject_id>/<int:hadm_id>/<int:row_id>',methods=['GET','POST'])
def ModifyPatientDatatimeevent(subject_id,hadm_id,row_id):
    if request.method == 'GET':
        if session.get("username"):
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'labeventsToCheckInfo': Datatimeevent.query.filter(Datatimeevent.row_id == row_id).first()
            }
            return render_template('modify_patient_admissions_datatimeevent.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:   # POST method
        datatimeeventToModify = Datatimeevent.query.filter_by(row_id=row_id).first()
        datatimeeventToModify.itemid = request.form.get('itemid')
        datatimeeventToModify.icustay_id = request.form.get('icustay_id')
        datatimeeventToModify.storetime = request.form.get('storetime')
        datatimeeventToModify.charttime = request.form.get('charttime')
        datatimeeventToModify.cgid = User.query.filter(User.username == session.get("username")).first().id
        datatimeeventToModify.warning = request.form.get('warning')
        datatimeeventToModify.error = request.form.get('error')
        datatimeeventToModify.stopped = request.form.get('stopped')
        db.session.commit()
        return redirect('/search/patient/datatimeevent/' + str(subject_id) + '/' + str(hadm_id))
@app.route('/delete/patient/datatimeevent/<int:subject_id>/<int:hadm_id>/<int:row_id>')
def DeletePatientDatatimeevent(subject_id,hadm_id,row_id):
    patientDatatimeeventToDelete = Datatimeevent.query.filter_by(row_id = row_id).first()
    db.session.delete(patientDatatimeeventToDelete)
    db.session.commit()
    return redirect('/search/patient/datatimeevent/' + str(subject_id) + '/' + str(hadm_id))
# 患者date信息搜索
@app.route('/search/patient/cpt/<int:subject_id>/<int:hadm_id>')
def SearchPatientCpt(subject_id, hadm_id):    # 搜索页面展示
    if session.get("username"):
        page = int(request.args.get('page', 1))
        now = datetime.utcnow()
        modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
        patientToSearchCpt = db.session.query(Admissions.subject_id, Admissions.hadm_id, Cpt.row_id,Cpt.chartdate,Cpt.costcenter\
                                                        ,Cpt.cpt_cd,Cpt.cpt_number,Cpt.cpt_suffix,Cpt.description,Cpt.sectionheader\
                                                        ,Cpt.subsectionheader,Cpt.ticket_id_seq).outerjoin(Cpt, Admissions \
                                                                                              .hadm_id == Cpt.hadm_id).filter(Cpt.hadm_id == '%d' % hadm_id).paginate(page, 15)
        patient = patientToSearchCpt.items
        nowYear = datetime.utcnow().year + 150
        patientsToShow = Patients.query.filter_by(subject_id=subject_id).first()
        if patientsToShow.expire_flag == '1':
            age = patientsToShow.dod.year - patientsToShow.dob.year
        else:
            age = nowYear - patientsToShow.dob.year
        argsToTrans = {
            'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
            'username': session.get("username"),
            'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
            'name': User.query.filter(User.username == session.get("username")).first().name,
            'patients':patient,
            'patientInfo':Patients.query.filter_by(subject_id=subject_id).first(),
            'age':age,
            'pagination': patientToSearchCpt,
            'hadm_id':hadm_id,
            'subject_id':subject_id
        }
        return render_template('search_patient_admissions_cpt.html', **argsToTrans)
    else:
        flash('您还未登陆，请登陆后进入个人中心！')
        return redirect('/')
@app.route('/add/patient/cpt/<int:subject_id>/<int:hadm_id>',methods=['GET','POST'])
def AddPatientCpt(subject_id, hadm_id):
    if request.method == 'GET':
        return render_template('add_patient_admissions_cpt.html',hadm_id=hadm_id,subject_id=subject_id)
    else:
        row_id = Cpt.query.filter().count() + 598635
        costcenter = request.form.get('costcenter')
        chartdate = request.form.get('chartdate')
        cpt_cd = request.form.get('cpt_cd')
        ticket_id_seq = request.form.get('ticket_id_seq')
        description = request.form.get('description') if request.form.get('description') is None else 'NULL'
        try:
            cpt_number = int(cpt_cd)
        except:
            cpt_number = int(cpt_cd[:-1])
            cpt_suffix = cpt_cd[-1]
        else:
            cpt_suffix = "NULL"
        sectionheader = DCpt.query.filter(cpt_number>=DCpt.mincodeinsubsection,cpt_number<=DCpt.maxcodeinsubsection).first().sectionheader
        subsectionheader = DCpt.query.filter(cpt_number >= DCpt.mincodeinsubsection,cpt_number <= DCpt.maxcodeinsubsection).first().subsectionheader
        cpt = Cpt(row_id=row_id, subject_id=subject_id,hadm_id=hadm_id, chartdate=chartdate, costcenter=costcenter, cpt_cd=cpt_cd, ticket_id_seq=ticket_id_seq, description=description, cpt_number=cpt_number, cpt_suffix=cpt_suffix, sectionheader=sectionheader, subsectionheader=subsectionheader)
        db.session.add(cpt)
        db.session.commit()
        return redirect('/search/patient/cpt/' + str(subject_id) + '/' + str(hadm_id))
@app.route('/modify/patient/cpt/<int:subject_id>/<int:hadm_id>/<int:row_id>',methods=['GET','POST'])
def ModifyPatientCpt(subject_id,hadm_id,row_id):
    if request.method == 'GET':
        if session.get("username"):
            now = datetime.utcnow()
            modifyNow = datetime(now.year + 150, now.month, now.day, now.hour, now.minute, now.second)
            argsToTrans = {
                'time': modifyNow.strftime("%Y-%m-%d %H:%M:%S"),
                'username': session.get("username"),
                'isAdmin': User.query.filter(User.username == session.get("username")).first().isAdmin,
                'labeventsToCheckInfo': Cpt.query.filter(Cpt.row_id == row_id).first()
            }
            return render_template('modify_patient_admissions_cpt.html', **argsToTrans)
        else:
            flash('您还未登陆，请登陆后进入个人中心！')
            return redirect('/')
    else:   # POST method
        cptToModify = Cpt.query.filter_by(row_id=row_id).first()
        cptToModify.costcenter = request.form.get('costcenter')
        cptToModify.chartdate = request.form.get('chartdate')
        cptToModify.cpt_cd = request.form.get('cpt_cd')
        cptToModify.ticket_id_seq = request.form.get('ticket_id_seq')
        cptToModify.description = request.form.get('description')   # if request.form.get('description') is None else 'NULL'
        try:
            cptToModify.cpt_number = int(cptToModify.cpt_cd)
        except:
            cptToModify.cpt_number = int(cptToModify.cpt_cd[:-1])
            cptToModify.cpt_suffix = cptToModify.cpt_cd[-1]
        else:
            cptToModify.cpt_suffix = "NULL"
        cptToModify.sectionheader = DCpt.query.filter(cptToModify.cpt_number>=DCpt.mincodeinsubsection,cptToModify.cpt_number<=DCpt.maxcodeinsubsection).first().sectionheader
        cptToModify.subsectionheader = DCpt.query.filter(cptToModify.cpt_number>= DCpt.mincodeinsubsection,cptToModify.cpt_number <= DCpt.maxcodeinsubsection).first().subsectionheader
        db.session.commit()
        return redirect('/search/patient/cpt/' + str(subject_id) + '/' + str(hadm_id))
@app.route('/delete/patient/cpt/<int:subject_id>/<int:hadm_id>/<int:row_id>')
def DeletePatientCpt(subject_id,hadm_id,row_id):
    patientCptToDelete = Cpt.query.filter_by(row_id = row_id).first()
    db.session.delete(patientCptToDelete)
    db.session.commit()
    return redirect('/search/patient/cpt/' + str(subject_id) + '/' + str(hadm_id))
# 程序总入口
if __name__ == '__main__':
    app.run(debug=True)