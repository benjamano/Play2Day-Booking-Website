import sqlite3, bcrypt, ssl, smtplib

from email.message import EmailMessage

from flask import Flask, render_template, redirect, request, url_for, session

from datetime import datetime, date, timedelta

emailsender = "benjamano12@gmail.com"
emailpassword = "bhpm pbna aajb gxwg"

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
        
        #sql = "DELETE FROM Manager WHERE Username = 'Ben'"
        #q.execute(sql)
        
        #sql = "INSERT INTO Manager (Username, Password) VALUES ('Ben','choc1234')"
        #q.execute(sql)

        tblCustomer = "CREATE TABLE IF NOT EXISTS Customer (CustomerID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, FirstName TEXT NOT NULL, LastName TEXT NOT NULL, Email TEXT NOT NULL, PhoneNumber VARCHAR(11), Password VARCHAR(255) NOT NULL, PasswordSalt VARCHAR(255))"

        tblManager = "CREATE TABLE IF NOT EXISTS Manager (ManagerID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Username VARCHAR(30) NOT NULL, Password VARCHAR(255) NOT NULL)"

        tblBooking = "CREATE TABLE IF NOT EXISTS Booking (BookingID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, CustomerID INTEGER NOT NULL, SessionID INTEGER NOT NULL, Date VARCHAR(20) NOT NULL, Time VARCHAR(20) NOT NULL, NumberOfChildren INTEGER NOT NULL, NumberOfAdults INTEGER NOT NULL, Price REAL NOT NULL, Arrived TEXT NOT NULL, ExtraNotes VARCHAR(255), FOREIGN KEY(SessionID) REFERENCES Session(SessionID), FOREIGN KEY(CustomerID) REFERENCES Customer(CustomerID))"

        tblSession = "CREATE TABLE IF NOT EXISTS Session (SessionID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, SessionType TEXT NOT NULL, AdultPrice REAL NOT NULL, ChildPrice REAL NOT NULL)"

        tblHolidays = "CREATE TABLE IF NOT EXISTS Holiday (HolidayID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Name TEXT NOT NULL, StartDate VARCHAR(20) NOT NULL, EndDate VARCHAR(20) NOT NULL, Description VARCHAR(255) NOT NULL)"

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
            #app.logger.info("Date is not in the past")
            return True
        else:
            #app.logger.info("Date is in the past")
            return False

    except Exception as error:
        return render_template('/error.html', error=error)

def customerloggedin():
    # Check the customer is logged in by checking if the email is present
    try:
        
        if session["Email"] == "":
            #app.logger.info("Account not logged in")
            return False

        else:
            return True
    
    except:
        return False

def managerloggedin():
        # Check the manager is logged in by checking if the username is present
    try:
        if session["ManagerUsername"] == "":
            #app.logger.info("Account not logged in")
            return False

        else:
            return True
    except:
        return False

def isweekday(BookingDate):

    Date = datetime.strptime(BookingDate, "%Y-%m-%d")
    # Get the day of the week (0 = Monday, 6 = Sunday)
    DayOfWeek = Date.weekday()

    checkexists = "SELECT count(*) FROM Holiday WHERE StartDate <= (?) AND EndDate >= (?)"
    q.execute(checkexists, [BookingDate, BookingDate])
    HolidaysThatDay=q.fetchone()[0]

    #app.logger.info(f"Holidays that day: {HolidaysThatDay}")

    # Check if the day is a weekday (Monday to Friday) or the booking is being made during the holiday
    if HolidaysThatDay > 0:
    
        return False

    else:
        if 0 <= DayOfWeek <= 4:
            return True
        else:
            return False
        
def bookingclosed(BookingDate):
    
    #This function checks if the booking is closed, due to a holiday being set that day by a manager, it returns a boolean value indicating whether the booking is closed or not, this is then used by the caller of the function to determine whether the booking is valid.
    
    try:
        getdescription = "SELECT Description FROM Holiday WHERE StartDate <= (?) AND EndDate >= (?)"
    
        q.execute(getdescription, [BookingDate, BookingDate])
        descriptions = q.fetchall()
    
        #app.logger.info(f"{descriptions}")

        i = 0

        for description in descriptions:
            
            #app.logger.info(f"{description}, {i}")
            
            if description[i] == "Closed":
        
                return True
            
            i += 1
    
        return False    
        
    except Exception as error:
        
        app.logger.info(f"Either no holidays at that time or an error occurred: {error}")

def findcustomerdetails(Email, CustomerID):
    
    #This is a simple function to find the customer details, depending on the values passed in, then returning another, for example, the email is not sent, but customer id is, so the email is found and returned. 

    if CustomerID == "" and Email != "":

        code = "SELECT * FROM Customer WHERE Email = (?)"

        q.execute(code, [Email])

        Fetch = q.fetchone()
## jack and joe were here

    elif CustomerID != "":

        code = "SELECT * FROM Customer WHERE CustomerID = (?)"

        q.execute(code, [CustomerID])

        Fetch = q.fetchone()
        
    else:
        
        Fetch = "Empty"

    #app.logger.info(f"Fetch: {Fetch}, Email: {Email}, CID: {CustomerID}")

    return Fetch

def HashPassword(Password):
    
    #This function hashes the password entered by the user, either when signing in.

    Salt = bcrypt.gensalt()
    HashedPassword = bcrypt.hashpw(Password.encode("utf-8"), Salt)
    return Salt, HashedPassword

def CheckPassword(Password, StoredSalt, StoredPassword):
    
    #This function checks the password using the stored salt that was stored in the database, the password entered when logging in and the stored password in the database.

    HashedPassword = bcrypt.hashpw(Password.encode("utf-8"), StoredSalt)
    return HashedPassword == StoredPassword

def CheckInputValid(FirstName, LastName, Email, PhoneNumber, Password, Function):
    
    #This function is used to check the inputs from the edit details forms or the signup forms, and checks the validity of the inputed data, returning False if the data doesn't meet the criteria, this shouldn't need to take action, it's mainly incase someone changes the html requirements through inspect element to allow invalid data.
    

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

def sendEmail(Email, Option):
    
    if Email == "" or Email == None or Email == "None":
        return False, "Error while sending email: No Email Entered or was empty"
    
    emailreceiver = Email
    
    details = findcustomerdetails(Email, CustomerID = "")
    
    FirstName = details[1]
    PhoneNumber = details[4]
    
    if Option == "Confirm":

        subject = "Welcome to Play2Day!"
        body = f"""
        Hi, {FirstName}!
        
        You've signed up to Play2Day with this email!
        
        We can't wait to see you here soon!
        
        If you didn't sign up, please reply to this email and we'll delete your account.

        The Play2Day Team"""

    elif Option == "CheckEmail":
        
        subject = "We need to check your details"
        
        body = f"""
        Hi {FirstName}, 
        
        We need to check your details are still correct, please respond to this email to confirm this email is still active.
        
        Best, The Play2Day Team"""
        
    elif Option == "CheckPhone":
        
        subject = "We need to check your details"
        
        body = f"""
        Hi {FirstName}, 
        
        We need to check your details are still correct, is your Phone Number {PhoneNumber}?
        
        If not please reply to this email
        
        Best, The Play2Day Team"""
        
    elif Option == "DeleteAccount":
        
        subject = "You've just deleted your account"
        
        body = f"""
        Hi {FirstName}, 
        
        We're so sorry to see you go, if you have any feedback please reply to this email, we are more than happy to help!
        
        Best, The Play2Day Team"""
        
    elif Option == "Test":
        subject = "Test Email"
        
        body = f"""
        This is a test email, if you can read this, the email system is working!
        
        Email: {Email}, Phone Number: {PhoneNumber}, FirstName: {FirstName}"""
    
    else:
        return False, "Error while sending email: Invalid Option Selected"
    
    context = ssl.create_default_context()
    
    em = EmailMessage()
    em["From"] = emailsender
    em["To"] = emailreceiver
    em["subject"] = subject
    em.set_content(body)
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(emailsender, emailpassword)
        smtp.sendmail(emailsender, emailreceiver, em.as_string())
    
    app.logger.info(f"Email sent to {emailreceiver} with subject {subject} and body {body}")
    
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
        
        #This function is called when the customer is first registered to the system, it checks the validality of data and makes sure a customer with that email doesn't already exist. If all the requirements are met, the customer is created and added into the database.

        Fetch = CheckInputValid(self.FirstName, self.LastName, self.Email, self.PhoneNumber, self.Password, Function="Full")

        valid = Fetch[0]
        error = Fetch[1]

        if not valid:

            #app.logger.info(f"Error while validating details: {error}")

            return False, f"Error while validating details: {error}"

        try:
            CheckCustomerAlreadyExists = "SELECT COUNT(*) FROM Customer WHERE email = (?)"
            q.execute(CheckCustomerAlreadyExists, [self.Email])
            result = q.fetchone()

        except Exception as error:
            #app.logger.info(f"Error while checking if customer already exists: {error}")
            return False, f"Error while checking if customer already exists: {error}"

        if result[0] > 0:
            #app.logger.info(f"Customer with email '{self.Email}' already exists.")

            return False, "A customer using that email already exists!"

        else:
            #app.logger.info(f"Customer with email '{self.Email}' does not exist, creating account")

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

                results = sendEmail(self.Email, "Confirm")
                
                if not results[0]:
                    app.logger.info(f"Error while sending email: {results[1]}")
                
                return True, None
            except Exception as error:
                app.logger.info(f"Error while registering customer: {error}")

                return False, error

    def Login(self, Email, Password, FirstName=None, LastName=None, PhoneNumber=None):
        
        #This function is called when the user is logging in through the website, it checks the date inputted in the form is valid, and checks the password to see if it is correct.
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
            CustomerDetails = findcustomerdetails(Email=self.Email, CustomerID = "")

            session["CustomerID"] = CustomerDetails[0]
            session["Email"] = self.Email

            return True, None
        else:
            # Passwords don't match
            #app.logger.info("Email or Password Incorrect, redirecting to error page")

            return False, "Email or password incorrect, please re-enter your details"

    def account(self, Email=None, Password=None, FirstName=None, LastName=None, PhoneNumber=None):
        
        # Gets the account details, and gets the nearest booking that is set as not arrived and isn't in the past.
        try:

            Email = session["Email"]

            details = findcustomerdetails(Email=Email, CustomerID = "")

            CustomerID = details[0]
            FirstName = details[1]

            Date = date.today()

            activebookings = "SELECT Booking.Date, Booking.Time FROM Booking WHERE Booking.Date >= (?) AND Booking.Arrived = 'False' AND Booking.CustomerID = (?) ORDER BY Booking.Date ASC"
            try:
                q.execute(activebookings, [Date, CustomerID])
                bookings = q.fetchone()
                NearestBookingDate = bookings[0]
                NearestBookingTime = bookings[1]

                return True, None, FirstName, NearestBookingDate, NearestBookingTime

            except Exception as error:
                app.logger.info(f"Either no bookings were found, or an error orrcured: {error}")

                return True, None, FirstName, "None", "None"

        except Exception as error:
            return False, f"Error while grabbing user's details or the upcoming bookings: {error}", None, None, None

    def EditDetails(self, NewFirst, NewLast, NewPhone, Edit, Email=None, Password=None, FirstName=None, LastName=None, PhoneNumber=None):

        #This function is called when the user open the edit account details page, the "Edit" variable is either 1 or 0, if it is 0, the function gets the customer's account details, if is is 1, the edited details are checked against some validation requirements, then the record is edited using the new details. 
        
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

                #app.logger.info(f"Error while validating details: {error}")

                return False, f"Error while validating details: {error}"

            try:

                CustomerID = session["CustomerID"]

                details = (NewFirst, NewLast, NewPhone, CustomerID)

                #app.logger.info(f"Editing account details, New name = {NewFirst} {NewLast}, New phone = {NewPhone}, CustomerID = {CustomerID}")

                update = "UPDATE Customer SET FirstName = (?), LastName = (?), PhoneNumber = (?) WHERE CustomerID = (?)"

                q.execute(update, details)

                sql.commit()

                return True, None
            except Exception as error:
                return False, f"Error while updating account details: {error}"

    def DeleteAccount(self):
        
        #This function is called when the account is to be deleted, it deletes all the bookings associated with the account to be deleted as well as the account being deleted. 
        CustomerID = session["CustomerID"]

        try:

            DeleteBookings = "DELETE FROM Booking WHERE CustomerID = (?)"

            q.execute(DeleteBookings, [CustomerID])

        except Exception as error:

            return False, f"Error while delete customer bookings: {error}"

        try:
            
            sendEmail(session["Email"], "DeleteAccount")

            DeleteAccount = "DELETE FROM Customer WHERE CustomerID = (?)"

            q.execute(DeleteAccount, [CustomerID])
            sql.commit()

            #app.logger.info("Account succesfully deleted")
            
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
        
        #This function is called on the first page of the new bookings page, it checks if bookings are closed on that date and checks to see it's not in the past, and then finds if the date is the weekend or not, causing the select session page to be different depending on the variable session['WeekdayBooking'].
        try:
            
            if bookingclosed(self.BookingDate):
                
                return False, "Bookings are Closed this day"
                
            else:

                if checkdate(self.BookingDate) == False:
                    # If booking date is in the past
                    return False, "Please book a date in the future!"

                elif isweekday(self.BookingDate) == True:
                    # If booking date is on a weekday
                    #app.logger.info("Booking is being made on a weekday")
                    session["WeekdayBooking"] = True

                else:
                    # If booking date is on the weekend
                    #app.logger.info("Booking is beng made on the weekend")
                    session["WeekdayBooking"] = False

                session["BookingDate"] = self.BookingDate

        except Exception as error:

            return False, f"Error while checking booking date validility: {error}"

        return True, None

    def SelectSessionType(self, option):
        
        # This function uses the passed "option" variable to determine the session the customer is booking, then redirecting the user to the correct page.

        #app.logger.info(f"Option: {option}")

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
        
        #This function checks what time the play session is being booked in, this is then used to find out if the maximum number of bookings has been reached, it also gets the SessionID from the database to be stored and used later.

        BookingDate = session["BookingDate"]
        CustomerID = session["CustomerID"]

        session["BookingTime"] = self.BookingTime
        session["numberadults"] = self.NumberOfAdults
        session["numberchildren"] = self.NumberOfChildren

        if checkdate(Date=BookingDate) == False:

            return False, "Please book a date in the future!"

        if self.BookingTime == "10:00-14:00":

            #app.logger.info("Weekday Play AM = True")
            get = "SELECT SessionID FROM Session WHERE SessionType = (?)"
            q.execute(get, ["Weekday Play AM"])

            session["PlaySessionType"] = "Weekday Play AM"

        else:

            #app.logger.info("Weekday Play PM = True")
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

        #app.logger.info(f"Details: CID: {CustomerID}, SID: {CustomerID}, Date: {BookingDate}, Exists: {exists}")

        if exists < 75:
            #app.logger.info("Session is open, redirecting to confirm booking page")

            return True, None

        else:
            #app.logger.info("Too many bookings for Weekday Play Session: {BookingDate}, {BookingTime}")

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

            #app.logger.info("Weekend Play AM = True")
            get = "SELECT SessionID FROM Session WHERE SessionType = (?)"
            q.execute(get, ["Weekend Play AM"])

            session["PlaySessionType"] = "Weekend Play AM"

        else:

            #app.logger.info("Weekend Play PM = True")
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
            #app.logger.info("Session is open, redirecting to confirm booking page")

            return True, None

        else:
            #app.logger.info("Too many bookings for Weekday Play Session: {BookingDate}, {BookingTime}")

            return False, "Sorry, there are too many bookings for this Weekday Play Session, please book another day or time."

    def Party(self):

        CustomerID = session["CustomerID"]
        BookingDate = session["BookingDate"]

        session["BookingTime"] = self.BookingTime
        session["numberadults"] = self.NumberOfAdults
        session["numberchildren"] = self.NumberOfChildren

        #app.logger.info(f"{self.BookingTime}")

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
            #app.logger.info(f"Details: CID: {CustomerID}, SID: {self.SessionID}, Date: {BookingDate}, Exists: {exists}")

            if exists < 2:

                #app.logger.info("Party Session is open, redirecting to confirm booking page")
                return True, None

            else:

                #app.logger.info("Too many bookings for Party: {BookingDate}, {BookingTime}")

                return False, "Sorry, there are no party booking available for this date or time, please book another day or time."

        except Exception as error:
            return False, f"Error while making party booking: {error}"

    def PrivateHire(self, PrivateHireType):
        
        #This function is similar to those above it, but it checks wether a private hire is available in a different way.

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
            #app.logger.info(f"Looking for private hire booking with and Booking date = {self.BookingDate}")
            q.execute(checkexists, [self.BookingDate])
            exists=q.fetchone()[0]

            if exists == 0:

                session["PrivateHire"] = True

                #app.logger.info("Session is open, redirecting to confirm booking page")

                return True, None

            else:
                return False, "This slot is booked, please book another date!"

        except Exception as error:
            return False, f"Error while making private hire booking: {error}"

    def GetFinalPrice(self, BookingType, PrivateHireType):

        #This function is used to find the final price for the booking being made, it will get the adult and child price from the database using the previously stored sessionID, then using the number of adults and children to workout the total price, unless it is a private hire, where the price will be dependant on the type of private hire being made.
        #It also adds any optional extras selected onto the extra price, returning the final price to be stored in the database when the booking is created.

        try:


            if BookingType != "Private Hire":

                SessionID = session["SessionID"]

                #app.logger.info(SessionID)
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

                #app.logger.info(f"({adultprice} * {NumberAdults} = {adulttotal}) + ({childprice} * {NumberChildren} = {childtotal}) = {Price}")

            elif PrivateHireType == "Adventure Play Private Hire":

                Price = 300.0

            elif PrivateHireType == "Laser Tag Private Hire":

                Price = 200.0

            elif PrivateHireType == "Laser Tag + Adventure Play Private Hire":

                Price = 400.0

            else:

                return False, f"Something went wrong", None

            if self.ExtraNotes == "Buffet":

                Price += 100.0

            if self.ExtraNotes == "PizzaParty":

                Price += 80.0

            if self.ExtraNotes == "LaserParty":

                Price += 50.0

            if self.ExtraNotes == "PartyBags":

                Price += 10.0

            if self.ExtraNotes == "AdultLaser":
                
                Price += 15.0

            session["Price"] = Price

            return True, None, Price

        except Exception as error:
            return False, f"Error while grabbing booking details: {error}", None

    def CreateBooking(self):

        #This function is called when  the booking details have been confirmed and the system is ready to create the booking, it irst makes the extra notes a better, easier to view format by turning it into a string instead of a list. Then it creates the booking using the pre-determine booking data, created earlier in the process, then creates the booking by inserting into the sql.
        try:

            #app.logger.info(f"Making booking with details: CustomerID = {self.CustomerID}, SessionID =  {self.SessionID}, Booking Date = {self.BookingDate}, Booking Time = {self.BookingTime}, Price = {self.BookingPrice}, ExtraNotes = {self.ExtraNotes}")

            #ExtraNotesSTR = ', '.join(self.ExtraNotes)

            new = "INSERT INTO Booking(CustomerID, SessionID, Date, Time, NumberOfChildren, NumberOfAdults, Price, Arrived, ExtraNotes) VALUES (?,?,?,?,?,?,?,'False',?)"
            details = [self.CustomerID, self.SessionID, self.BookingDate, self.BookingTime, self.NumberOfChildren, self.NumberOfAdults, self.BookingPrice, self.ExtraNotes]
            q.execute(new, details)
            sql.commit()

            #app.logger.info(f"Retrieving booking ID, data = {self.CustomerID}, {self.SessionID}, {self.BookingDate}, {self.BookingTime}")

            get = "SELECT BookingID FROM Booking WHERE CustomerID = (?) AND SessionID = (?) AND Date = (?) AND Time = (?)"
            details = (self.CustomerID, self.SessionID, self.BookingDate, self.BookingTime)
            q.execute (get, details)
            fetch = q.fetchone()
            BookingID = fetch[0]

            #app.logger.info(f"BookingID: {BookingID} Redirecting to Manage Booking template")

            session["BookingID"] = BookingID

            return True, None

        except Exception as error:

            return False, f"Error while creating booking: {error}"

    def ManageBooking(self):
        
        #This function is called when the customer wants to view all the bookings they have created, it grabs all the bookings the user has created, where the booking date is the date that day or the future.

        try:

            Date = date.today()

            getactivebookings = "SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID WHERE Booking.CustomerID = ? AND Booking.Date >= ? ORDER BY Booking.Date ASC;"
            q.execute(getactivebookings, [self.CustomerID, Date])
            activebookings = q.fetchall()

            return True, None, activebookings

        except Exception as error:

            return False, f"Error while opening manage booking template: {error}", None

    def DeleteBooking(self):
        
        #This function is called when a booking is to be deleted, using the the BookingID to delete the booking from the database.

        #app.logger.info(f"Deleting Booking with Booking ID: {self.BookingID}")

        DeleteBooking = "DELETE FROM Booking WHERE BookingID = (?)"

        try:
            q.execute(DeleteBooking, [self.BookingID])
            sql.commit()
            #app.logger.info("Booking Deleted Succesfully")

            return True, None

        except Exception as error:

            return False, f"Error while deleting booking: {error}"
        
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
            session["Email"] = Email

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
        session["BookingValid"] = ""


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
            session["Email"] = Email
            session["Phone"] = ""
            session["First"] = ""
            session["Last"] = ""
            session["FirstName"] = ""
            session["LastName"] = ""

            return redirect(url_for("account"))

        else:
            return render_template("error.html", error=f"Error while registering: {error}")

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
    NearestBookingDate = Result[3]
    NearestBookingTime = Result[4]

    if Success:
        return render_template("account.html", First=First, NearestBookingDate=NearestBookingDate, NearestBookingTime=NearestBookingTime)

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
    session["WeekdayBooking"] = False
    session["ExtraNotes"] = ""
    session["BookingValid"] = False


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
    BookingDate = session["BookingDate"]

    # This checks the option grabbed from the html template and redirects the user accordingly.
    if request.method == "POST":
        option = request.form["bookingtype"]

        NewBooking = Booking(CustomerID=None, BookingID=None, SessionID=None, BookingDate=BookingDate, BookingTime=None, NumberOfChildren=None, NumberOfAdults=None, BookingPrice=None, ExtraNotes=None)

        Result = NewBooking.SelectSessionType(option)

        Success = Result[0]
        error = Result[1]
        urlname = Result[2]

        if Success:
            session["BookingValid"] = True
            return redirect(url_for(urlname))

        else:
            session["BookingValid"] = False
            return render_template("error.html", error=error)

    # The variable "WeekdayBooking" is a boolean which tells the booking page if the booking is being made on the weekday or weekend
    else:

        checkexists = "SELECT count(*) FROM Booking WHERE SessionID IN (7, 8, 9) AND Date = (?)"
        #app.logger.info(f"Looking for private hire booking with and Booking date = {BookingDate}")
        q.execute(checkexists, [BookingDate])
        exists=q.fetchone()[0]

        if exists == 0:

            PHBooked = False

        else:
            PHBooked = True

        return render_template("newbooking.html", WeekdayBooking = WeekdayBooking, PHBooked = PHBooked)

@app.route('/account/newbooking/playsession/weekday',  methods=["POST","GET"])
def weekdayplaysession():

    if customerloggedin() == False:
        return redirect(url_for("index"))

    if session["BookingValid"] == "False":
        return redirect(url_for("newbooking"))
    
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
    
    if session["BookingValid"] == False:
        return redirect(url_for("newbooking"))

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
    
    if session["BookingValid"] == False:
        return redirect(url_for("newbooking"))

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
    
    if session["BookingValid"] == False:
        return redirect(url_for("newbooking"))

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
    
    if session["BookingValid"] == False:
        return redirect(url_for("newbooking"))

    PrivateHireType = session["PrivateHireType"]
    BookingType = session["BookingType"]

    if request.method == "POST":

        try:

            ExtraNotes = request.form.getlist("Extra")
            #app.logger.info(f"Extras before: {ExtraNotes}")
            ExtraNotes = ", ".join(ExtraNotes)
            #app.logger.info(f"Extras after: {ExtraNotes}")
            
            session["ExtraNotes"] = ExtraNotes

            #app.logger.info(f"Extras: {ExtraNotes}")

        except Exception as error:
            app.logger.info(f"Either no Extra Notes selected or an error happened: {error}")

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
        ExtraNotes = request.form["ExtraNotes"]
        BookingPrice = request.form["BookingPrice"]

        session["BookingPrice"] = BookingPrice
        session["BookingID"] = BookingID
        session["BookingDate"] = BookingDate
        session["BookingTime"] = BookingTime
        session["SessionType"] = SessionType
        session["ExtraNotes"] = ExtraNotes

        #app.logger.info(f"Session Type: {SessionType}")

        return redirect(url_for("booking"))

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
    ExtraNotes = session["ExtraNotes"]
    BookingPrice = session["BookingPrice"]

    if request.method == "POST":
        return redirect(url_for("deletebooking"))

    else:

        return render_template("booking.html", BookingID = BookingID, BookingDate = BookingDate, BookingTime = BookingTime, ExtraNotes = ExtraNotes, SessionType = SessionType, BookingPrice = BookingPrice)

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

        NewBooking = Booking(CustomerID=None, BookingID = None, SessionID=SessionID, BookingDate=None, BookingTime=None,NumberOfChildren=NumberOfChildren, NumberOfAdults=NumberOfAdults, BookingPrice=None, ExtraNotes=ExtraNotes)

        Result = NewBooking.GetFinalPrice(BookingType=BookingType, PrivateHireType=PrivateHireType)

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
        session["BookingValid"] = False
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

@app.route("/centerinfo/contact")
def contact():
    return render_template("centredetails/contact.html")

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

                #app.logger.info(f"Manager with Username {Username} found, checking password then redirecting to account page")

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

                #app.logger.info(f"Manager with Username {Username} does not exist, redirecting to error page")

                return render_template('/error.html', error="Account Doesn't Exist")

    else:

        return render_template("manager/managerlogin.html")

@app.route("/manager/account", methods=["POST","GET"])
def manageraccount():
    
    if managerloggedin() == False:
        return redirect(url_for("index"))

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
    
    Date = date.today()
    
    if managerloggedin() == False:
        return redirect(url_for("index"))
    
    if request.method == "POST":

        if "Filter" in request.form != "Filter":
            
            StartDate = request.form.get("StartDate")
            EndDate = request.form.get("EndDate")
            Filter = request.form.get("Filter")

            #app.logger.info(f"{StartDate} {EndDate} {Filter}")

            if Filter == "all" and StartDate and EndDate:
                # Filter by date range
                getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults, Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Booking.Date BETWEEN '{StartDate}' AND '{EndDate}' ORDER BY Booking.Date ASC"
            elif Filter != "all" and StartDate and EndDate:
                # Filter by type and date range

                getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults , Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Session.SessionType = '{Filter}' AND Booking.Date BETWEEN '{StartDate}' AND '{EndDate}' ORDER BY Booking.Date ASC"
                
            elif Filter != "all":
                # Filter by type only
                if  Filter == "Private Hire":
                    getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults , Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Session.SessionID = 8 OR Session.SessionID = 9 OR Session.SessionID = 10 AND Booking.Date >= '{Date}' ORDER BY Booking.Date ASC"
                else:
                    getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults , Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Session.SessionType = '{Filter}' AND Booking.Date >= '{Date}' ORDER BY Booking.Date ASC"
            elif StartDate and EndDate:
                # Filter by date range only
                getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults, Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Booking.Date BETWEEN '{StartDate}' AND '{EndDate}' AND Booking.Date >= '{Date}' ORDER BY Booking.Date ASC"
            
            elif StartDate == "" and EndDate != "":
                
                getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults , Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Session.SessionType = '{Filter}' AND Booking.Date > '{StartDate}' ORDER BY Booking.Date ASC"
            
            elif StartDate != "" and EndDate == "":
                
                getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults , Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID WHERE Session.SessionType = '{Filter}' AND Booking.Date < '{EndDate}' ORDER BY Booking.Date ASC"
                
            else:
                getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults, Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID AND Booking.Date >= '{Date}' ORDER BY Booking.Date ASC"

            q.execute(getactivebookings)
            activebookings = q.fetchall()
            #app.logger.info(f"{getactivebookings} ,{activebookings}")

            return render_template("manager/selectbooking.html", activebookings=activebookings)

        else:

            #app.logger.info("Redirecting to booking page")

            BookingID = request.form["BookingID"]
            BookingDate = request.form["BookingDate"]
            BookingTime = request.form["BookingTime"]
            SessionType = request.form["SessionType"]
            ExtraNotes = request.form["ExtraNotes"]
            BookingPrice = request.form["BookingPrice"]
            NumberAdults = request.form["NumberAdults"]
            NumberChildren = request.form["NumberChildren"]
            FirstName = request.form["FirstName"]
            LastName = request.form["LastName"]
            
            #app.logger.info(f"BookingID: {BookingID} BookingDate: {BookingDate} BookingTime: {BookingTime} SessionType: {SessionType} ExtraNotes: {ExtraNotes} BookingPrice: {BookingPrice} NumberAdults: {NumberAdults} NumberChildren: {NumberChildren} FirstName: {FirstName} LastName: {LastName}")

            session["BookingID"] = BookingID
            session["BookingPrice"] = BookingPrice
            session["BookingDate"] = BookingDate
            session["BookingTime"] = BookingTime
            session["SessionType"] = SessionType
            session["NumberAdults"] = NumberAdults
            session["NumberChildren"] = NumberChildren
            session["ExtraNotes"] = ExtraNotes
            session["FirstName"] = FirstName
            session["LastName"] = LastName

            return redirect(url_for("managerbooking"))

    else:
        try:

            getactivebookings = f"SELECT Booking.BookingID, Booking.Date, Booking.Time, Session.SessionType, Booking.ExtraNotes, Booking.Price, Booking.NumberOfChildren, Booking.NumberOfAdults, Customer.FirstName, Customer.LastName, Booking.Arrived FROM Booking INNER JOIN Session ON Booking.SessionID = Session.SessionID INNER JOIN Customer ON Booking.CustomerID = Customer.CustomerID AND Booking.Date >= '{Date}' ORDER BY Booking.Date ASC"
            q.execute(getactivebookings)
            activebookings = q.fetchall()

            return render_template("manager/selectbooking.html", activebookings=activebookings)

        except Exception as error:
            return render_template("error.html", error=error)

@app.route("/manager/managebooking/booking", methods=["POST", "GET"])
def managerbooking():
    
    if managerloggedin() == False:
        return redirect(url_for("index"))

    BookingID = session["BookingID"]
    BookingDate = session["BookingDate"]
    BookingTime = session["BookingTime"]
    SessionType = session["SessionType"]
    ExtraNotes = session["ExtraNotes"]
    BookingPrice = session["BookingPrice"]
    NumberAdults = session["NumberAdults"]
    NumberChildren = session["NumberChildren"]
    FirstName = session["FirstName"]
    LastName = session["LastName"]

    #app.logger.info(f"BookingID: {BookingID} BookingDate: {BookingDate} BookingTime: {BookingTime} SessionType: {SessionType} ExtraNotes: {ExtraNotes} BookingPrice: {BookingPrice} NumberAdults: {NumberAdults} NumberChildren: {NumberChildren} FirstName: {FirstName} LastName: {LastName} ")

    if request.method == "POST":

        #app.logger.info(f"Deleting Booking with Booking ID: {BookingID}")

        DeleteBooking = "DELETE FROM Booking WHERE BookingID = (?)"

        try:
            q.execute(DeleteBooking, [BookingID])
            sql.commit()
            #app.logger.info("Booking Deleted Succesfully")

            return redirect(url_for("managereditbooking"))

        except Exception as error:
            return render_template("/error.html", error=error)

    else:

        return render_template("manager/booking.html", BookingID = BookingID, BookingDate = BookingDate, BookingTime = BookingTime, ExtraNotes = ExtraNotes, SessionType = SessionType, BookingPrice = BookingPrice, NumberAdults = NumberAdults, NumberChildren = NumberChildren, FirstName = FirstName, LastName = LastName)

@app.route('/manager/editcustomer', methods=["POST","GET"])
def managereditcustomer():
    
    if managerloggedin() == False:
        return redirect(url_for("index"))
    
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
    
    if managerloggedin() == False:
        return redirect(url_for("index"))

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

                        #app.logger.info(f"Error while validating details: {error}")

                        return render_template("error.html", error=error)
                        #return False, f"Error while validating details: {error}"
                    else:

                        details = (NewFirst, NewLast, NewPhone, CustomerID)

                        #app.logger.info(f"Editing account details, New name = {NewFirst} {NewLast}, New phone = {NewPhone}, CustomerID = {CustomerID}")

                        update = "UPDATE Customer SET FirstName = (?), LastName = (?), PhoneNumber = (?) WHERE CustomerID = (?)"

                        q.execute(update, details)

                        sql.commit()

                        return redirect(url_for("managereditcustomer"))

                else:

                    return redirect(url_for("managereditcustomer"))

            except Exception as error:

                return render_template("error.html", error=error)

        else:
            #app.logger.info(f"Deleting Customer with Customer ID: {CustomerID}")

            DeleteCustomer = "DELETE FROM Customer WHERE CustomerID = (?)"

            try:
                q.execute(DeleteCustomer, [CustomerID])
                sql.commit()
                #app.logger.info("Customer Deleted Succesfully")
                return redirect(url_for("managereditcustomer"))

            except Exception as error:
                return render_template("error.html", error=error)

    else:

        return render_template("manager/customer.html", CustomerID = CustomerID, FirstName = First, LastName = Last, Email = Email, PhoneNumber = Phone)

@app.route("/manager/manageholidays", methods=["POST", "GET"])
def manageholidays():
    
    if managerloggedin() == False:
        return redirect(url_for("index"))

    if request.method == "POST":

        HolidayID = request.form["HolidayID"]

        deleteholiday = "DELETE FROM Holiday WHERE HolidayID = (?)"
        
        q.execute(deleteholiday, [HolidayID])
        
        return redirect(url_for("manageholidays"))

    else:

        Date = date.today()

        getholidays = "SELECT * FROM Holiday WHERE EndDate >= (?) ORDER BY StartDate ASC"
        q.execute(getholidays, [Date])

        holidays = q.fetchall()

        #app.logger.info(f"Returned holidays: {holidays}")

        return render_template("/manager/manageholidays.html", holidays = holidays)

@app.route("/manager/newholiday", methods=["POST", "GET"])
def createholiday():
    
    if managerloggedin() == False:
        return redirect(url_for("index"))

    if request.method == "POST":

        try:
            StartDate = request.form["startdate"]
            EndDate = request.form["enddate"]
            Name = request.form["name"]
            Description = request.form["description"]
            
            if len(Description) >= 50 or len(Name) >= 30:
                
                return render_template("error.html", error=f"Description or holiday name is too long")
            #app.logger.info(f"Start Date: {StartDate} End Date: {EndDate} Name: {Name} Description: {Description}")

            if StartDate == "" or EndDate == "" or Name == "":

                return render_template("error.html", error="You must not leave any field blank!")

            else:

                addholiday = "INSERT INTO Holiday (Name, StartDate, EndDate, Description) VALUES (?,?,?,?)"

                q.execute(addholiday, [Name, StartDate, EndDate, Description])
                sql.commit()
            
                return redirect(url_for("manageholidays")) 

        except Exception as error:

            return render_template("error.html", error=error)

    else:
        return render_template("manager/newholiday.html")

@app.route("/manager/arrived", methods=["POST", "GET"])
def mark_arrived():
    
    if managerloggedin() == False:
        return redirect(url_for("index"))

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
    
@app.route("/manager/selectsession", methods=["POST", "GET"])
def selectsession():
        
        if managerloggedin() == False:
            return redirect(url_for("index"))
    
        if request.method == "POST":
    
            SessionID = request.form["SessionID"]
            SessionName = request.form["SessionName"]
            AdultPrice = request.form["AdultPrice"]
            ChildPrice = request.form["ChildPrice"]   
    
            session["SessionID"] = SessionID
            session["SessionName"] = SessionName
            session["AdultPrice"] = AdultPrice
            session["ChildPrice"] = ChildPrice
            
    
            return redirect(url_for("managereditsession"))
    
        else:
            
            getsessions = "SELECT * FROM Session ORDER BY SessionID ASC"
            q.execute(getsessions)
            
            activesessions = q.fetchall()
            
            app.logger.info(f"Active Sessions: {activesessions}")
    
            return render_template("manager/selectticket.html", activetickets = activesessions)

# ---------------------------------------------------------------------------------------------------------------- #

@app.route("/account/developer")
def devtest():
    
    sendEmail("benmercer76@btinternet.com", "Test")

    i = 0

    SessionVars = ["CustomerID","Email","Phone","First","Last","FirstName","LastName","NumberChildren","NumberAdults","BookingPrice","ExtraNotes","SessionType","BookingTime","BookingDate","BookingID","ManagerID","ManagerUsername","PrivateHireType","numberadults","numberchildren","WeekdayBooking","PlaySession","PrivateHire","Party","PlaySessionType","Price","PartyType","SessionID"]
    SessionVarsFound = []

    # This is grabbing every session variable with the names stated in the "SessionVars" list, then showing it in the html template
    for i in range(len(SessionVars)):

        try:

            data = session[SessionVars[i]]

            if data == "":

                SessionVarsFound.append(f"{SessionVars[i]} : Null")

            else:

                SessionVarsFound.append(f"{SessionVars[i]} : {data}")

            i + 1

        except:

            i + 1

    #app.logger.info(SessionVarsFound)

    return render_template("devtest.html", SessionVarsFound=SessionVarsFound)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
