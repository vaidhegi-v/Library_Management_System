from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vaiu1@#",
        database="library"
    )

# Reusable query function
def execute_query(query, params=(), fetch_one=False, commit=False):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone() if fetch_one else cursor.fetchall()
    if commit:
        db.commit()
    cursor.close()
    db.close()
    return result

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/Admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        admin = request.form["admin"]
        ps = request.form["ps"]
        res1 = execute_query("SELECT * FROM admin WHERE admin=%s AND password=%s", (admin, ps), fetch_one=True)
        if res1:
            return render_template("output.html", res1=res1)
        else:
            return "Admin name or Password is incorrect"
    return render_template("admin.html")

@app.route("/Add Books", methods=["GET", "POST"])
def addbook():
    if request.method == "POST":
        bname = request.form.get("book")
        author = request.form["author"]
        des = request.form.get("des")
        execute_query("INSERT INTO book(book_name,author,description) VALUES(%s,%s,%s)", (bname, author, des), commit=True)
        res2 = execute_query("SELECT book_name FROM book WHERE book_name=%s AND author=%s", (bname, author), fetch_one=True)
        if res2:
            return render_template("output.html", res2=res2)
    return render_template("add_book.html")

@app.route("/Signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        n = request.form.get("uname")
        e = request.form.get("uemail")
        p = request.form.get("upassword")
        execute_query("INSERT INTO sign_up(name, email, password) VALUES(%s, %s, %s)", (n, e, p), commit=True)
        return render_template("sign_com.html")
    return render_template("signup.html")

@app.route("/User")
def user():
    return render_template("user.html")

@app.route("/Login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        em = request.form.get("email")
        pw = request.form.get("password")
        acard = request.form.get("acard")
        result = execute_query("SELECT email,password FROM sign_up WHERE email=%s AND password=%s", (em, pw), fetch_one=True)
        if result:
            execute_query("UPDATE sign_up SET admit_card=%s WHERE email=%s AND password=%s", (acard, em, pw), commit=True)
            return redirect("/User Main")
        else:
            return render_template("logfail.html")
    return render_template("login.html")

@app.route("/User Main")
def usermain():
    return render_template("user_main.html")

@app.route("/Check", methods=["GET", "POST"])
def checkbook():
    if request.method == "POST":
        bname = request.form["bname"]
        bauthor = request.form["author"]
        res3 = execute_query("SELECT * FROM book WHERE book_name=%s AND author=%s", (bname, bauthor), fetch_one=True)
        if res3:
            return render_template("output.html", res3=res3, bname=bname)
    return render_template("check_book.html")

@app.route("/Take", methods=["GET", "POST"])
def takebook():
    if request.method == "POST":
        acard = request.form["acard"]
        tbook = request.form["bname"]
        author = request.form["author"]
        date = request.form["tdate"]
        res4 = execute_query("SELECT book_name, author FROM book WHERE book_name=%s AND author=%s", (tbook, author), fetch_one=True)
        if res4:
            execute_query("DELETE FROM book WHERE book_name=%s AND author=%s", (tbook, author), commit=True)
            execute_query("INSERT INTO user(a_card, bname, author, t_date) VALUES(%s, %s, %s, %s)", (acard, tbook, author, date), commit=True)
            return render_template("output.html", res4=res4)
    return render_template("take.html")

@app.route("/Return", methods=["GET", "POST"])
def return_book():
    if request.method == "POST":
        acard = request.form["acard"]
        rbook = request.form["bname"]
        author = request.form["author"]
        rdate = request.form["rdate"]
        tdate = request.form["tdate"]
        res5 = execute_query("SELECT * FROM user WHERE bname=%s AND author=%s", (rbook, author), fetch_one=True)
        if res5:
            execute_query("UPDATE user SET r_date=%s, today_date=%s WHERE bname=%s AND author=%s", (rdate, tdate, rbook, author), commit=True)
            if rdate >= tdate:
                execute_query("INSERT INTO book(book_name, author) VALUES(%s, %s)", (rbook, author), commit=True)
                return "You have returned your book"
            else:
                fine = 25
                execute_query("UPDATE user SET fine=%s * (SELECT DATEDIFF(%s, %s)) WHERE bname=%s AND author=%s AND a_card=%s",
                              (fine, tdate, rdate, rbook, author, acard), commit=True)
                res6 = execute_query("SELECT fine FROM user WHERE bname=%s AND author=%s AND a_card=%s", (rbook, author, acard), fetch_one=True)
                if res6:
                    return render_template("output.html", res6=res6, fine=res6)
    return render_template("return.html")

@app.route("/Check Fine", methods=["GET", "POST"])
def check_fine():
    if request.method == "POST":
        acard = request.form.get("acard")
        bname = request.form.get("bname")
        author = request.form.get("author")
        res7 = execute_query("SELECT fine FROM user WHERE bname=%s AND author=%s AND a_card=%s", (bname, author, acard), fetch_one=True)
        if res7:
            return render_template("output.html", res7=res7)
    return render_template("check_fine.html")

@app.route("/Paid", methods=["GET", "POST"])
def paid():
    if request.method == "POST":
        bname = request.form.get("bname")
        author = request.form.get("author")
        fine = request.form.get("fine")
        res8 = execute_query("SELECT fine FROM user WHERE bname=%s AND author=%s", (bname, author), fetch_one=True)
        if res8 == fine:
            execute_query("UPDATE user SET fine=0 WHERE bname=%s AND author=%s", (bname, author), commit=True)
            return render_template("output.html", res8=res8)
    return render_template("paid.html")

if __name__ == "__main__":
    app.run(debug=True)
