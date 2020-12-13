from flask import session, Blueprint, request, render_template, flash, redirect, url_for
import datetime
from app.module import dbModule

main = Blueprint('main', __name__, url_prefix='/')


@main.route('/', methods=['GET'])
def index():
    chk = True
    db_class = dbModule.Database()
    sql = "SELECT * FROM movie"
    db_class.execute(sql)
    entmovie = db_class.cursor.fetchall()

    return render_template('/main/index.html',entmovie=entmovie,initstate=chk)


@main.route('/mypage', methods=['GET'])
def mypage():
    if 'user' in session:
         chk = True
         db_class = dbModule.Database()
         sql = "select account_num, account_type, account_crdate \
         from customer \
         where customer_id='%s'" % session['user']
         db_class.execute(sql)
         accinfo = db_class.cursor.fetchall()
         sql = "select M.movie_name, M.movie_type, M.number_of_copy, M.rating, M.movie_id \
from ORDER_DATA O, CUSTOMER C, MOVIE M \
where O.customer_id=C.customer_id and C.customer_id='%s' and O.movie_id=M.movie_id and O.return_time is null"%session['user']
         db_class.execute(sql)
         ordmovie = db_class.cursor.fetchall()
         sql = "select M.movie_name, M.movie_type, M.number_of_copy, M.rating \
from customer C, movie M, queue Q \
where C.customer_id='%s' and C.customer_id=Q.customer_id and M.movie_id=Q.movie_id"%session['user']
         db_class.execute(sql)
         movieque = db_class.cursor.fetchall()

         return render_template('/main/index.html', ordmovie=ordmovie, movieque=movieque, accinfo=accinfo, fbtn=chk)

    else:
        return render_template('/main/login.html')


@main.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('/main/login.html')
    else:
        db_class = dbModule.Database()
        incid = request.form['cid']
        sql = "select customer_id from customer where customer_id='%s'"%incid
        db_class.execute(sql)
        tmp = db_class.cursor.fetchall()
        if tmp:
            session['user'] = incid
        else:
            return '''
            <script> alert("로그인 실패...")</script>'''
        return redirect('/')


@main.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@main.route('/rate', methods=['POST'])
def rate():
    db_class = dbModule.Database()
    rtmovie = request.form["test"]
    sql = "select order_id from order_data where customer_id='%s' \
          and movie_id='%s'"%(session['user'],rtmovie)
    db_class.execute(sql)
    cusorder = db_class.cursor.fetchall()
    orid = cusorder[0]['order_id']
    print(orid)
    sql = "UPDATE DBProject.order_data \
           SET cusmov_rating = %d \
          WHERE order_id='%s'"%(int(request.form['rating']), orid)
    db_class.execute(sql)
    db_class.commit()

    return redirect('/mypage')


@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template("/main/search.html")
    else :
        db_class = dbModule.Database()
        mvtype = request.form["mtype"]
        print(mvtype)
        sql = "select movie_name, movie_type, number_of_copy, rating \
        from movie \
        where movie_type='%s'"%mvtype
        db_class.execute(sql)
        fbtmovie = db_class.cursor.fetchall()

        return render_template('/main/search.html',fbtmovie=fbtmovie)


@main.route('/searchw', methods=['POST'])
def searchw():
    db_class = dbModule.Database()
    mvword = request.form["wtext"].split(",")
    sql = []
    print(mvword)
    if (len(mvword) == 1):
        sql = "select movie_name, movie_type, number_of_copy, rating\
                      from movie\
                      where movie_name like '%%" + mvword[0] + "%%'"
    else:
        sql = "select movie_name, movie_type, number_of_copy, rating\
                              from movie\
                              where movie_name like '%%" + mvword[0] + "%%' \
                              and movie_name like '%%" + mvword[1] + "%%'"
    db_class.execute(sql)
    fbwmovie = db_class.cursor.fetchall()
    return render_template('/main/search.html', fbwmovie=fbwmovie)


@main.route('/searcha',methods=['POST'])
def searcha():
    db_class = dbModule.Database()
    mvactor = request.form["actors"].split(',')
    if (len(mvactor) == 1):
        sql = "select M.movie_name, M.movie_type, M.number_of_copy, M.rating\
                from movie M, character_list CL, actor A \
                where CL.actor_id=A.actor_id and CL.movie_id=M.movie_id \
                and A.actor_name='%s'" % mvactor[0]

    else:
        sql = "select M.movie_name, M.movie_type, M.number_of_copy, M.rating \
                    from movie M, character_list L1, character_list L2, actor A1, actor A2 \
                    where M.movie_id=L1.movie_id and M.movie_id=L2.movie_id and \
                    L1.actor_id=A1.actor_id and A1.actor_name='%s' and \
                    L2.actor_id=A2.actor_id and A2.actor_name='%s'" % (mvactor[0], mvactor[1])

    db_class.execute(sql)
    fbamovie = db_class.cursor.fetchall()
    return render_template('/main/search.html', fbamovie=fbamovie)


@main.route('/recommendation', methods=['GET'])
def recommendation():
    if 'user' in session:
        db_class = dbModule.Database()
        sql = "select * \
        from movie \
        where number_of_copy>2 order by number_of_copy desc"
        db_class.execute(sql)
        bstmovie = db_class.cursor.fetchall()
        print(bstmovie)

        sql = "CREATE VIEW typeview as \
    select M.movie_type, count(*) \
    from movie M, order_data O \
    where O.customer_id='%s' and O.movie_id=M.movie_id group by movie_type order by count(*) desc"%session['user']
        db_class.execute(sql)

        sql = "select * from typeview"
        db_class.execute(sql)
        tmp = db_class.cursor.fetchall()
        print(tmp)
        sql = "select M.movie_name, M.movie_type, M.number_of_copy, M.rating \
    from movie M \
    where M.movie_type=(select movie_type from typeview limit 1) \
    and M.movie_id not in(select O.movie_id from ORDER_DATA O where O.customer_id='%s')"%session['user']
        db_class.execute(sql)
        permovie = db_class.cursor.fetchall()
        print(permovie)

        sql = "drop view typeview"
        db_class.execute(sql)
        db_class.commit()

        return render_template('/main/recommendation.html',bstmovie=bstmovie,permovie=permovie)

    else :
        return render_template('/main/login.html')

# 입력
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('/main/register.html')
    else:
        db_class = dbModule.Database()
        cid = request.form['cid']
        lname = request.form['lname']
        fname = request.form['fname']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        telephone = request.form['telephone']
        eaddress = request.form['eaddress']
        cardnum = request.form['cardnum']
        crating = request.form['crating']
        accnum = request.form['accnum']
        atype = request.form['atype']
        crdate = datetime.datetime.now().strftime("%Y-%m-%d")
        sql = "INSERT INTO DBProject.customer(customer_id, Lname, Fname, address, city, \
state, zipcode, telephone, Email_address, card_num, rating, account_num, \
account_type, account_crdate) \
VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s','%s', '%s', '%d', '%d', '%s', '%s')"%(cid,lname,fname,address,city,state,int(zipcode),telephone,eaddress,cardnum,int(crating),int(accnum),atype,crdate)

        db_class.execute(sql)
        db_class.commit()
        return redirect('/')