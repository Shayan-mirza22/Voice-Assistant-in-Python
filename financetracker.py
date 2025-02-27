#  Design and implement a personal finance tracker that allows users to manage their income, expenses, and budget. The application should have the following features: o A command-line interface (CLI) for user interaction. o Options to add, view, and delete transactions. o Budget tracking with monthly and yearly summaries. o Data persistence using SQLite or a CSV file. o Exception handling and input validation. 

from tkinter import *
import sqlite3
import time
from datetime import datetime
from tabulate import tabulate
#conn = sqlite3.connect(":memory:")
# Connect to the database
conn = sqlite3.connect("Users.db")
c = conn.cursor()

# Create users table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )''')

# Table for storing income for each user
c.execute('''CREATE TABLE IF NOT EXISTS user_income (
                user_id INTEGER,
                income REAL NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')
# Table for storing expense categories and their corresponding budget
c.execute('''CREATE TABLE IF NOT EXISTS expense_categories (
                user_id INTEGER,
                category TEXT NOT NULL,
                budget REAL NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')
#c.execute("ALTER TABLE expense_categories ADD COLUMN mdate TEXT")
#c.execute("ALTER TABLE expense_categories ADD COLUMN ydate TEXT")
# Commit and close the connection

conn.commit()
conn.close()

root = Tk()
root.configure(bg='#1E1E1E')
root.title("FS22.pk Finance Tracker.")
root.geometry("800x800")  # Set window size

def Greetings():
    current_time = time.localtime() 
    current_hour = current_time.tm_hour
# Determine the appropriate greeting based on the hour of the day
    if 5 <= current_hour < 12:
      greeting = "GOOD MORNING!"
    elif 12 <= current_hour < 18:
      greeting = "GOOD AFTERNOON."
    else:
      greeting = "GOOD NIGHT!"
    gr_label = Label(root, text=greeting, fg="#FFD700", bg='#1E1E1E', font=("Helvetica Neue", 12))
    gr_label.place(x=630, y=70)

# Global list to hold references to the widgets
widgets = []

def hide_widgets():
    for widget in widgets:
        widget.place_forget()

# Welcome Label
wel_label = Label(root, text="FS22.pk", fg="#FFD700", bg='#1E1E1E', font=("Helvetica", 26, "bold"))
wel_label.place(x=300, y=140)
widgets.append(wel_label)

wel_label_sub = Label(root, text='Your Financial Journey made easy.', fg="#FFD700", bg='#1E1E1E', font=("Helvetica Neue", 10, "italic"))
wel_label_sub.place(x=300, y=180)
widgets.append(wel_label_sub)

log_label = Label(root, text='Enter Email Address:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
log_label.place(x=290, y=240)
widgets.append(log_label)

log_entry = Entry(root)
log_entry.place(x=290, y=270, width=230, height=30)
widgets.append(log_entry)

log_label1 = Label(root, text='Enter Password:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
log_label1.place(x=290, y=320)
widgets.append(log_label1)

log_entry1 = Entry(root, show='*')
log_entry1.place(x=290, y=350, width=230, height=30)
widgets.append(log_entry1)

log_button = Button(root, text='Log In', fg="#CCCCCC", bg='#3A3A3A', width=10, cursor='hand2', command=lambda: login_function(log_entry.get(), log_entry1.get()))
log_button.place(x=360, y=405)
widgets.append(log_button)

sign_label = Label(root, text="Don't have an account?", fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
sign_label.place(x=310, y=460)
widgets.append(sign_label)

sign_label1 = Label(root, text='Sign Up', fg='#0000FF', bg='#1E1E1E', font=("Helvetica Neue", 10, "underline"), cursor='hand2')
sign_label1.place(x=450, y=460)
widgets.append(sign_label1)

con_label = Label(root, text='Contact Us', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10, 'underline'), cursor='hand2')
con_label.place(x=670, y=600)
widgets.append(con_label)

con_label1 = Label(root, text='Terms of Policy', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10, 'underline'), cursor='hand2')
con_label1.place(x=657, y=620)
widgets.append(con_label1)

# Bind the Sign Up label
sign_label1.bind("<Button-1>", lambda e: Sign_function())

def Sign_function():
    hide_widgets()  # Hide existing widgets
    
    wel_label = Label(root, text="FS22.pk", fg="#FFD700", bg='#1E1E1E', font=("Helvetica", 26, "bold"))
    wel_label.place(x=300, y=100)
    widgets.append(wel_label)

    wel_label_sub = Label(root, text='Your Financial Journey made easy.', fg="#FFD700", bg='#1E1E1E', font=("Helvetica Neue", 10, "italic"))
    wel_label_sub.place(x=300, y=140)
    widgets.append(wel_label_sub)

    name_label = Label(root, text='Enter your name:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    name_label.place(x=290, y=200)
    widgets.append(name_label)

    global name_entry
    name_entry = Entry(root)
    name_entry.place(x=290, y=230, width=230, height=30)
    widgets.append(name_entry)

    email_label = Label(root, text='Enter Email Address:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    email_label.place(x=290, y=280)
    widgets.append(email_label)
    
    global email_entry
    email_entry = Entry(root)
    email_entry.place(x=290, y=310, width=230, height=30)
    widgets.append(email_entry)

    pas_label = Label(root, text='Enter Password:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    pas_label.place(x=290, y=360)
    widgets.append(pas_label)

    global pas_entry
    pas_entry = Entry(root, show='*')
    pas_entry.place(x=290, y=390, width=230, height=30)
    widgets.append(pas_entry)

    global income_entry
    income_label = Label(root, text='Enter your monthly income:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    income_label.place(x=290, y=440)
    income_entry = Entry(root)
    income_entry.place(x=290, y=470, width=230, height=30)
    widgets.append(income_label)
    widgets.append(income_entry)


    global sign_button
    sign_button = Button(root, text='Sign Up', fg="#CCCCCC", bg='#3A3A3A', width=10, cursor='hand2', command= open_new_acc)
    sign_button.place(x=360, y=525)
    widgets.append(sign_button)

    con_label = Label(root, text='Contact Us', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10, 'underline'), cursor='hand2')
    con_label.place(x=670, y=600)
    widgets.append(con_label)

    con_label1 = Label(root, text='Terms of Policy', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10, 'underline'), cursor='hand2')
    con_label1.place(x=657, y=620)
    widgets.append(con_label1)

def open_new_acc():
    # Get the values from the Entry fields
    name = name_entry.get()
    email = email_entry.get()
    password = pas_entry.get()
    income = income_entry.get()

    if not name or not email or not password or not income:
        error_label = Label(root, text="All fields are required.", fg="red", bg='#1E1E1E')
        error_label.place(x=335, y=525)
        sign_button.config(state='disabled')
        return

    try:
        conn = sqlite3.connect("Users.db")
        c = conn.cursor()
        
        # Insert user details into users table
        c.execute('INSERT INTO users(name, email, password) VALUES(?, ?, ?)', (name, email, password))
        user_id = c.lastrowid  # Get the ID of the newly created user

        # Insert income for the user
        c.execute('INSERT INTO user_income(user_id, income) VALUES(?, ?)', (user_id, income))

        conn.commit()
        hide_widgets()
        after_login()

    except sqlite3.IntegrityError:
        error_label = Label(root, text="Account creation failed. Email already exists.", fg="red", bg='#1E1E1E')
        error_label.place(x=330, y=525)
        sign_button.config(state='disabled')
    
    conn.close()


def login_function(email, password):
    # Check if email or password fields are empty
    if not email or not password:
        error_label = Label(root, text="Email and password fields cannot be empty.", fg="red", bg='#1E1E1E')
        error_label.place(x=287, y=480)
        widgets.append(error_label)
        return

    conn = sqlite3.connect("Users.db")
    c = conn.cursor()

    # Try to retrieve the user with the given email and password
    c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = c.fetchone()
    if user:
        global logged_in_user_id
        logged_in_user_id = user[0]
        hide_widgets()
        after_login()
        #success_label = Label(root, text=f"Welcome {user[0]}! You have logged in successfully.", fg="#FFD700", bg='#1E1E1E', font=("Helvetica", 14))
        #success_label.place(x=50, y=50)
    else:
        error_label = Label(root, text="Invalid email or password.", fg="red", bg='#1E1E1E')
        error_label.place(x=350, y=480)
        widgets.append(error_label)

    conn.close()

def after_login():
   #Greetings()
   #TTime()
   wel_label = Label(root, text="FS22.pk", fg="#FFD700", bg='#1E1E1E', font=("Helvetica", 26, "bold"))
   wel_label.place(x=290, y=30)
   #widgets.append(wel_label)

   wel_label_sub = Label(root, text='Your Financial Journey made easy.', fg="#FFD700", bg='#1E1E1E', font=("Helvetica Neue", 10, "italic"))
   wel_label_sub.place(x=290, y=70)
   #widgets.append(wel_label_sub)
   
   tr_label = Label(root, text='Update your Info', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 12, "underline"), cursor= 'hand2')
   tr_label.place(x=60, y=160)
   widgets.append(tr_label)
   li_label = Label(root, text='||', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 12, "underline"))
   li_label.place(x= 270, y=160)
   widgets.append(li_label)
   pre_label = Label(root, text='Prepare your Budget', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 12, "underline"), cursor= 'hand2')
   pre_label.place(x=320, y=160)
   widgets.append(pre_label)
   li_label = Label(root, text='||', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 12, "underline"))
   li_label.place(x= 500, y=160)
   widgets.append(li_label)
   su_label = Label(root, text='Summary', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 12, "underline"), cursor= 'hand2')
   su_label.place(x=600, y=160)
   widgets.append(su_label)
   su_label.bind("<Button-1>", lambda e: view_summary())
   ru_label = Label(root, text='Command Prompt:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
   ru_label.place(x=32, y=240)
   widgets.append(ru_label)
   global command_line
   command_line = Text(root, width=92, height=10, bg='black', fg='#FFFFFF')
   command_line.place(x=30, y=270)
   widgets.append(command_line)

   run_button = Button(root, text='Run', fg="#CCCCCC", bg='#3A3A3A', width=10, cursor='hand2', command= run_selector)
   run_button.place(x=600, y=450)
   widgets.append(run_button)

   ex_button = Button(root, text= 'Exit', fg="#CCCCCC", bg='#3A3A3A', width=10, cursor='hand2', command= root.quit)
   ex_button.place(x=690, y=450)
   widgets.append(ex_button)

def add():
   addin_button = Button(root, text='Add Income', fg="#CCCCCC", bg='#3A3A3A', width=20, cursor='hand2', command= add_income)
   addin_button.place(x=30, y=450)
   widgets.append(addin_button)
   addex_button = Button(root, text='Add Expenses', fg="#CCCCCC", bg='#3A3A3A', width=20, cursor='hand2', command= add_expenses)
   addex_button.place(x=200, y=450)
   widgets.append(addex_button)
   #global addexca_button
   #addexca_button = Button(root, text='Add Expense Categories', fg="#CCCCCC", bg='#3A3A3A', width=20, #cursor='hand2')
   #addexca_button.place(x=370, y=450)

def delete1():
    delex_button = Button(root, text='Delete Expenses', fg="#CCCCCC", bg='#3A3A3A', width=20, cursor='hand2', command= Del_exp)
    delex_button.place(x=30, y=450)
    widgets.append(delex_button)
    delexc_button = Button(root, text='Delete Transactions', fg="#CCCCCC", bg='#3A3A3A', width=20, cursor='hand2',)
    delexc_button.place(x=200, y=450)
    widgets.append(delexc_button)
   #hide_widgets()

def view():
    viewtr_button = Button(root, text='View your Info', fg="#CCCCCC", bg='#3A3A3A', width=20, cursor='hand2', command= view_info)
    viewtr_button.place(x=30, y=450)
    widgets.append(viewtr_button)
    viewex_button = Button(root, text='View Expenses', fg="#CCCCCC", bg='#3A3A3A', width=20, cursor='hand2', command= View_Expense)
    viewex_button.place(x=200, y=450)
    widgets.append(viewex_button)

def summarize():
    monsum_button = Button(root, text='Monthly Summary', fg="#CCCCCC", bg='#3A3A3A', width=20, cursor='hand2')
    monsum_button.place(x=30, y=450)
    widgets.append(monsum_button)
    yearsum_button = Button(root, text='Yearly Summary', fg="#CCCCCC", bg='#3A3A3A', width=20, cursor='hand2')
    yearsum_button.place(x=200, y=450)
    widgets.append(yearsum_button)

def run_selector():
    cmd = command_line.get("1.0", END).strip()
    if cmd.lower() == 'add':
        add()
    elif cmd.lower() == 'delete':
        delete1()
        #addexca_button.place_forget()
    elif cmd.lower() == 'view':
        view()
        #addexca_button.place_forget()
    elif cmd.lower() == 'summarize':
        summarize()
        #addexca_button.place_forget()
    else:
        else_label = Label(root, text='Invalid Command', fg="red", bg='#1E1E1E')
        else_label.place(x=350, y=400)

def add_income():
    hide_widgets()
    inc_label = Label(root, text='Please enter your Monthly Income:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 12))
    inc_label.place(x=290, y=250)
    inc_entry = Entry(root)
    inc_entry.place(x=290, y=280, width= 290, height=30)
    inc_button = Button(root, text='Submit', fg="#CCCCCC", bg='#3A3A3A', width=10, cursor='hand2')
    inc_button.place(x=360, y=325)

def add_expenses():
    hide_widgets()
    
    num_label = Label(root, text='How many types of expenses you want to add:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    num_label.place(x=290, y=250)
    global num_entry
    num_entry = Entry(root)
    num_entry.place(x=290, y=280, width=290, height=30)

    num_button = Button(root, text='Submit', fg="#CCCCCC", bg='#3A3A3A', width=10, cursor='hand2', command=add_expense_categories)
    num_button.place(x=360, y=325)

def add_expense_categories():
    expnum = int(num_entry.get())  # Total number of expenses to be added
    expenses = []  # List to keep track of entered expenses (can also use database for this)
    current_expense = len(expenses) + 1  # Track the current expense being entered

    def submit_expense():
        nonlocal current_expense
        category = exp_entry.get()
        budget = budget_entry.get()

        # Insert into the database
        conn = sqlite3.connect("Users.db")
        c = conn.cursor()
        global yeardate
        yeardate = datetime.now()
        year = yeardate.year
        global monthdate
        monthdate = datetime
        month = monthdate.today()
        # Assuming `logged_in_user_id` is a global variable or session-stored user id after login
        c.execute('INSERT INTO expense_categories(user_id, category, budget, mdate, ydate) VALUES (?, ?, ?, ?, ?)', 
                  (logged_in_user_id, category, budget, month, year))
        conn.commit()
        conn.close()

        # Store the entered expense data in the expenses list (optional if saved to DB)
        expenses.append({"category": category, "budget": budget})

        # Move to the next expense if not all expenses are added
        if current_expense < expnum:
            current_expense = len(expenses) + 1  # Set to the next expense number based on the count
            # Update both labels to reflect the current expense number
            exp_label.config(text=f'Please enter the type of expense {current_expense}')
            budget_label.config(text=f'Enter the budget for expense {current_expense}')
            
            # Clear the entry fields for the next expense
            exp_entry.delete(0, 'end')
            budget_entry.delete(0, 'end')
        else:
            # All expenses have been entered, disable further input
            exp_label.config(text="All expenses entered!")
            exp_entry.config(state='disabled')  # Disable the entry field
            budget_label.config(text="Budgets entered!")
            budget_entry.config(state='disabled')  # Disable budget entry
            exp_button.config(state='disabled')  # Disable the submit button

    # Label and Entry fields for the expense type
    exp_label = Label(root, text=f'Please enter the type of expense {current_expense}', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    exp_label.place(x=290, y=355)
    exp_entry = Entry(root)
    exp_entry.place(x=290, y=385, width=290, height=30)

    # Label and Entry fields for the budget
    budget_label = Label(root, text=f'Enter the budget for expense {current_expense}', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    budget_label.place(x=290, y=425)
    budget_entry = Entry(root)
    budget_entry.place(x=290, y=455, width=290, height=30)

    # Button to submit each expense and budget
    exp_button = Button(root, text='Submit', fg="#CCCCCC", bg='#3A3A3A', width=10, cursor='hand2', command=submit_expense)
    exp_button.place(x=360, y=500)

def View_Expense():
    conn = sqlite3.connect("Users.db")
    c = conn.cursor()
    hide_widgets()
# Execute the query
    c.execute(f"SELECT category, budget FROM expense_categories WHERE user_id = {logged_in_user_id}")

# Fetch all rows from the executed query
    rows = c.fetchall()

    budget_label = Label(root, text='Your Budget',fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 18, 'underline'))
    budget_label.place(x=290, y=150)
# Format and print the output
    exp = tabulate(rows, headers=["Category", "Expense"], tablefmt='grid')
    ex_list = Label(root, text=exp,  fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    ex_list.place(x=250, y=210)

# Close the connection
    conn.close()

def  view_info():
    conn = sqlite3.connect("Users.db")
    c = conn.cursor()
    hide_widgets()
# Execute the query
    global logged_in_user_id
    c.execute(f"SELECT * FROM users WHERE id = {logged_in_user_id}")
# Fetch all rows from the executed query
    rows = c.fetchall()
    info_label = Label(root, text='Your Personal Information',fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 18, 'underline'))
    info_label.place(x=290, y=150)
    info = tabulate(rows, headers=["ID", "Name", "Email", "Password"], tablefmt='grid')
    info_list = Label(root, text=info,  fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    info_list.place(x=250, y=210)
def Del_exp():
    hide_widgets()
    del_label = Label(root, text='Enter name of the expense to be deleted:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 13))
    del_label.place(x=240, y=200)
    global del_entry
    del_entry = Entry(root)
    del_entry.place(x=240, y=230, width=305, height=35)
    del_button = Button(root, text='Delete', fg="#CCCCCC", bg='#3A3A3A', width=15, cursor='hand2', command=del_command)
    del_button.place(x=330, y=285)

def del_command():
    conn = sqlite3.connect("Users.db")
    c = conn.cursor()
    try:
        del_cat = del_entry.get()
        # Use parameterized query to prevent SQL injection
        c.execute("DELETE FROM expense_categories WHERE category = ?", (del_cat,))
        conn.commit()  # Commit the changes to the database
        t_label = Label(root, text='Data deleted Successfully.', fg="red", bg='#1E1E1E')
        t_label.place(x=287, y=325)
    except Exception as e:
        ex_label = Label(root, text=f'Unable to delete this data: {str(e)}', fg="red", bg='#1E1E1E', font=("Helvetica Neue", 10))
        ex_label.place(x=297, y=325)
    finally:
        conn.close()  # Ensure the connection is closed after operation
def view_summary():
    hide_widgets()
    su_label = Label(root, text='Enter 1 if you want monthly salary and 2 if you want yearly summary: ', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    su_label.place(x=240, y=200)
    
    global su_entry
    su_entry = Entry(root)
    su_entry.place(x=240, y=230)

    su_button = Button(root, text='Submit', fg="#CCCCCC", bg='#3A3A3A', width=15, cursor='hand2', command=bu_summary)
    su_button.place(x=330, y=285)

def bu_summary():
    ans = su_entry.get()
    if ans == '1':
        Monthly()
    elif ans == '2':
        Yearly()
    else:
        el_label = Label(root, text='Failed to generate a summary. Try Again Later!', fg="red", bg='#1E1E1E', font=("Helvetica Neue", 10))
        el_label.place(x=310, y=340)

def Monthly():
    hide_widgets()
    m_label = Label(root, text='Enter number of the month whom you want summary:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    m_label.place(x=240, y=200)

    global m_entry
    m_entry = Entry(root)
    m_entry.place(x=240, y=230)

    m_button = Button(root, text='Get Summary', fg="#CCCCCC", bg='#3A3A3A', width=15, cursor='hand2', command=mo_func)
    m_button.place(x=330, y=285)

def mo_func():
    conn = sqlite3.connect("Users.db")
    c = conn.cursor()
    try:
        rmonth = m_entry.get()
        c.execute("SELECT category, budget FROM expense_categories WHERE mdate = ? AND user_id = ?", (rmonth, logged_in_user_id))
        out = c.fetchall()
        
        m1_label = Label(root, text=str(out), fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
        m1_label.place(x=240, y=330)  # Corrected this line
    except Exception as e:
        print(e)  # Print the error for debugging
        el_label = Label(root, text='Failed to generate a summary. Try Again Later!', fg="red", bg='#1E1E1E', font=("Helvetica Neue", 10))
        el_label.place(x=240, y=330)
    finally:
        conn.close()  # Close the database connection

def Yearly():
    hide_widgets()
    y_label = Label(root, text='Enter the year whom you want summary:', fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
    y_label.place(x=240, y=200)

    global y_entry
    y_entry = Entry(root)
    y_entry.place(x=240, y=230)

    y_button = Button(root, text='Get Summary', fg="#CCCCCC", bg='#3A3A3A', width=15, cursor='hand2', command=y_func)
    y_button.place(x=330, y=285)

def y_func():
    conn = sqlite3.connect("Users.db")
    c = conn.cursor()
    try:
        ryear = y_entry.get()  # Corrected this line
        c.execute("SELECT category, budget FROM expense_categories WHERE ydate = ? AND user_id = ?", (ryear, logged_in_user_id))
        out = c.fetchall()
        
        m1_label = Label(root, text=str(out), fg="#CCCCCC", bg='#1E1E1E', font=("Helvetica Neue", 10))
        m1_label.place(x=240, y=330)  # Corrected this line
    except Exception as e:
        print(e)  # Print the error for debugging
        el_label = Label(root, text='Failed to generate a summary. Try Again Later!', fg="red", bg='#1E1E1E', font=("Helvetica Neue", 10))
        el_label.place(x=240, y=330)
    finally:
        conn.close()  # Close the database connection

       

    
root.mainloop()


#223.mirzashayan@gmail.comshayan123