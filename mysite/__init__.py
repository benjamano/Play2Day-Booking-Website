import sqlite3

import bcrypt

from flask import Flask, render_template, redirect, request, url_for, session

from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key = "ComputingNEASoSecure"

sql = sqlite3.connect("/home/benjamano/mysite/Bookings.db", check_same_thread=False)
q = sql.cursor()

# ----| If function = 1 create Customer ---- If function = 2 add the sessions into the Session table ---- If function = 3 add the manager details |---- #

function = 0

# --------------| Defining Functions |-------------- #

# -------------------------------------| Startup Function |------------------------------------- #

if function == 1:
    code = "INSERT INTO Customer (FirstName, LastName, Email, PhoneNumber, Password) VALUES (?,?,?,?,?)"
    vals = ("Ben","Mercer","benmercer76@btinternet.com", "07860603962" ,"1234")
    q.execute(code,vals)
    sql.commit()

    print(code,vals)

elif function == 2:
    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Weekend Play AM", "2.00", "10.00")
    q.execute(code,vals)

    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Weekend Play PM", "2.00", "10.00")
    q.execute(code,vals)

    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Weekday Play AM", "5.00", "5.00")
    q.execute(code,vals)

    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Weekday Play PM", "3.00", "11.00")
    q.execute(code,vals)

    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Party AM", "5.00", "17.00")
    q.execute(code,vals)

    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Party PM", "5.00", "17.00")
    q.execute(code,vals)

    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Adventure Play Private Hire", "5.00", "15.00")
    q.execute(code,vals)

    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Laser Tag Private Hire", "5.00", "13.00")
    q.execute(code,vals)

    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Laser Tag + Adventure Play Private Hire", "5.00", "20.00")
    q.execute(code,vals)

    code = "INSERT INTO Session (SessionType, AdultPrice, ChildPrice) VALUES (?,?,?)"
    vals = ("Adult Night", "10.00", "0.00")
    q.execute(code,vals)

    sql.commit()

    print(code, vals)

elif function == 3:

    code = "INSERT INTO Manager (Username, Password) VALUES (?,?)"
    vals = ("Ben", "1234")
    q.execute(code, vals)

    sql.commit()

# --------------------------------------------------------------------------------------------- #

def onStart():
    try:

        tblCustomer = "CREATE TABLE IF NOT EXISTS Customer (CustomerID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, FirstName TEXT NOT NULL, LastName TEXT NOT NULL, Email TEXT NOT NULL, PhoneNumber VARCHAR(11), Password VARCHAR(255) NOT NULL, PasswordSalt VARCHAR(255))"

        tblManager = "CREATE TABLE IF NOT EXISTS Manager (ManagerID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Username VARCHAR(30) NOT NULL, Password VARCHAR(255) NOT NULL)"

        tblBooking = "CREATE TABLE IF NOT EXISTS Booking (BookingID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, CustomerID INTEGER NOT NULL, SessionID INTEGER NOT NULL, Date VARCHAR(20) NOT NULL, Time VARCHAR(20) NOT NULL, NumberOfChildren INTEGER NOT NULL, NumberOfAdults INTEGER NOT NULL, Price REAL NOT NULL, Arrived TEXT NOT NULL, ExtraNotes VARCHAR(255), FOREIGN KEY(SessionID) REFERENCES Session(SessionID), FOREIGN KEY(CustomerID) REFERENCES Customer(CustomerID))"

        tblSession = "CREATE TABLE IF NOT EXISTS Session (SessionID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, SessionType TEXT NOT NULL, AdultPrice REAL NOT NULL, ChildPrice REAL NOT NULL)"

        tblHolidays = "CREATE TABLE IF NOT EXISTS Holiday (HolidayID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Holiday Name TEXT NOT NULL, StartDate VARCHAR(20) NOT NULL, EndDate VARCHAR(20) NOT NULL)"

        q.execute(tblCustomer)
        q.execute(tblManager)
        q.execute(tblSession)
        q.execute(tblBooking)
        q.execute(tblHolidays)

    except Exception as error:
        return render_template('error.html', error=error)

def checkdate(Date):
    try:
        # Grab the date, and return True if the date is valid and False if invalid
        Date = datetime.strptime(Date, '%Y-%m-%d').date()
        today = datetime.now().date()

        if Date > today:
            app.logger.info("Date is not in the past")
            return True
        else:
            app.logger.info("Date is in the past")
            return False

    except Exception as error:
        return render_template('/error.html', error=error)

def customerloggedin():
    # Check the customer is logged in by checking if the email is present
    if session["Email"] == "":
        app.logger.info("Account not logged in")
        return False

    else:
        return True

def isweekday(BookingDate):

    Date = datetime.strptime(BookingDate, "%Y-%m-%d")
    # Get the day of the week (0 = Monday, 6 = Sunday)
    DayOfWeek = Date.weekday()

    # Check if the day is a weekday (Monday to Friday)
    if 0 <= DayOfWeek <= 4:
        return True
    else:
        return False

def findcustomerdetails(Email, CustomerID):

    if CustomerID == "" and Email != "":

        code = "SELECT * FROM Customer WHERE Customer.Email = (?)"

        q.execute(code, [Email])

        Fetch = q.fetchone()

    if CustomerID != "":

        code = "SELECT * FROM Customer WHERE CustomerID = (?)"

        q.execute(code, [CustomerID])

        Fetch = q.fetchone()

    return Fetch

def HashPassword(Password):

    Salt = bcrypt.gensalt()
    HashedPassword = bcrypt.hashpw(Password.encode("utf-8"), Salt)
    return Salt, HashedPassword

def CheckPassword(Password, StoredSalt, StoredPassword):

    HashedPassword = bcrypt.hashpw(Password.encode("utf-8"), StoredSalt)
    return HashedPassword == StoredPassword

def CheckInputValid(FirstName, LastName, Email, PhoneNumber, Password, Function):

    if len(FirstName) > 30 or len(LastName) > 30:

        return False, "First or Last Name is too long"
    elif Function != "IgnoreEmailandPassword" and len(Email) > 30:

        return False, "Email is too long"
    elif len(PhoneNumber) > 11 or (not PhoneNumber.isnumeric() and PhoneNumber != ""):

        return False, "Phone Number is too long or includes non-number characters"
    elif Function == "Full" and len(Password) > 30:

        return False, "Password is too long"
    else:

        return True, None

# ------------------------------------------------------------------------------------------------------------- #

onStart()

# ------------------------------------------------------------------------------------------------------------- #

class Customer:
    def __init__(self, Email, Password, FirstName, LastName, PhoneNumber):
        self.Email = Email
        self.Password = Password
        self.FirstName = FirstName
        self.LastName = LastName
        self.PhoneNumber = PhoneNumber

    def Register(self):

        Fetch = CheckInputValid(self.FirstName, self.LastName, self.Email, self.PhoneNumber, self.Password, Function="Full")

        valid = Fetch[0]
        error = Fetch[1]

        if not valid:

            app.logger.info(f"Error while validating details: {error}")

            return False, f"Error while validating details: {error}"

        try:
            CheckCustomerAlreadyExists = "SELECT COUNT(*) FROM Customer WHERE email = (?)"
            q.execute(CheckCustomerAlreadyExists, [self.Email])
            result = q.fetchone()

        except Exception as error:
            app.logger.info(f"Error while checking if customer already exists: {error}")
            return False, f"Error while checking if customer already exists: {error}"

        if result[0] > 0:
            app.logger.info(f"Customer with email '{self.Email}' already exists.")

            return False, "A customer using that email already exists!"

        else:
            app.logger.info(f"Customer with email '{self.Email}' does not exist, creating account")

            try:
                Salt, GrabbedHashedPassword = HashPassword(self.Password)

                app.logger.info(f"{Salt}, {GrabbedHashedPassword}")
                try:
                    app.logger.info(f"First: {self.FirstName}")

                    NewCustomer = "INSERT INTO Customer (FirstName, LastName, Email, PhoneNumber, Password, PasswordSalt) VALUES (?,?,?,?,?,?)"
                    q.execute(NewCustomer, [self.FirstName,self.LastName,self.Email,self.PhoneNumber,GrabbedHashedPassword,Salt])
                    sql.commit()
                except Exception as error:
                    app.logger.info(f"Error while executing SQL: {error}")

                    return False, error

                CustomerID = findcustomerdetails(Email=self.Email, CustomerID = "")[0]

                session["CustomerID"] = CustomerID
                session["Email"] = self.Email

                return True, None
            except Exception as error:
                app.logger.info(f"Error while registering customer: {error}")

                return False, error

    def Login(self, Email, Password, FirstName=None, LastName=None, PhoneNumber=None):
        try:
            code = "SELECT Password, PasswordSalt FROM Customer WHERE Email = (?)"
            q.execute(code, [self.Email])
            Fetch = q.fetchone()

            StoredPassword = Fetch[0]
            StoredSalt = Fetch[1]
        except Exception as error:
            return False, f"Account with Email: {Email} doesn't exist : {error}"
        if CheckPassword(self.Password, StoredSalt, StoredPassword):
            # Passwords match
            CustomerID = findcustomerdetails(Email=self.Email, CustomerID = "")[0]

            session["CustomerID"] = CustomerID
            session["Email"] = self.Email

            return True, None
        else:
            # Passwords don't match
            app.logger.info("Email or Password Incorrect, redirecting to error page")

            return False, "Email or password incorrect, please re-enter your details"

    def account(self, Email=None, Password=None, FirstName=None, LastName=None, PhoneNumber=None):
        try:

            CustomerID = session["CustomerID"]

            FirstName = findcustomerdetails(Email="", CustomerID = CustomerID)[1]

            return True, None, FirstName
        except Exception as error:
            return False, f"Error while grabbing user's first name: {error}"

    def EditDetails(self, NewFirst, NewLast, NewPhone, Edit, Email=None, Password=None, FirstName=None, LastName=None, PhoneNumber=None):

        if Edit == 0:

            Email = session["Email"]

            FindCustomerDetails = "SELECT * FROM Customer WHERE Email = (?)"
            q.execute(FindCustomerDetails, [Email])
            Fetch = q.fetchone()

            return True, None, Fetch

        else:

            Fetch = CheckInputValid(FirstName=NewFirst, LastName=NewLast, Email=Email, PhoneNumber=NewPhone, Password="", Function="IgnoreEmailandPassword")

            valid = Fetch[0]
            error = Fetch[1]

            if not valid:

                app.logger.info(f"Error while validating details: {error}")

                return False, f"Error while validating details: {error}"

            try:

                CustomerID = session["CustomerID"]

                details = (NewFirst, NewLast, NewPhone, CustomerID)

                app.logger.info(f"Editing account details, New name = {NewFirst} {NewLast}, New phone = {NewPhone}, CustomerID = {CustomerID}")

                update = "UPDATE Customer SET FirstName = (?), LastName = (?), PhoneNumber = (?) WHERE CustomerID = (?)"

                q.execute(update, details)

                sql.commit()

                return True, None
            except Exception as error:
                return False, f"Error while updating account details: {error}"

    def DeleteAccount(self):
        CustomerID = session["CustomerID"]

        try:

            DeleteBookings = "DELETE FROM Booking WHERE CustomerID = (?)"

            q.execute(DeleteBookings, [CustomerID])

        except Exception as error:

            return False, f"Error while delete customer bookings: {error}"

        try:

            DeleteAccount = "DELETE FROM Customer WHERE CustomerID = (?)"

            q.execute(DeleteAccount, [CustomerID])
            sql.commit()

            app.logger.info("Account succesfully deleted")

            return True, None

        except Exception as error:

            return False, error

class Booking:
    def __init__(self, CustomerID, SessionID, BookingDate, BookingTime, NumberOfChildren, NumberOfAdults, BookingPrice, ExtraNotes, BookingID):
        self.CustomerID = CustomerID
        self.SessionID = SessionID
        self.BookingDate = BookingDate
        self.BookingTime = BookingTime
        self.NumberOfChildren = NumberOfChildren
        self.NumberOfAdults = NumberOfAdults
        self.BookingPrice = BookingPrice
        self.ExtraNotes = ExtraNotes
        self.BookingID = BookingID

    def AddBookingDate(self):

        try:

            if checkdate(self.BookingDate) == False:
                # If booking date is in the past
                return False, "Please book a date in the future!"

            elif isweekday(self.BookingDate) == True:
                # If booking date is on a weekday
                app.logger.info("Booking is being made on a weekday")
                session["WeekdayBooking"] = True

            else:
                # If booking date is on the weekend
                app.logger.info("Booking is beng made on the weekend")
                session["WeekdayBooking"] = False
            
            session["BookingDate"] = self.BookingDate
        
        except Exception as error:

            return False, f"Error while checking booking date validility: {error}"

        return True, None

    def SelectSessionType(self, option):

        app.logger.info(f"Option: {option}")

        if option == "Weekend Play Session":
            session["BookingType"] = "Weekend Play Session"
            return True, None, "weekendplaysession"

        elif option == "Weekday Play Session":
            session["BookingType"] = "Weekday Play Session"
            return True, None, "weekdayplaysession"

        elif option == "Party":
            session["BookingType"] = "Party"
            return True, None, "party"

        elif option == "Private Hire":
            session["BookingType"] = "Private Hire"
            return True, None, "privatehire"
        else:
            return False, "Option selected is not valid!"

    def Weekday(self):

        BookingDate = session["BookingDate"]
        CustomerID = session["CustomerID"]

        session["BookingTime"] = self.BookingTime
        session["numberadults"] = self.NumberOfAdults
        session["numberchildren"] = self.NumberOfChildren

        if checkdate(Date=BookingDate) == False:
            return render_template("error.html", error="Please book a date in the future!")

        if self.BookingTime == "10:00-14:00":

            app.logger.info("Weekday Play AM = True")
            get = "SELECT SessionID FROM Session WHERE SessionType = (?)"
            q.execute(get, ["Weekday Play AM"])

            session["PlaySessionType"] = "Weekday Play AM"

        else:

            app.logger.info("Weekday Play PM = True")
            get = "SELECT SessionID FROM Session WHERE SessionType = (?)"
            q.execute(get, ["Weekday Play PM"])

            session["PlaySessionType"] = "Weekday Play PM"

        Fetch = q.fetchone()
        SessionID = Fetch[0]

        session["SessionID"] = SessionID

        checkplaysession = "SELECT count(*) FROM Booking WHERE CustomerID = (?) AND SessionID = (?) AND Date = (?)"
        details = ([(CustomerID), (SessionID), (BookingDate)])
        q.execute(checkplaysession, details)
        exists=q.fetchone()[0]

        app.logger.info(f"Details: CID: {CustomerID}, SID: {CustomerID}, Date: {BookingDate}, Exists: {exists}")

        if exists < 75:
            app.logger.info("Session is open, redirecting to confirm booking page")

            return True, None

        else:
            app.logger.info("Too many bookings for Weekday Play Session: {BookingDate}, {BookingTime}")

            return False, "Sorry, there are too many bookings for this Weekday Play Session, please book another day or time."
    
    def WeekendOrHoliday(self):
        
        BookingDate = session["BookingDate"]
        CustomerID = session["CustomerID"]

        session["BookingTime"] = self.BookingTime
        session["numberadults"] = self.NumberOfAdults
        session["numberchildren"] = self.NumberOfChildren

        if checkdate(Date=BookingDate) == False:
            return render_template("error.html", error="Please book a date in the future!")

        if self.BookingTime == "10:00-14:00":

            app.logger.info("Weekend Play AM = True")
            get = "SELECT SessionID FROM Session WHERE SessionType = (?)"
            q.execute(get, ["Weekend Play AM"])

            session["PlaySessionType"] = "Weekend Play AM"

        else:

            app.logger.info("Weekend Play PM = True")
            get = "SELECT SessionID FROM Session WHERE SessionType = (?)"
            q.execute(get, ["Weekend Play PM"])

            session["PlaySessionType"] = "Weekend Play PM"

        fetch = q.fetchone()
        SessionID = fetch[0]

        session["SessionID"] = SessionID

        checkplaysessionexists = "SELECT count(*) FROM Booking WHERE CustomerID = (?) AND SessionID = (?) AND Date = (?)"
        details = ((CustomerID), (SessionID), (BookingDate))
        q.execute(checkplaysessionexists, details)
        exists=q.fetchone()[0]

        if exists < 75:
            app.logger.info("Session is open, redirecting to confirm booking page")
            
            return True, None

        else:
            app.logger.info("Too many bookings for Weekday Play Session: {BookingDate}, {BookingTime}")
            
            return False, "Sorry, there are too many bookings for this Weekday Play Session, please book another day or time."
    
    def Party(self):
        
        CustomerID = session["CustomerID"]
        BookingDate = session["BookingDate"]

        session["BookingTime"] = self.BookingTime
        session["numberadults"] = self.NumberOfAdults
        session["numberchildren"] = self.NumberOfChildren

        app.logger.info(f"{self.BookingTime}")
        
        try:
            if self.BookingTime == "11:00-13:30":

                SessionID = "5"
        
                session["PartyType"] = "Party AM"

            elif self.BookingTime == "15:00-17:30":

                SessionID = "6"

                session["PartyType"] = "Party PM"

            session["SessionID"] = SessionID

            checkparty = "SELECT count(*) FROM Booking WHERE CustomerID = (?) AND SessionID = (?) AND Date = (?)"
            details = (CustomerID, SessionID, BookingDate)
            q.execute(checkparty, details)
            exists=q.fetchone()[0]
            app.logger.info(f"Details: CID: {CustomerID}, SID: {self.SessionID}, Date: {BookingDate}, Exists: {exists}")

            if exists < 2:

                app.logger.info("Party Session is open, redirecting to confirm booking page")
                return True, None

            else:

                app.logger.info("Too many bookings for Party: {BookingDate}, {BookingTime}")
                
                return False, "Sorry, there are no party booking available for this date or time, please book another day or time."

        except Exception as error:
            return False, f"Error while making party booking: {error}"
    
    def PrivateHire(self, PrivateHireType):
        
        BookingDate = session["BookingDate"]

        session["numberadults"] = self.NumberOfAdults
        session["numberchildren"] = self.NumberOfChildren
        session["PrivateHireType"] = PrivateHireType
        session["BookingTime"] = "18:30 - 20:30"
        
        try:

            get = "SELECT SessionID FROM Session WHERE SessionType = (?)"
            q.execute(get, [PrivateHireType])
            fetch = q.fetchone()
            SessionID = fetch[0]

            session["SessionID"] = SessionID

            checkexists = "SELECT count(*) FROM Booking WHERE SessionID IN (7, 8, 9) AND Date = (?)"
            app.logger.info(f"Looking for private hire booking with and Booking date = {BookingDate}")
            q.execute(checkexists, [BookingDate])
            exists=q.fetchone()[0]

            if exists == 0:

                session["PrivateHire"] = True

                app.logger.info("Session is open, redirecting to confirm booking page")

                return True, None

            else:
                return False, "This slot is booked, please book another date!"

        except Exception as error:
            return False, f"Error while making private hire booking: {error}"
    
    def GetFinalPrice(self, BookingType):
              
        try:
            
            if BookingType != "Private Hire":

                SessionID = session["SessionID"]
                
                app.logger.info(SessionID)
                getprices = "SELECT AdultPrice, ChildPrice FROM Session WHERE SessionID = (?)"
                q.execute(getprices, [SessionID])
                prices = q.fetchone()

                adultprice = prices[0]
                childprice = prices[1]

                NumberAdults = int(self.NumberOfAdults)
                NumberChildren = int(self.NumberOfChildren)
                adultprice = float(adultprice)
                childprice = float(childprice)

                adulttotal = adultprice * NumberAdults
                childtotal = childprice * NumberChildren

                Price = adulttotal + childtotal

                session["Price"] = Price

                app.logger.info(f"({adultprice} * {NumberAdults} = {adulttotal}) + ({childprice} * {NumberChildren} = {childtotal}) = {Price}")

            else:

                Price = 250.0

            session["Price"] = Price
            
            return True, None, Price            

        except Exception as error:
            return False, f"Error while grabbing booking details: {error}", None
        
    def CreateBooking(self):
        
        try:

            app.logger.info(f"Making booking with details: CustomerID = {self.CustomerID}, SessionID =  {self.SessionID}, Booking Date = {self.BookingDate}, Booking Time = {self.BookingTime}, Price = {self.BookingPrice}, ExtraNotes = {self.ExtraNotes}")

            new = "INSERT INTO Booking(CustomerID, SessionID, Date, Time, NumberOfChildren, NumberOfAdults, Price, Arrived, ExtraNotes) VALUES (?,?,?,?,?,?,?,'False',?)"
            details = (self.CustomerID, self.SessionID, self.BookingDate, self.BookingTime, self.NumberOfChildren, self.NumberOfAdults, self.BookingPrice, self.ExtraNotes)
            q.execute(new, details)
            sql.commit()

            app.logger.info(f"Retrieving booking ID, data = {self.CustomerID}, {self.SessionID}, {self.BookingDate}, {self.BookingTime}")

            get = "SELECT BookingID FROM Booking WHERE CustomerID = (?) AND SessionID = (?) AND Date = (?) AND Time = (?)"
            details = (self.CustomerID, self.SessionID, self.BookingDate, self.BookingTime)
            q.execute (get, details)
            fetch = q.fetchone()
            BookingID = fetch[0]

            app.logger.info(f"BookingID: {BookingID} Redirecting to Manage Booking template")

            session["BookingID"] = BookingID

            return True, None

        except Exception as error:
            
            return False, f"Error while creating booking: {error}"
    
    def ManageBooking(self):
        
        try:

            getactivebookings = "SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID WHERE Booking.CustomerID = ?;"
            q.execute(getactivebookings, [self.CustomerID])
            activebookings = q.fetchall()

            return True, None, activebookings           

        except Exception as error:

            return False, f"Error while opening manage booking template: {error}", None
    
    def DeleteBooking(self):

        app.logger.info(f"Deleting Booking with Booking ID: {self.BookingID}")

        DeleteBooking = "DELETE FROM Booking WHERE BookingID = (?)"

        try:
            q.execute(DeleteBooking, [self.BookingID])
            sql.commit()
            app.logger.info("Booking Deleted Succesfully")

            return True, None

        except Exception as error:
            
            return False, f"Error while deleting booking: {error}"

#class Session:
    #def __init__(self, SessionType):
        #self.SessionType = SessionType

    #def get_session_details(self):
        # Implement the logic to retrieve session details.

#class manager:

# ------------------------------------------------------------------------------------------------------------------------------------------------------ #
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=["POST","GET"])
def login():

    if request.method == "POST":

        Email = request.form["Email"]
        Password = request.form["Password"]

        NewCustomer = Customer(Email, Password, FirstName = None, LastName = None, PhoneNumber = None)

        Result = NewCustomer.Login(Email, Password)

        Success = Result[0]
        error = Result[1]

        if Success:
            return redirect(url_for("account"))

        else:
            return render_template("error.html", error=error)

    else:
        return render_template('login.html')

@app.route('/logout')
def logout():

    try:

        # ----| Clearing all the session vairiables then redirecting to the login page ----| #

        session["ManagerUsername"] = ""
        session["ManagerID"] = ""
        session["Password"] = ""
        session["Email"] = ""
        session["PlaySession"] = False
        session["Party"] = False
        session["PrivateHire"] = False
        session["CustomerID"] = ""
        session["PlaySessionType"] = ""
        session["BookingID"] = ""
        session["BookingDate"] = ""
        session["PrivateHireType"] = ""
        session["BookingTime"] = ""
        session["numberadults"] = ""
        session["numberchildren"] = ""
        session["BookingType"] = ""


        return redirect(url_for("index"))

    except Exception as error:
        return render_template("error.html", error=error)

@app.route('/signup', methods=["POST","GET"])
def signup():

    if request.method == "POST":

        First = request.form["First"]
        Last = request.form["Last"]
        Email = request.form["Email"]
        Phone = request.form["Phone"]
        Password = request.form["Password"]

        NewCustomer = Customer(Email=Email, Password=Password, FirstName=First, LastName=Last, PhoneNumber=Phone)

        Result = NewCustomer.Register()

        Success = Result[0]
        error = Result[1]

        if Success:
            return redirect(url_for("account"))

        else:
            return render_template("error.html", error=error)

    else:
        return render_template("signup.html")

@app.route('/account/editaccountdetails', methods=["POST","GET"])
def editaccountdetails():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    if request.method == "POST":

        try:

            NewFirst = request.form["NewFirst"]
            NewLast = request.form["NewLast"]
            NewPhone = request.form["NewPhone"]

            NewCustomer = Customer(Email = None, Password = None, FirstName = None, LastName = None, PhoneNumber = None)

            Result = NewCustomer.EditDetails(NewFirst = NewFirst, NewLast = NewLast, NewPhone = NewPhone, Edit = 1)

            Success = Result[0]
            error = Result[1]

            if Success:
                return redirect(url_for("editaccountdetails"))
            else:
                return render_template("error.html", error=error)

        except Exception as error:
            return render_template("error.html", error=f"Error in editing account details: {error}")

    else:

        NewCustomer = Customer(Email = None, Password = None, FirstName = None, LastName = None, PhoneNumber = None)

        Result = NewCustomer.EditDetails(NewFirst = None, NewLast= None, NewPhone= None, Edit = 0)

        Success = Result[0]
        error = Result[1]
        Fetch = Result[2]

        if Success:
            try:
                return render_template("accountdetails.html", First=Fetch[1], Last=Fetch[2], Email=Fetch[3], Phone=Fetch[4])

            except Exception as error:
                return render_template("error.html", error=f"Error while rendering template for account details: {error}")
        else:
            return render_template("error.html", error=f"Error while grabbing account details: {error}")



@app.route("/account/delete_account", methods=['POST'])
def deleteaccount():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    NewCustomer = Customer(Email = None, Password = None, FirstName = None, LastName = None, PhoneNumber = None)

    Result = NewCustomer.DeleteAccount()

    Success = Result[0]
    error = Result[1]

    if Success:
        return redirect(url_for("index"))
    else:
        return render_template("error.html", error=f"Error while deleting account: {error}")



@app.route("/account", methods=["POST","GET"])
def account():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    NewCustomer = Customer(Email = None, Password = None, FirstName = None, LastName = None, PhoneNumber = None)
    Result =  NewCustomer.account()

    Success = Result[0]
    error = Result[1]
    First = Result[2]

    if Success:
        return render_template("account.html", First=First)

    else:
        return render_template("error.html", error=error)

@app.route('/account/newbooking', methods=["POST","GET"])
def newbooking():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    # Resetting all session variables that are used in this process
    session["PlaySession"] = False
    session["Party"] = False
    session["PrivateHire"] = False
    session["PlaySessionType"] = ""
    session["BookingSession"] = ""
    session["BookingID"] = ""
    session["BookingDate"] = ""
    session["PrivateHireType"] = ""
    session["BookingTime"] = ""
    session["numberadults"] = ""
    session["numberchildren"] = ""
    session["PlaySession"] = False
    session["WeekdayBooking"] = False
    session["ExtraNotes"] = ""


    if request.method == "POST":
        CustomerID = session["CustomerID"]
        BookingDate = request.form["BookingDate"]

        NewBooking = Booking(CustomerID=CustomerID, BookingID=None,SessionID=None, NumberOfAdults=None, NumberOfChildren=None, ExtraNotes=None, BookingDate=BookingDate, BookingTime=None, BookingPrice=None)
        
        Result = NewBooking.AddBookingDate()

        Success = Result[0]
        error = Result[1]

        if Success:
            return redirect(url_for("sessiontype"))

        else:
            return render_template("error.html", error=error)

    else:
        return render_template("date.html")

@app.route("/account/newbooking/sessiontype", methods=["POST","GET"])
def sessiontype():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    WeekdayBooking = session["WeekdayBooking"]

    # This checks the option grabbed from the html template and redirects the user accordingly.
    if request.method == "POST":
        option = request.form["bookingtype"]

        NewBooking = Booking(CustomerID=None, BookingID=None, SessionID=None, BookingDate=None, BookingTime=None, NumberOfChildren=None, NumberOfAdults=None, BookingPrice=None, ExtraNotes=None)

        Result = NewBooking.SelectSessionType(option)

        Success = Result[0]
        error = Result[1]
        urlname = Result[2]

        if Success:
            return redirect(url_for(urlname))

        else:
            return render_template("error.html", error=error)

    # The variable "WeekdayBooking" is a boolean which tells the booking page if the booking is being made on the weekday or weekend
    else:
        return render_template("newbooking.html", WeekdayBooking = WeekdayBooking)

@app.route('/account/newbooking/playsession/weekday',  methods=["POST","GET"])
def weekdayplaysession():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    if request.method == "POST":

        BookingTime = request.form["bookingtime"]
        numberadults = request.form["numberadults"]
        numberchildren = request.form["numberchildren"]

        NewBooking = Booking(CustomerID=None, BookingID=None, SessionID=None, BookingDate=None, BookingTime=BookingTime, NumberOfChildren=numberchildren, NumberOfAdults=numberadults, BookingPrice=None, ExtraNotes=None)

        Result = NewBooking.Weekday()

        Success = Result[0]
        error = Result[1]

        if Success:
            return redirect(url_for("extras"))    

        else:
            return render_template("error.html", error=error)

    else:
        return render_template("weekdayplaysession.html")

@app.route('/account/newbooking/playsession/weekendholiday',  methods=["POST","GET"])
def weekendplaysession():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    if request.method == "POST":

        BookingTime = request.form["bookingtime"]
        numberadults = request.form["numberadults"]
        numberchildren = request.form["numberchildren"]
        
        NewBooking = Booking(CustomerID=None, BookingID=None, SessionID=None, BookingDate=None, BookingTime=BookingTime, NumberOfChildren=numberchildren, NumberOfAdults=numberadults, BookingPrice=None, ExtraNotes=None)

        Result = NewBooking.WeekendOrHoliday()

        Success = Result[0]
        error = Result[1]
        
        if Success:
            return redirect(url_for("extras"))    
            
        else:
            return render_template("error.html", error=error)

    else:
        return render_template("weekendplaysession.html")


@app.route('/account/newbooking/party', methods=["POST","GET"])
def party():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    if request.method == "POST":

        BookingTime = request.form["bookingtime"]
        NumberAdults = request.form["numberadults"]
        NumberChildren = request.form["numberchildren"]
        
        NewBooking = Booking(CustomerID=None, BookingID=None, SessionID=None, BookingDate=None, BookingTime=BookingTime, NumberOfChildren=NumberChildren, NumberOfAdults=NumberAdults, BookingPrice=None, ExtraNotes=None)

        Result = NewBooking.Party()

        Success = Result[0]
        error = Result[1]
        
        if Success:
            return redirect(url_for("extras"))
        
        else:
            return render_template("error.html", error=error)
        
    else:
        return render_template("party.html")

@app.route("/account/newbooking/privatehire", methods=["POST","GET"])
def privatehire():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    if request.method == "POST":

        PrivateHireType = request.form["privatehiretype"]
        NumberAdults = request.form["numberadults"]
        NumberChildren = request.form["numberchildren"]

        NewBooking = Booking(CustomerID=None, BookingID=None, SessionID=None, BookingDate=None, BookingTime=None, NumberOfChildren=NumberChildren, NumberOfAdults=NumberAdults, BookingPrice=None, ExtraNotes=None)

        Result = NewBooking.PrivateHire(PrivateHireType=PrivateHireType)

        Success = Result[0]
        error = Result[1]
        
        if Success:
            return redirect(url_for("extras"))        
        else:
            return render_template("error.html", error=error)

    else:
        return render_template("privatehire.html")

@app.route("/account/newbooking/optionalextras", methods=["POST","GET"])
def extras():
    
    if customerloggedin() == False:
        return redirect(url_for("index"))
    
    PrivateHireType = session["PrivateHireType"]
    BookingType = session["BookingType"]
    
    if request.method == "POST":
        
        try:
            
            ExtraNotes = request.form["Extra"]
            session["ExtraNotes"] = ExtraNotes
            
        except Exception as error:
            
            app.logger.info(f"Either no Extra Notes selected or an error happene: {error}")
            
        return redirect(url_for("confirmbooking"))

    else:
        return render_template("optionalextras.html", BookingType = BookingType, privatehiretype = PrivateHireType)

@app.route("/account/managebooking", methods=["POST","GET"])
def managebooking():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    CustomerID = session["CustomerID"]

    if request.method == "POST":

        BookingID = request.form["BookingID"]
        BookingDate = request.form["BookingDate"]
        BookingTime = request.form["BookingTime"]
        SessionType = request.form["SessionType"]
        Extra = request.form["Extra"]
        BookingPrice = request.form["BookingPrice"]
        
        session["BookingPrice"] = BookingPrice
        session["BookingID"] = BookingID
        session["BookingDate"] = BookingDate
        session["BookingTime"] = BookingTime
        session["SessionType"] = SessionType
        session["Extra"] = Extra

        app.logger.info(f"Session Type: {SessionType}")

        return redirect('/account/managebooking/booking')

    else:
        
        NewBooking = Booking(CustomerID=CustomerID, BookingID=None,BookingDate=None, BookingTime=None,BookingPrice=None, SessionID=None, NumberOfAdults=None, NumberOfChildren=None, ExtraNotes=None)
        
        Result = NewBooking.ManageBooking()
        
        Success = Result[0]
        error = Result[1]
        activebookings = Result[2]
        
        if Success:
            return render_template("managebooking.html", activebookings = activebookings)
        
        else:
            return render_template("error.html", error=error)

@app.route("/account/managebooking/booking", methods=["POST", "GET"])
def booking():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    BookingID = session["BookingID"]
    BookingDate = session["BookingDate"]
    BookingTime = session["BookingTime"]
    SessionType = session["SessionType"]
    Extra = session["Extra"]
    BookingPrice = session["BookingPrice"]

    if request.method == "POST":
        return redirect(url_for("deletebooking"))
    
    else:

        return render_template("booking.html", BookingID = BookingID, BookingDate = BookingDate, BookingTime = BookingTime, Extra = Extra, SessionType = SessionType, BookingPrice = BookingPrice)

@app.route("/account/managebooking/deletebooking", methods=["POST", "GET"])
def deletebooking():

    BookingID = session["BookingID"]

    NewBooking = Booking(CustomerID=None, BookingID = BookingID, BookingDate=None, BookingTime=None,BookingPrice=None, SessionID=None, NumberOfAdults=None, NumberOfChildren=None, ExtraNotes=None)

    Result = NewBooking.DeleteBooking()

    Success = Result[0]
    error = Result[1]
    
    if Success:
        return redirect(url_for("managebooking"))
    
    else:
        return render_template("error.html", error=error)

@app.route("/account/newbooking/confirmbooking", methods=["POST","GET"])
def confirmbooking():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    if request.method == "POST":
        return redirect(url_for("createbooking"))

    else:
        
        NumberOfAdults = session["numberadults"]
        NumberOfChildren = session["numberchildren"]
        BookingType = session["BookingType"]
        BookingTime = session["BookingTime"]
        BookingDate = session["BookingDate"]
        PrivateHireType = session["PrivateHireType"]
        SessionID = session["SessionID"]
        ExtraNotes = session["ExtraNotes"]
        
        NewBooking = Booking(CustomerID=None, BookingID = None, SessionID=SessionID, BookingDate=None, BookingTime=None,NumberOfChildren=NumberOfChildren, NumberOfAdults=NumberOfAdults, BookingPrice=None, ExtraNotes=None)

        Result = NewBooking.GetFinalPrice(BookingType=BookingType)

        Success = Result[0]
        error = Result[1]
        Price = Result[2]
        
        if Success:
            return render_template("confirmbooking.html", BookingType = BookingType, BookingTime = BookingTime, BookingDate = BookingDate, PrivateHireType = PrivateHireType, NumberAdults = NumberOfAdults, NumberChildren = NumberOfChildren, Price = Price, ExtraNotes = ExtraNotes)
        
        else:
            return render_template("error.html", error=error)

@app.route("/account/newbooking/createbooking")
def createbooking():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    CustomerID = session["CustomerID"]
    SessionID = session["SessionID"]
    BookingTime = session["BookingTime"]
    BookingDate = session["BookingDate"]
    NumberOfAdults = session["numberadults"]
    NumberOfChildren = session["numberchildren"]
    Price = session["Price"]
    ExtraNotes = session["ExtraNotes"]

    NewBooking = Booking(CustomerID=CustomerID, BookingID=None, SessionID=SessionID, BookingDate=BookingDate, BookingTime=BookingTime,NumberOfChildren=NumberOfChildren, NumberOfAdults=NumberOfAdults, BookingPrice=Price, ExtraNotes=ExtraNotes)

    Result = NewBooking.CreateBooking()

    Success = Result[0]
    error = Result[1]
    
    if Success:
        return redirect(url_for("managebooking"))
    
    else:
        return render_template("error.html", error=error)

# ---------------------------------------------| Information |----------------------------------------- #

@app.route("/centerinfo")
def centerinfo():
    return render_template("centredetails/home.html")

@app.route("/centerinfo/lasertag")
def laserinfo():
    return render_template("centredetails/laser.html")

@app.route("/centerinfo/parties")
def partyinfo():
    return render_template("centredetails/parties.html")

@app.route("/centerinfo/menus")
def menuinfo():
    return render_template("centredetails/menus.html")

# ---------------------------------------------| Manager |--------------------------------------------- #

@app.route("/managerlogin", methods=["POST","GET"])
def managerlogin():

    if request.method == "POST":

        Username = request.form["Username"]
        Password = request.form["Password"]

        if Username == "" or Password == "":

            return render_template("manager/managerlogin.html")

        else:

            CheckCustomerExists = "SELECT COUNT(*) FROM Manager WHERE Username = (?) AND Password = (?)"
            q.execute(CheckCustomerExists, [Username, Password])
            result = q.fetchone()

            if result[0] > 0:

                session["ManagerUsername"] = Username

                app.logger.info(f"Manager with Username {Username} found, checking password then redirecting to account page")

                try:

                    RetrieveManager = "SELECT * FROM Manager WHERE Username = (?) AND Password = (?)"
                    q.execute(RetrieveManager, [Username, Password])
                    Fetch = q.fetchone()

                    ManagerID = Fetch[0]

                    session["ManagerID"] = ManagerID

                    return redirect(url_for("manageraccount"))

                except Exception:

                    return render_template("error.html", error="Password Incorrect")

            else:

                app.logger.info(f"Manager with Username {Username} does not exist, redirecting to error page")

                return render_template('/error.html', error="Account Doesn't Exist")

    else:

        return render_template("manager/managerlogin.html")

@app.route("/manager/account", methods=["POST","GET"])
def manageraccount():

    try:
        Today = date.today()
        Tommorow = Today + timedelta(days=1)

        gettommorowsbookings = "SELECT count(*) FROM Booking WHERE Date = (?)"
        q.execute(gettommorowsbookings, [Tommorow])
        Fetch = q.fetchone()
        TommorowsBookings = Fetch[0]

        gettotalbookings = "SELECT count(*) FROM Booking"
        q.execute(gettotalbookings)
        Fetch = q.fetchone()
        TotalBookings = Fetch[0]

    except Exception as error:
        return render_template("error.html", error=error)

    return render_template("manager/account.html", TotalBookings = TotalBookings, TommorowsBookings = TommorowsBookings)

@app.route("/manager/editbooking", methods=["POST", "GET"])
def managereditbooking():
    if request.method == "POST":

        if "Filter" in request.form != "Filter":

            StartDate = request.form.get("StartDate")
            EndDate = request.form.get("EndDate")
            Filter = request.form.get("Filter")

            app.logger.info(f"{StartDate} {EndDate} {Filter}")

            if Filter == "all" and StartDate and EndDate:
                # Filter by date range
                getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.Extra, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults, Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Booking.Date BETWEEN '{StartDate}' AND '{EndDate}' ORDER BY Booking.Date ASC"
            elif Filter != "all" and StartDate and EndDate:
                # Filter by type and date range

                getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults , Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Session.SessionType = '{Filter}' AND Booking.Date BETWEEN '{StartDate}' AND '{EndDate}' ORDER BY Booking.Date ASC"
            elif Filter != "all":
                # Filter by type only
                if  Filter == "Private Hire":
                    getactivebookings = "SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults , Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Session.SessionID = 8 OR Session.SessionID = 9 OR Session.SessionID = 10 ORDER BY Booking.Date ASC"
                else:
                    getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults , Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Session.SessionType = '{Filter}' ORDER BY Booking.Date ASC"
            elif StartDate and EndDate:
                # Filter by date range only
                getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults, Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Booking.Date BETWEEN '{StartDate}' AND '{EndDate}' ORDER BY Booking.Date ASC"
            else:
                getactivebookings = "SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults, Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID ORDER BY Booking.Date ASC"

            q.execute(getactivebookings)
            activebookings = q.fetchall()
            app.logger.info(f"{getactivebookings} ,{activebookings}")

            return render_template("manager/selectbooking.html", activebookings=activebookings)

        else:

            app.logger.info("Redirecting to booking page")

            BookingID = request.form["BookingID"]
            BookingDate = request.form["BookingDate"]
            BookingTime = request.form["BookingTime"]
            SessionType = request.form["SessionType"]
            Extra = request.form["Extra"]
            BookingPrice = request.form["BookingPrice"]
            NumberAdults = request.form["NumberAdults"]
            NumberChildren = request.form["NumberChildren"]
            FirstName = request.form["FirstName"]
            LastName = request.form["LastName"]

            session["BookingID"] = BookingID
            session["BookingPrice"] = BookingPrice
            session["BookingDate"] = BookingDate
            session["BookingTime"] = BookingTime
            session["SessionType"] = SessionType
            session["NumberAdults"] = NumberAdults
            session["NumberChildren"] = NumberChildren
            session["Extra"] = Extra
            session["FirstName"] = FirstName
            session["LastName"] = LastName

            return redirect(url_for("managerbooking"))

    else:
        try:

            getactivebookings = "SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults, Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID ORDER BY Booking.Date ASC"
            q.execute(getactivebookings)
            activebookings = q.fetchall()

            return render_template("manager/selectbooking.html", activebookings=activebookings)

        except Exception as error:
            return render_template("error.html", error=error)

@app.route("/manager/managebooking/booking", methods=["POST", "GET"])
def managerbooking():

    BookingID = session["BookingID"]
    BookingDate = session["BookingDate"]
    BookingTime = session["BookingTime"]
    SessionType = session["SessionType"]
    Extra = session["Extra"]
    BookingPrice = session["BookingPrice"]
    NumberAdults = session["NumberAdults"]
    NumberChildren = session["NumberChildren"]
    FirstName = session["FirstName"]
    LastName = session["LastName"]

    if request.method == "POST":

        app.logger.info(f"Deleting Booking with Booking ID: {BookingID}")

        DeleteBooking = "DELETE FROM Booking WHERE BookingID = (?)"

        try:
            q.execute(DeleteBooking, [BookingID])
            sql.commit()
            app.logger.info("Booking Deleted Succesfully")

            return redirect(url_for("managereditbooking"))

        except Exception as error:
            return render_template("/error.html", error=error)

    else:

        return render_template("manager/booking.html", BookingID = BookingID, BookingDate = BookingDate, BookingTime = BookingTime, Extra = Extra, SessionType = SessionType, BookingPrice = BookingPrice, NumberAdults = NumberAdults, NumberChildren = NumberChildren, FirstName = FirstName, LastName = LastName)

@app.route('/manager/editcustomer', methods=["POST","GET"])
def managereditcustomer():
    if request.method == "POST":
        try:
            CustomerID = request.form["CustomerID"]
            First = request.form["FirstName"]
            Last = request.form["LastName"]
            Email = request.form["Email"]
            Phone = request.form["PhoneNo"]

            session["CustomerID"] = CustomerID
            session["First"] = First
            session["Last"] = Last
            session["Email"] = Email
            session["Phone"] = Phone

            return redirect(url_for("managercustomer"))

        except Exception as error:
            return render_template("error.html", error=error)

    else:
        try:

            getcustomers = "SELECT Customer.CustomerID, Customer.FirstName, Customer.LastName, Customer.Email, Customer.PhoneNumber FROM Customer"
            q.execute(getcustomers)
            activecustomers = q.fetchall()

            return render_template("manager/selectcustomer.html", activecustomers = activecustomers)

        except Exception as error:

            return render_template("error.html", error=error)


@app.route("/manager/editcustomer/customer", methods=["POST", "GET"])
def managercustomer():

    CustomerID = session["CustomerID"]
    First = session["First"]
    Last = session["Last"]
    Email = session["Email"]
    Phone = session["Phone"]

    if request.method == "POST":
        
        Delete = request.form["delete"]
        
        if Delete == "False":
            
            try:
    
                NewFirst = request.form["NewFirst"]
                NewLast = request.form["NewLast"]
                NewPhone = request.form["NewPhone"]
    
                if NewFirst != First or NewLast != Last or NewPhone != Phone:
    
                    Fetch = CheckInputValid(FirstName=NewFirst, LastName=NewLast, Email=Email, PhoneNumber=NewPhone, Password="", Function="IgnoreEmailandPassword")
    
                    valid = Fetch[0]
                    error = Fetch[1]
    
                    if not valid:
    
                        app.logger.info(f"Error while validating details: {error}")
    
                        return render_template("error.html", error=error)
                        #return False, f"Error while validating details: {error}"
                    else:
    
                        details = (NewFirst, NewLast, NewPhone, CustomerID)
    
                        app.logger.info(f"Editing account details, New name = {NewFirst} {NewLast}, New phone = {NewPhone}, CustomerID = {CustomerID}")
    
                        update = "UPDATE Customer SET FirstName = (?), LastName = (?), PhoneNumber = (?) WHERE CustomerID = (?)"
    
                        q.execute(update, details)
    
                        sql.commit()
    
                        return redirect(url_for("managereditcustomer"))
                
                else:
                    
                    return redirect(url_for("managereditcustomer"))
                
            except Exception as error:
                
                return render_template("error.html", error=error)

        else:
            app.logger.info(f"Deleting Customer with Customer ID: {CustomerID}")

            DeleteCustomer = "DELETE FROM Customer WHERE CustomerID = (?)"

            try:
                q.execute(DeleteCustomer, [CustomerID])
                sql.commit()
                app.logger.info("Customer Deleted Succesfully")
                return redirect(url_for("managereditcustomer"))
            
            except Exception as error:
                return render_template("error.html", error=error)
        
    else:

        return render_template("manager/customer.html", CustomerID = CustomerID, FirstName = First, LastName = Last, Email = Email, PhoneNumber = Phone)

@app.route("/manager/holidays", methods=["POST", "GET"])
def manageholidays():

    return render_template("/manager/editholidays.html")

@app.route("/manager/arrived", methods=["POST", "GET"])
def mark_arrived():

    if request.method == "POST":
        BookingID = request.form["BookingID"]#
        Arrived = request.form["Arrived"]

        if Arrived == "True":
            code = "UPDATE Booking SET Arrived = 'False' WHERE BookingID = (?)"

        else:

            code = "UPDATE Booking SET Arrived = 'True' WHERE BookingID = (?)"

        try:

            q.execute(code, [BookingID])
            sql.commit()

        except Exception as error:
            return render_template("error.html", error=f"Error when executing SQL, when trying to change arrived status: {error}")

        return redirect(url_for("managereditbooking"))

    else:
        return redirect(url_for("managereditbooking"))

# ---------------------------------------------------------------------------------------------------------------- #

@app.route("/account/developer")
def devtest():
    
    return render_template("devtest.html")


if __name__ == '__main__':
    #db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
