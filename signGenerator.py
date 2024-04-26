import tkinter
from tkinter import colorchooser, messagebox
from PIL import ImageGrab,ImageTk,Image
import tkinter.font as tkFont
from hashlib import sha256
import pymongo
import re
from bson.binary import Binary
from io import BytesIO


class CreateMySignApp:
    #initializing helper variables in constructor
    def __init__(self):
        #creating main Window
        self.window = self.createMainWindow()
        self.canvas = None
        self.color = "black"
        self.creating_sign = False
        self.pen_x = 0
        self.pen_y = 0
        self.email_entry = None
        self.password_entry = None
        self.login_window = None
        self.isLoggedIn = False
        self.useremail = None
        self.client = None
        self.scroll_frame = None
        self.login_create_account_btn = None
        self.input_box = None
        self.font_dropdown = None
        self.font_size_dropdown = None
        self.createGUI()
        
    #Function to create Main window
    def createMainWindow(self):
        window = tkinter.Tk()
        window.title("Create My Sign")
        window.config(bg="#e6e3e3")
        window.minsize(width=1000, height=1000)
        heading = tkinter.Label(window, text="Welcome to Make My Sign", font=("Helvetica", 20, "bold"))
        heading.place(x=290, y= 30)
        window.protocol("WM_DELETE_WINDOW", self.destroyWindow)

        return window

    def destroyWindow(self):
        if not (self.client is None):
                self.client.close()
                self.client = None
        self.window.destroy()



    #Function which places button and canvas on the main screen by calling helper functions
    def createGUI(self):
        self.createCanvas()
        self.createButtons()
        self.createInput()
        self.window.mainloop()

    #creating canvas
    def createCanvas(self):
        self.canvas = tkinter.Canvas(self.window, width=650, height=500, borderwidth=2, relief="solid")
        self.canvas.place(x=150, y=100)
        self.canvas.bind("<Button-1>", self.onCanvasClick)
        self.canvas.bind("<B1-Motion>", self.onCanvasMotion)

    #creating fontsize,download,rest and font style,login,colorpicker buttons
    def createButtons(self):
        self.createDownloadButton()
        self.createResetButton()
        self.createFontDropdown()
        self.createFontSizeDropDown()
        self.createLoginButton()
        self.createColorPickerButton()

    #login button
    def createLoginButton(self):
        self.login_create_account_btn = tkinter.Button(self.window, text="Sign In/ Sign Up", command=self.createLoginFrame, width=15, height=2)
        self.login_create_account_btn.place(x=850, y=50)

    #Enter sign text entry
    def createInput(self):
        input_label = tkinter.Label(self.window, text="Enter Your Sign : ")
        input_label.place(x=570, y=670)
        self.input_box = tkinter.Entry(self.window, width=15)
        self.input_box.place(x=570, y=700)
        self.input_box.bind("<KeyRelease>", self.getInputValue)

    #font style dropdown
    def createFontDropdown(self):
        font_dropdown_label = tkinter.Label(self.window, text="Font Styles : ")
        font_dropdown_label.place(x=690, y=670)
        font_names = tkFont.families()
        self.font_dropdown = tkinter.StringVar()
        self.font_dropdown.set(font_names[0])
        font_dropdown_menu = tkinter.OptionMenu(self.window, self.font_dropdown, *font_names, command=self.changeFonts)
        font_dropdown_menu.place(x=690, y=700)

    #font size dropdown
    def createFontSizeDropDown(self):
        font_size_label = tkinter.Label(self.window, text="Font Size : ")
        font_size_label.place(x=820, y=670)
        font_sizes = [8, 10, 12, 14, 16, 18, 20, 22, 24]
        self.font_size_dropdown = tkinter.IntVar()
        self.font_size_dropdown.set(12)  # Default font size
        font_size_dropdown_menu = tkinter.OptionMenu(self.window, self.font_size_dropdown, *font_sizes, command=self.changeFonts)
        font_size_dropdown_menu.place(x=820, y=700)
    
    #function to change font style and font size on changing font and size
    def changeFonts(self,*args):
        font_name = self.font_dropdown.get()
        font_size = self.font_size_dropdown.get()  
        try:
            value = self.input_box.get()
            self.canvas.delete("all")
            x = self.canvas.winfo_width() // 2
            y = self.canvas.winfo_height() // 2
            self.creating_sign = True
            #recreating sign with changed style and size
            self.canvas.create_text(x, y, text=value, font=(font_name, font_size), fill=self.color, tags=("text",))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get input value: {str(e)}")
    #Color picker
    def createColorPickerButton(self):
        colorLabel = tkinter.Label(self.window, text="Choose Sign Color : ")
        colorLabel.place(x=450,y=670)
        color_button = tkinter.Button(self.window, text="Choose Color", command=self.chooseColor, width=15, height=2)
        color_button.place(x=430, y=700)

    #download button
    def createDownloadButton(self):
        downloadLabel = tkinter.Label(self.window, text="Click Here To Download : ")
        downloadLabel.place(x=290,y=670)
        download_button = tkinter.Button(self.window, text="Download", command=self.onDownloadClick, width=15, height=2)
        download_button.place(x=290, y=700)
    #rest button
    def createResetButton(self):
        resetLabel = tkinter.Label(self.window, text="Click Here To Reset : ")
        resetLabel.place(x=150,y=670)
        reset_button = tkinter.Button(self.window, text="Reset", command=self.onResetClick, width=15, height=2)
        reset_button.place(x=150, y=700)

    #function to create login window
    def createLoginFrame(self):
        self.login_window = tkinter.Toplevel(self.window)
        self.login_window.geometry("300x200")
        self.login_window.title("Login Window")
        email_label = tkinter.Label(self.login_window, text="Email")
        email_label.grid(row=1, column=0, padx=5, pady=5)
        self.email_entry = tkinter.Entry(self.login_window)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        password_label = tkinter.Label(self.login_window, text="Password")
        password_label.grid(row=2, column=0, padx=5, pady=5)
        self.password_entry = tkinter.Entry(self.login_window, show='*')
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        login_button = tkinter.Button(self.login_window, text="Login", command=self.login)
        login_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        create_account_button = tkinter.Button(self.login_window, text="Create Account", command=self.createAccount)
        create_account_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    #function to DB connection object
    def getDBConnection(self):
        try:
            self.client = pymongo.MongoClient("mongodb://localhost:27017/")
            db = self.client["generatemysign"]
            return db
        except pymongo.errors.ConnectionError:
            messagebox.showerror("Error", "Failed to connect to the database.")
            return None

    #validating user credentials
    def login(self):
        self.useremail = self.email_entry.get()
        password = self.password_entry.get()
        client = self.getDBConnection()
        users_collection = client["users"]
        
        if users_collection is None:
            return False

        user = users_collection.find_one({"email": self.useremail})

        if user is None:
            messagebox.showerror("Error", "Invalid Credentials")
            return False

        #if correct credentials then displaying username and user previous download signs image
        if sha256(password.encode('utf-8')).hexdigest() == user["password"]:
            messagebox.showinfo("Success", "Login Successfully.")
            self.login_window.destroy()
            self.login_create_account_btn.config(text="Logout",command=self.logout)
            self.greeting_label = tkinter.Label(self.window, text=f"Hello, {self.useremail}!")
            self.greeting_label.place(x=750, y=60)
            self.retrieveSigns(self.useremail)
            self.isLoggedIn = True
            return True
        else:
            messagebox.showerror("Error", "Invalid Credentials")
            return False
    
    #logut function. 
    def logout(self):
        if messagebox.askokcancel("Logout", "Are you sure you want to logout?"):
            self.login_create_account_btn.config(text="Sign In/ Sign Up", command=self.createLoginFrame)
            self.greeting_label.destroy()
            self.canvas.delete("all")
            self.input_box.delete(0, "end")
            self.scroll_frame.destroy()
            if not (self.client is None):
                self.client.close()
                self.client = None


    #Create account function
    def createAccount(self):
        client = self.getDBConnection()
        users_collection = client["users"]

        if users_collection is None:
            return False

        userpassword = self.password_entry.get()
        useremail = self.email_entry.get()

        #if user alredy exists throwing error.
        user = users_collection.find_one({"email": useremail})
        if user is not None:
            messagebox.showerror("Error", "User already exists!")
            return
        
        #Checking password criteria. One special character , one cap letter and minimum 8 characrers.
        if len(userpassword) < 8:
            messagebox.showerror("Error", "Password should be at least 8 characters long!")
            return
        elif not re.search(r'[A-Z]', userpassword):
            messagebox.showerror("Error", "Password should have at least one uppercase letter!")
            return
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', userpassword):
            messagebox.showerror("Error", "Password should have at least one special character!")
            return

        #encoding password with sha256 module
        userPasswordHash = sha256(userpassword.encode('utf-8')).hexdigest()
        user = {"password": userPasswordHash, "email": useremail}
        users_collection.insert_one(user)
        messagebox.showinfo("Success", "Your account has been created.")
        self.login_window.destroy()

    #changig colors 
    def chooseColor(self):
        self.color = colorchooser.askcolor(title="Choose color")[1]
        if self.creating_sign:
            self.changeFonts()

    #initializing pens point
    def onCanvasClick(self, event):
        if not self.creating_sign:
            self.pen_x = event.x
            self.pen_y = event.y

    #capturing the user sign drawing.
    def onCanvasMotion(self, event):
        if not self.creating_sign:
            self.canvas.create_line(self.pen_x, self.pen_y, event.x, event.y, fill=self.color, width=5, capstyle=tkinter.ROUND)
            self.pen_x = event.x
            self.pen_y = event.y
    
    #Download sign function
    def onDownloadClick(self):
        try:
            x = self.canvas.winfo_rootx() + 100
            y = self.canvas.winfo_rooty() + 35
            x1 = x + 600
            y1 = y + 600

            #grabbing sign from canvas and storing it.
            image = ImageGrab.grab(bbox=(x, y, x1, y1))
            image.save("sign.png")
            messagebox.showinfo("Success","Sign downloaded successfully.")

            #if logged in then displaying all the previous and current sing in separate window
            if self.isLoggedIn:
                self.storeSignImage(self.useremail)
                self.scroll_frame.destroy()
                self.retrieveSigns(self.useremail)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download the image: {str(e)}")

    #reseting the canvas
    def onResetClick(self):
        try:
            self.canvas.delete("all")
            self.creating_sign = False
            self.input_box.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset: {str(e)}")

    #creating sign using text written by user
    def getInputValue(self, event):
        try:
            value = self.input_box.get()
            font_name = self.font_dropdown.get()
            font_size = self.font_size_dropdown.get()
            font = tkFont.Font(family=font_name)
            self.canvas.delete("all")
            x = self.canvas.winfo_width() // 2
            y = self.canvas.winfo_height() // 2
            self.creating_sign = True
            self.canvas.create_text(x, y, text=value, font=(font_name, font_size), fill=self.color, tags=("text",))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get input value: {str(e)}")

    #storing sign image in DB
    def storeSignImage(self,useremail):
        try:
            client = self.getDBConnection()
            sign_collections = client["signCollection"]
            with open('sign.png', "rb") as f:
                image_binary = Binary(f.read())
            sign_collections.insert_one({"userEmail": useremail, "signImage": image_binary})
        except Exception as e:
            messagebox.showerror("Error", f"Failed to store image in database: {str(e)}")

    #retrieving image from db.
    def retrieveSigns(self,useremail):
        try:
            images = []
            client = self.getDBConnection()
            sign_collections = client["signCollection"]
            for image_doc in sign_collections.find({"userEmail": useremail}):
                signImage = image_doc["signImage"]
                image = Image.open(BytesIO(signImage))
                photo = ImageTk.PhotoImage(image)
                images.append(photo)
            #displaying image on separate window
            self.displaySigns(images)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve images: {str(e)}")

    #function to display images
    def displaySigns(self, images):
        self.scroll_frame = tkinter.Toplevel(self.window)
        self.scroll_frame.geometry("700x700")
        self.scroll_frame.title("Your Signs")

        canvas = tkinter.Canvas(self.scroll_frame, bg="#e6e3e3")
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tkinter.Scrollbar(self.scroll_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        inner_frame = tkinter.Frame(canvas, bg="#e6e3e3")
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        for idx, image in enumerate(images):
            signImage = tkinter.Label(inner_frame,image=image)
            signImage.image = image
            signImage.grid(row=idx + 1, column=0, padx=10, pady=10)
    
    #closing DB connection
    def __del__(self):
        if not (self.client is None) :
            if self.client:
                self.client.close()
                self.client = None

#creating a object
app = CreateMySignApp()
