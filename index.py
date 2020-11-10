# Importing elements from flask
from flask import Flask, render_template, redirect, request, url_for, session
# Importing the Python date module
from datetime import datetime, date, timedelta
import sqlite3 as s
import sys
# Importing the BeatifulSoup module
from bs4 import BeautifulSoup
import requests
app = Flask(__name__, static_folder='static')  
# Super secret key
app.secret_key = "super secret key"
# Database file
DB_FILE = 'mydb.db'    	
# Connecting to the database	
connection = s.connect(DB_FILE, check_same_thread=False)

# Creating a class with functions
class Insert:
        def weatherTable(var1, var2):
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("insert into weather VALUES (:date, :temp)", (var1,var2))
                connection.commit()
                cursor.close()
        def coronaTable(var1, var2, var3):
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("insert into virus VALUES (:total, :deaths, :recovered)", (var1,var2,var3))
                connection.commit()
                cursor.close()

# Page route for index
@app.route("/")
def index():
        try:
                # Retrieving Dubai's weather
                website = requests.get("https://www.bbc.com/weather/292223")
                soup = BeautifulSoup(website.content, 'html.parser')
                timeDiv = soup.find("span", class_ = "wr-c-observations__timestamp gel-long-primer gs-u-mt--")
                details = timeDiv.find_all("p")
                try:
                        time = details[0].get_text()
                        date = details[1].get_text()
                        tempDiv = soup.find("div", class_ = "wr-value--temperature gel-trafalgar")
                        temp = tempDiv.find("span", class_ = "wr-value--temperature--c").get_text() 
                        timeValue = time[0:17]
                        tempValue = temp[:3]
                        dateValue = date +" " +timeValue
                except:
                        tempValue = "Error"
                        dateValue = "Error"
                        print("Something went wrong while trying to scrape from this website. Try again later!")
                # Adding values to the database
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("select date from weather")
                result = cursor.fetchall()
                if(dateValue,) in result:
                        print("This entry already exists. No entries were added.")
                else:
                        ins = Insert
                        ins.weatherTable(dateValue,tempValue)

                # Retrieving a three-day forecast for Dubai's weather
                website2  = requests.get("https://www.timeanddate.com/weather/united-arab-emirates/dubai/ext")
                soup2 = BeautifulSoup(website2.content, 'html.parser')
                content = soup2.find("table", id="wt-ext")
                days = content.find_all("tr")
                oneday = (datetime.today()+timedelta(days=1)).strftime("%b %d")
                twoday = (datetime.today()+timedelta(days=2)).strftime("%b %d")
                threeday = (datetime.today()+timedelta(days=3)).strftime("%b %d")
                
                class MyThreeDayForecast:
                        def __iter__(self):
                                self.a = 3
                                return self

                        def __next__(self):
                                if self.a <= 5:
                                        if self.a==3:
                                                self.day = oneday
                                        if self.a==4:
                                                self.day = twoday
                                        if self.a==5:
                                                self.day = threeday
                                        row = days[self.a].find_all("td")
                                        self.a += 1
                                        try:
                                                self.temp = row[1].get_text()
                                                self.desc = row[2].get_text()
                                        except:
                                                self.temp = "Error."
                                                self.desc = "Error."
                                                print("Something went wrong while trying to scrape from this website. Try again later!")

                                else:
                                        raise StopIteration

                myclass = MyThreeDayForecast()
                myiter = iter(myclass)

                for x in myiter:
                        connection = s.connect(DB_FILE)
                        cursor = connection.cursor()
                        cursor.execute("select day from threeday")
                        result = cursor.fetchall()
                        if(myclass.day,) in result:
                                print("This date already exists. No entries were added.")
                        else:
                                connection = s.connect(DB_FILE)
                                cursor = connection.cursor()
                                cursor.execute("insert into threeday VALUES (:day, :temp, :desc)", (myclass.day,myclass.temp,myclass.desc))
                                connection.commit()
                                cursor.close()     

                # Passing the variables to the HTML file
                return redirect(url_for('home'))
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

@app.route('/home', methods = ['POST', 'GET'])
def home():
        try:
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("select * from weather ORDER BY rowid DESC LIMIT 1")
                rv1 = cursor.fetchall()
                cursor.execute("select * from (select * from threeday ORDER BY rowid DESC LIMIT 3) ORDER BY DAY ASC")
                rv2 = cursor.fetchall()
                cursor.close()
                return render_template('index.html', day=rv1, threeday =rv2)
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

@app.route('/news')
def news():
        try:
                # Retrieving and parsing the website content through its URL
                website  = requests.get("https://www.cosmopolitan.com/uk/beauty-hair/makeup/")
                soup = BeautifulSoup(website.content, 'html.parser')
                # Finding a div using its ID
                news = soup.find_all("div", class_ = "simple-item list-header-item list-header-small-item")
                # Retrieving the title, image and link of the article
                try:
                        newsClass1 = news[0].find(class_ = "list-header-item list-header-small-item-wrap")
                        newsHead1 = newsClass1.find("a").get_text()
                        newsClass2 = news[1].find(class_ = "list-header-item list-header-small-item-wrap")
                        newsHead2 = newsClass2.find("a").get_text()
                        newsClass3 = news[2].find(class_ = "list-header-item list-header-small-item-wrap")
                        newsHead3 = newsClass3.find("a").get_text()
                        newsClass4 = news[3].find(class_ = "list-header-item list-header-small-item-wrap")
                        newsHead4 = newsClass4.find("a").get_text()
                        newsLink1 = news[0].find("a")
                        newsLink2= news[1].find("a")
                        newsLink3= news[2].find("a")
                        newsLink4= news[3].find("a")
                        newsImg1 = newsLink1.find("img")
                        newsImg2= newsLink2.find("img")
                        newsImg3= newsLink3.find("img")
                        newsImg4= newsLink4.find("img")
                except:
                        newsHead1 = "Error"
                        newsHead2 = "Error"
                        newsHead3 = "Error"
                        newsHead4 = "Error"
                        newsLink1 = "Error"
                        newsLink2= "Error"
                        newsLink3= "Error"
                        newsLink4= "Error"
                        newsImg1 = "Error"
                        newsImg2= "Error"
                        newsImg3= "Error"
                        newsImg4= "Error"
                        print("Something went wrong while trying to scrape from this website. Try again later!")
                # Passing the variables to the page
                return render_template('news.html', newsLink1 = newsLink1['href'], newsLink2 = newsLink2['href'], newsLink3 = newsLink3['href'], 
                newsLink4 = newsLink4['href'], newsImg1 = newsImg1['data-src'], newsImg2 = newsImg2['data-src'], 
                newsImg3 = newsImg3['data-src'], newsImg4 = newsImg4['data-src'], newsHead1 = newsHead1,
                newsHead2 = newsHead2, newsHead3 = newsHead3, newsHead4 = newsHead4)

        except:
                return render_template('error.html', msg=sys.exc_info()[1])

@app.route('/stats')
def stats():
        try:
                website = requests.get("https://www.statsheep.com/UCucot-Zp428OwkyRm2I7v2Q")
                soup = BeautifulSoup(website.content, 'html.parser')
                container = soup.find("table", class_="data-table m-top-standard m-bottom-standard")
                rows = container.find_all("tr")
                for x in range(12, 17):  
                        row = rows[x]
                        fields = row.find_all("td")
                        try:
                                date = fields[0].get_text()
                                subs = fields[1].get_text()
                                views = fields[2].get_text()
                                earnings = fields[3].get_text()
                        except:
                                date = "Error"
                                subs = "Error"
                                views = "Error"
                                earnings = "Error"
                                print("Something went wrong while trying to scrape from this website. Try again later!")
                        connection = s.connect(DB_FILE)
                        cursor = connection.cursor()
                        cursor.execute("select date from stats")
                        result = cursor.fetchall()
                        if(date,) in result:
                                print("This entry already exists. No entries were added.")
                        else:
                                cursor.execute("insert into stats VALUES (:date, :subs, :views, :earnings)", (date,subs,views,earnings))
                                connection.commit()
                                cursor.close()

                return redirect(url_for('displayStats'))
        
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

@app.route('/displayStats', methods = ['POST', 'GET'])
def displayStats():
        try:
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("select * from stats")
                rv = cursor.fetchall()
                cursor.close()
                return render_template('stats.html', rows=rv)
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

# Page route for reviews
@app.route('/reviews', methods = ['POST', 'GET'])
def reviews():
        try:
                if request.method == 'POST':
                        queryLink = request.form['query'].replace(" ","-")
                        website  = requests.get("https://mirabeauty.com/search/rawquery/"+queryLink)
                        soup = BeautifulSoup(website.content, 'html.parser')
                        imageDiv=soup.find(class_="StyledBox-sc-13pk1d4-0 iWnQed")
                        image = imageDiv.find("img")
                        titleDiv = soup.find(class_="StyledBox-sc-13pk1d4-0 fWrrBh")
                        title = titleDiv.find("span", class_="ProductDetails__ProductName-sc-9z5y49-0 bQxcUs").get_text()
                        return render_template('reviews.html', image = image['src'], title=title, queryLink=queryLink)
                return render_template('reviews.html')
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

# Inserting values from the contact form into table
def _cinsert(name, email, message):
	params = {'name':name, 'email':email, 'message':message}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into contact VALUES (:name, :email, :message)",params)
	connection.commit()
	cursor.close()

# Reloading page after values have been inserted into the table
@app.route('/contact', methods=['POST', 'GET'])
def contact():
        try:
                if request.method == 'POST':
                        _cinsert(request.form['name'], request.form['email'], request.form['message'])
                        return render_template('contact.html', msg="Your message has been sent!")
                else:
                        return render_template('contact.html')
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

# Inserting values into guestbook table
def _ginsert(name, message):
	
	params = {'name':name, 'message':message}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into guestbook VALUES (:name, :message)",params)
	connection.commit()
	cursor.close()

# Error page 
@app. route('/error')
def error():
         return render_template('error.html')

# Routing for guestbook page
@app.route('/guestbook')
def guestbook():
        try:
                # Retrieving and parsing the website content through its URL
                website  = requests.get("https://www.worldometers.info/coronavirus/")
                soup = BeautifulSoup(website.content, 'html.parser')
                # Finding a div using its ID
                corona = soup.find_all("div", id = "maincounter-wrap")
                # Retrieving the title of each counter
                counterTitle1 = corona[0].find("h1").get_text()
                counterTitle2= corona[1].find("h1").get_text()
                counterTitle3= corona[2].find("h1").get_text()
                # Retrieving the numbers in the counter
                corona1= corona[0].find("div", class_ = "maincounter-number")
                counter1 = corona1.find("span").get_text()
                corona2= corona[1].find("div", class_ = "maincounter-number")
                counter2 = corona2.find("span").get_text()
                corona3= corona[2].find("div", class_ = "maincounter-number")
                counter3 = corona3.find("span").get_text()
                # Adding values to the database
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("select total from virus")
                result = cursor.fetchall()
                if(counter1,) in result:
                        print("This entry already exists. No entries were added.")
                else:
                        ins = Insert
                        ins.coronaTable(counter1,counter2,counter3)

                return render_template('guestbook.html', counterTitle1=counterTitle1, counterTitle2 = counterTitle2, counterTitle3 = counterTitle3, counterNumber1 = counter1, 
                counterNumber2 = counter2, counterNumber3 = counter3)
        except:
                return render_template('error.html', msg=sys.exc_info()[1])
                
                
# Reloads page after inserting values into the table
@app.route('/gsign', methods=['POST'])
def gsign():
	
	_ginsert(request.form['name'], request.form['message'])
	return redirect(url_for('guestbook')) 


# Routing for page that contains the guestbook entries
@app.route('/view', methods=['POST', 'GET'])
def view():
        connection = s.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM guestbook")
        rv = cursor.fetchall()
        connection.commit()
        cursor.close()
        return render_template("view.html", entries=rv)


# Logging in code
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        query = "select * from accounts where username = '" + request.form['username']
        query = query + "' and password = '" + request.form['password'] + "';"
        
        cur = connection.execute(query)
        rv = cur.fetchall()
        
        cur.close()
        if len(rv) == 1:
            session['username'] = request.form['username']
            session['logged in'] = True

            return render_template('login.html', msg="Welcome back, ")
        else:
            return render_template('login.html', msg="Check your login details and try again.")
    else:
        return render_template('login.html')

# Profile page that has the name of the user signed in
@app.route('/account')
def account():
    if session['logged in'] == True:
         # Retrieving and parsing the website content through its URL
        website  = requests.get("https://www.makeupfornoobs.com/make-up-tips-according-to-skin-types/")
        soup = BeautifulSoup(website.content, 'html.parser')
        # Finding a div using its ID
        whole = soup.find("div", class_ = "entry")
        para = whole.find_all("h3")
        para2 = whole.find_all("p")
        connection = s.connect(DB_FILE)
        query1 = "select * from accounts where username = '" + session['username']
        query1 = query1 + "' and skintype = 'dry';"
        cur = connection.execute(query1)
        rv = cur.fetchall()
        title=""
        body=""
        subtitle=""
        if len(rv) == 1:
                subtitle="Since you have dry skin, we have personalised tips for you to manage it in the best way possible."
                title = para[0].get_text()
                body = para2[4].get_text()
        query2 = "select * from accounts where username = '" + session['username']
        query2 = query2 + "' and skintype = 'oily';"
        cur2 = connection.execute(query2)
        rv2 = cur2.fetchall()
        if len(rv2) == 1:
                subtitle="Since you have oily skin, we have personalised tips for you to manage it in the best way possible."
                title = para[1].get_text()
                body = para2[5].get_text()
        query3 = "select * from accounts where username = '" + session['username']
        query3 = query3 + "' and skintype = 'normal';"
        cur3 = connection.execute(query3)
        rv3 = cur3.fetchall()
        if len(rv3) == 1:
                subtitle="Since you have normal skin, we have personalised tips for you to manage it in the best way possible."
                title = para[2].get_text()
                body = para2[6].get_text()
        query4 = "select * from accounts where username = '" + session['username']
        query4 = query4 + "' and skintype = 'combination';"
        cur4 = connection.execute(query4)
        rv4 = cur4.fetchall()
        if len(rv4) == 1:
                subtitle="Since you have combination skin, we have personalised tips for you to manage it in the best way possible."
                title = para[3].get_text()
                body = para2[7].get_text()
        cursor = connection.cursor()
        query = "SELECT * FROM accounts WHERE username = '"+ session['username'] + "';"
        cursor = connection.execute(query)
        profile = cursor.fetchone()
        cursor.close()
        return render_template('account.html',profile=profile,title=title,body=body,subtitle=subtitle)
    else:
        return redirect('/login')

# Creates a new user in the accounts table
def _insertuser(username, email, password, skintype):
    params = {'username': username, 'email': email, 'password': password, 'skintype': skintype}
    cursor = connection.cursor()
    cursor.execute("insert into accounts(username, email, password, skintype) values (:username, :email, :password, :skintype)"
                   , params)
    connection.commit()

# Routing for registering page
@app.route('/register',  methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        _insertuser(request.form['username'], request.form['email'], request.form['password'], request.form['skintype'])
        return render_template('register.html', msg="You have successfully signed up. Please login.")
    else:
        return render_template('register.html')

# Logout function
@app.route('/logout')
def logout():
        session.pop('logged in', None)
        session.pop('username', None)
        return redirect('/')

# Inserting values and reloading page for the 5 different review pages
def _insert1(username, comment):
	
	params = {'username':username, 'comment':comment}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into reviews1 VALUES (:username, :comment)",params)
	connection.commit()
	cursor.close()
    
@app.route('/sign1', methods=['POST'])
def sign1():
        _insert1(session['username'], request.form['comment'])
        return redirect(url_for('review1'))
    
@app.route('/review1', methods=['POST', 'GET'])
def review1():
        try:
                website  = requests.get("https://www.lorealparisusa.com/products/makeup/eye/mascara/voluminous-lash-paradise-washable-mascara.aspx?shade=200-blackest-black")
                soup = BeautifulSoup(website.content, 'html.parser')
                product = soup.find("div", class_ = "box box-title")
                try:
                        subtitle = product.find("span").get_text()
                        title = product.find("h1").get_text()
                        desc = soup.find("p", class_ = "tab-content-text").get_text()
                except:
                        subtitle = "Error"
                        title = "Error"
                        desc = "Error"
                        print("Something went wrong while trying to scrape from this website. Try again later!")
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM reviews1")
                rv = cursor.fetchall()
                connection.commit()
                cursor.close()
                return render_template('review1.html', entries=rv, subtitle=subtitle, title=title, desc=desc[0:195])
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

def _insert2(username, comment):
	"""
	put a ne w entry in the database
	"""
	params = {'username':username, 'comment':comment}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into reviews2 VALUES (:username, :comment)",params)
	connection.commit()
	cursor.close()
    
@app.route('/sign2', methods=['POST'])
def sign2():
	"""
	Accepts POST requests, and processes the form;
	Redirect to index when completed.
	"""
	_insert2(session['username'], request.form['comment'])
	return redirect(url_for('review2'))
    
@app.route('/review2', methods=['POST', 'GET'])
def review2():
        try:
                website  = requests.get("https://www.ulta.com/prep-prime-fix-primer-setting-spray?productId=xlsImpprod15921204")
                soup = BeautifulSoup(website.content, 'html.parser')
                product = soup.find("div", class_ = "ProductMainSection")
                try:
                        subtitle = product.find(class_= "ProductMainSection__brandName").get_text()
                        title = product.find(class_ = "ProductMainSection__productName").get_text()
                        priceSpan = soup.find("span", class_="Text Text--title-6 Text--left Text--bold Text--small Text--neutral-80")
                        price = priceSpan.get_text()
                        desc = soup.find(id = "productDetails").get_text()
                except:
                        subtitle = "Error"
                        title = "Error"
                        price = "Error"
                        desc = "Error"
                        print("Something went wrong while trying to scrape from this website. Try again later!")
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM reviews2")
                rv = cursor.fetchall()
                connection.commit()
                cursor.close()
                return render_template('review2.html', entries=rv, subtitle=subtitle, title=title, desc=desc[7:218], price=price[5:])
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

def _insert3(username, comment):
	"""
	put a new entry in the database
	"""
	params = {'username':username, 'comment':comment}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into reviews3 VALUES (:username, :comment)",params)
	connection.commit()
	cursor.close()
    
@app.route('/sign3', methods=['POST'])
def sign3():
	"""
	Accepts POST requests, and processes the form;
	Redirect to index when completed.
	"""
	_insert3(session['username'], request.form['comment'])
	return redirect(url_for('review3'))
    
@app.route('/review3', methods=['POST', 'GET'])
def review3():
        try:
                website  = requests.get("https://www.hourglasscosmetics.com/products/veil-translucent-setting-powder")
                soup = BeautifulSoup(website.content, 'html.parser')
                product = soup.find("div", class_ = "product-name")
                try:
                        title = product.find("h1").get_text()
                        priceSpan = product.find("div", class_="product__price regular-price")
                        price = priceSpan.find("span", class_ = "price-item price-item--regular").get_text()
                        desc = soup.find("div", class_ = "std").get_text()
                except:
                        title = "Error"
                        price = "Error"
                        desc = "Error"
                        print("Something went wrong while trying to scrape from this website. Try again later!")
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM reviews3")
                rv = cursor.fetchall()
                connection.commit()
                cursor.close()
                return render_template('review3.html',entries=rv, title=title, price=price, desc=desc[0:280])
        except:
                return render_template('error.html', msg=sys.exc_info()[1])


def _insert4(username, comment):
	"""
	put a new entry in the database
	"""
	params = {'username':username, 'comment':comment}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into review4 VALUES (:username, :comment)",params)
	connection.commit()
	cursor.close()
    
@app.route('/sign4', methods=['POST'])
def sign4():
	"""
	Accepts POST requests, and processes the form;
	Redirect to index when completed.
	"""
	_insert4(session['username'], request.form['comment'])
	return redirect(url_for('review4'))
    
@app.route('/review4', methods=['POST', 'GET'])
def review4():
        try:
                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM review4")
                rv = cursor.fetchall()
                connection.commit()
                cursor.close()
                return render_template('review4.html',entries=rv)
        except:
                return render_template('error.html', msg=sys.exc_info()[1])

def _insert5(username, comment):
	"""
	put a new entry in the database
	"""
	params = {'username':username, 'comment':comment}
	connection = s.connect(DB_FILE)
	cursor = connection.cursor()  
	cursor.execute("insert into review5 VALUES (:username, :comment)",params)
	connection.commit()
	cursor.close()
    
@app.route('/sign5', methods=['POST'])
def sign5():
	"""
	Accepts POST requests, and processes the form;
	Redirect to index when completed.
	"""
	_insert5(session['username'], request.form['comment'])
	return redirect(url_for('review5'))
    
@app.route('/review5', methods=['POST', 'GET'])
def review5():
        try:
                website  = requests.get("https://www.ulta.com/barepro-performance-wear-liquid-foundation-broad-spectrum-spf-20?productId=xlsImpprod16321440")
                soup = BeautifulSoup(website.content, 'html.parser')
                product = soup.find("div", class_ = "ProductMainSection")
                try:
                        subtitle = product.find(class_= "ProductMainSection__brandName").get_text()
                        title = product.find(class_ = "ProductMainSection__productName").get_text()
                        priceSpan = soup.find("span", class_="Text Text--title-6 Text--left Text--bold Text--small Text--neutral-80")
                        price = priceSpan.get_text()
                        desc = soup.find(id = "productDetails").get_text()
                except: 
                        subtitle = "Error"
                        title = "Error"
                        priceSpan = "Error"
                        desc = "Error"
                        print("Something went wrong while trying to scrape from this website. Try again later!")

                connection = s.connect(DB_FILE)
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM review5")
                rv = cursor.fetchall()
                connection.commit()
                cursor.close()
                return render_template('review5.html',entries=rv, subtitle=subtitle, title=title[8:43], price=price[5:], desc=desc[28:230])
        except:
                return render_template('error.html', msg=sys.exc_info()[1])
   
if __name__ == '__main__':
        app.run(debug=True)