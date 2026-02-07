# 🚗 HOPE Rental – Car Rental Management System

HOPE Rental is a full-featured car rental management system built with **Flask**, **PostgreSQL**, and **HTML/CSS**.  
The project supports **user rentals**, **admin management**, **multi-step payments**, and a clean, modern UI with **Dark Mode** support.

This system was designed with clear separation between **users** and **admins**, focusing on real-world rental workflows.

---

## ✨ Features Overview

### 👤 User Features

- User authentication (Sign up / Login / Logout)
    
- View available cars
    
- Rent cars
    
- View personal rentals
    
- Pay for completed rentals (multi-step payments supported)
    
- See payment status and remaining balance
    

---

### 🛠 Admin Features

- Add new cars
    
- Edit car information
    
- Delete cars (only if no active rental exists)
    
- View all rentals
    
- Complete rentals
    
- Automatically set car status to **available** after rental completion
    
- Control rental lifecycle securely
    

---

## 🔐 Authentication & Authorization

- Session-based authentication
    
- Role-based access control:
    
    - **Users**: manage their own rentals and payments
        
    - **Admins**: manage cars and rentals
        
- Protected routes using decorators (`login_required`, `admin_required`)
    

---

## 🔄 Rental Lifecycle

1. User rents a car
    
2. Car status changes to `rented`
    
3. Admin completes the rental
    
4. Rental status changes to `completed`
    
5. Car status automatically changes back to `available`
    
6. User can pay the rental (one or multiple payments)
    
7. Rental is fully paid when balance reaches zero
    

---

## 💳 Payment System

- Payments are only allowed for **completed rentals**
    
- Supports partial payments
    
- Remaining balance is calculated dynamically
    
- Payment validation prevents overpayment
    
- Secure database constraints for payment status
    

---

## 🎨 UI & Design

- Clean and minimal interface
    
- Top navigation bar with:
    
    - Project name (HOPE Rental)
        
    - User name
        
    - Logout & Dashboard buttons
        
    - Dark mode toggle
        
- Custom CSS styling
    
- Separate Dark Mode CSS file
    
- Flash messages displayed clearly at the top of pages
    

---

## 🧱 Tech Stack

- **Backend**: Flask (Python)
    
- **Database**: PostgreSQL
    
- **Frontend**: HTML, CSS (Jinja2 templates)
    
- **Authentication**: Flask sessions
    
- **Styling**: Custom CSS + Dark Mode
    

---

## 📂 Project Structure

`project/ │ ├── app.py ├── database.py │ ├── templates/ │   ├── login.html │   ├── signup.html │   ├── dashboard.html │   ├── cars_list.html │   ├── my_rentals.html │   ├── pay_rental.html │   └── admin/ │       ├── rentals.html │       └── edit_car.html │ ├── static/ │   ├── style.css │   └── dark.css │ └── README.md`

---

## ▶️ How to Run the Project

### 1. Install dependencies

`pip install flask psycopg2`

### 2. Configure the database

- Create a PostgreSQL database
    
- Update database credentials in `database.py`
    

### 3. Run the application

`python app.py`

### 4. Open in browser

`http://127.0.0.1:5000/login`

---

## 🧪 Data Integrity & Safety

- Cars with active rentals cannot be deleted
    
- Rentals cannot be paid before completion
    
- Decimal values handled safely for prices
    
- Database-level constraints prevent invalid states
    

---

## 🚀 Possible Future Improvements

- Online payment gateway integration
    
- Invoice generation (PDF)
    
- Admin analytics dashboard
    
- Email notifications
    
- Auto-complete rentals by end date
    

---

## 📌 Project Name

**HOPE Rental**  
A simple, clean, and reliable car rental management system.

---

## 👨‍💻 Author

Developed as a university database project using Flask and PostgreSQL.