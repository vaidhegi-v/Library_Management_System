from flask import Flask,render_template,request,redirect
import mysql.connector
library=Flask(__name__)
mysql=mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vaiu1@#",
    database="library"
)

cursor=mysql.cursor()

@library.route("/")
def home():
    return render_template("home.html")

@library.route("/Admin",methods=["GET","POST"])
def admin():
    if request.method == "POST":
        admin=request.form["admin"]
        ps=request.form["ps"]
        cursor.execute("select * from admin where admin=%s and password=%s",(admin,ps))
        res1=cursor.fetchone()
        mysql.commit()
        if res1:
            return render_template("output.html",res1=res1)
        else:
            return "Admin name or Password is incorrect"
    return render_template("admin.html")

@library.route("/Add Books",methods=["GET","POST"])
def addbook():
    if request.method == "POST":
        bname=request.form.get("book")
        author=request.form["author"]
        des=request.form.get("des")
        cursor.execute("insert into book(book_name,author,description) values(%s,%s,%s)",(bname,author,des))
        cursor.execute("select book_name from book where book_name=%s and author=%s",(bname,author))
        res2=cursor.fetchone()
        print(res2)
        mysql.commit()
        if res2:
            return render_template("output.html",res2=res2)
    return render_template("add_book.html")

@library.route("/Signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        n=request.form.get("uname")
        e=request.form.get("uemail")
        p=request.form.get("upassword")
        cursor.execute("insert into sign_up(name,email,password) values(%s,%s,%s)",(n,e,p))
        mysql.commit()
        return render_template("sign_com.html")
    return render_template("signup.html")

@library.route("/User")
def user():
    return render_template("user.html")

@library.route("/Login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        em=request.form.get("email")
        pw=request.form.get("password") 
        acard=request.form.get("acard")
        cursor.execute("select email,password from sign_up where email=%s and password=%s",(em,pw))
        result=cursor.fetchone()
        mysql.commit()
        if result:
            cursor.execute("update sign_up set admit_card=%s where email=%s and password=%s",(acard,em,pw))
            return redirect("/User Main")
        else:
            return render_template("logfail.html")
    return render_template("login.html")

@library.route("/User Main")
def usermain():
    return render_template("user_main.html")

@library.route("/Check",methods=["GET","POST"])
def checkbook():
    if request.method == "POST":
        bname=request.form["bname"]
        bauthor=request.form["author"]
        cursor.execute("select * from book where book_name=%s and author=%s",(bname,bauthor))
        res3=cursor.fetchone()
        mysql.commit()
        if res3:
            return render_template("output.html",res3=res3,bname=bname)
    return render_template("check_book.html")

@library.route("/Take",methods=["GET","POST"])
def takebook():
    if request.method == "POST":
        acard=request.form["acard"]
        tbook=request.form["bname"]
        author=request.form["author"]
        date=request.form["tdate"]
        cursor.execute("select book_name,author from book where book_name=%s and author=%s",(tbook,author))
        res4=cursor.fetchone()
        print(res4)
        mysql.commit()
        if res4:
            cursor.execute("delete from book where book_name=%s and author=%s",(tbook,author))
            cursor.execute("insert into user(a_card,bname,author,t_date) values(%s,%s,%s,%s)",
                           (acard,tbook,author,date))
            mysql.commit()
            return render_template("output.html",res4=res4)        
    return render_template("take.html")

@library.route("/Return",methods=["GET","POST"])
def return_book():
    if request.method == "POST":
        acard=request.form["acard"]
        rbook=request.form["bname"]
        author=request.form["author"]
        rdate=request.form["rdate"]
        tdate=request.form["tdate"]
        cursor.execute("select * from user where bname=%s and author=%s",(rbook,author))
        res5=cursor.fetchone()
        print(res5)
        mysql.commit()
        if res5:
            cursor.execute("update user set r_date=%s,today_date=%s where bname=%s and author=%s",(rdate,tdate,rbook,author))
            mysql.commit()
            if rdate>=tdate:
                cursor.execute("insert into book(book_name,author) values(%s,%s)",(rbook,author))
                mysql.commit()
                return "You are return your book"
            else:
                fine=25
                cursor.execute("update user set fine=%s*(select datediff(%s,%s)) where bname=%s and author=%s and a_card=%s",
                               (fine,tdate,rdate,rbook,author,acard))
                cursor.execute("select fine from user where bname=%s and author=%s and a_card=%s",(rbook,author,acard))
                res6=cursor.fetchone()
                fine=res6
                mysql.commit()
                if res6 != "NULL":
                    return render_template("output.html",res6=res6,fine=fine)
    return render_template("return.html")

@library.route("/Check Fine",methods=["GET","POST"])
def check_fine():
    if request.method == "POST":
        acard=request.form.get("acard")
        bname=request.form.get("bname")
        author=request.form.get("author")
        cursor.execute("select fine from user where bname=%s and author=%s and a_card=%s",(bname,author,acard))
        res7=cursor.fetchone()
        mysql.connect()
        if res7 != "NULL":
            return render_template("output.html",res7=res7)
    return render_template("check_fine.html")

@library.route("/Paid",methods=["GET","POST"])
def paid():
    if request.method == "POST":
        bname=request.form.get("bname")
        author=request.form.get("author")
        fine=request.form.get("fine")
        cursor.execute("select fine from user bname=%s and author=%s and a_card=%s",(bname,author,fine))
        res8 = cursor.fetchone()
        mysql.commit()
        if res8 == fine:
            cursor.execute("update user set fine=0 where bname=%s and author=%s",(bname,author))
            return render_template("output.html",res8=res8)
    return render_template()


if __name__ == "__main__":
    library.run(debug=True)

cursor.close()
mysql.close()