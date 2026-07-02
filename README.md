# TechBridge Support Platform

A modern, robust, and scalable Django backend platform connecting customers with IT technicians for support and repairs. It features real-time live chat via WebSockets, comprehensive ticketing lifecycle management, OTP-based secure authentication, and Stripe checkout for payments.

## 🚀 Features

- **JWT Authentication & OTP Registration**
  - Secure customer and technician onboarding via email-delivered One Time Passwords (OTP).
  - Robust session management with JWT (Access and Refresh tokens).

- **Ticket Lifecycle Management**
  - Customers can create specialized IT support tickets.
  - Technicians can view available jobs, accept tickets, and mark them as complete.
  - Granular ticket statuses: `open` -> `assigned` -> `pending_confirmation` -> `done`.

- **Real-Time Live Chat (WebSockets)**
  - Customers and Technicians can communicate instantly.
  - Built with Django Channels and Redis to handle asynchronous high-speed message delivery.
  - Ticket-specific chat rooms securely scoped to authorized participants.

- **Stripe Payments Integration**
  - Fully integrated checkout sessions.
  - Webhook listeners to automatically verify completed payments and mark tickets as `done`.

- **Review System**
  - Customers can rate and review technicians after a job is successfully completed.

- **Analytics Dashboard**
  - Data aggregation APIs serving total tickets, completion counts, revenue generated, and timelines for Customers, Technicians, and Admin.

- **Custom Admin Interface**
  - Sleek, modern admin panel powered by `django-unfold`.
  - Sidebar navigation customized with beautiful Material Symbols icons grouped by logical operations.

- **Optimized & Paginated APIs**
  - Fully optimized ORM queries (N+1 query resolution using `.select_related()`).
  - Automated `PageNumberPagination` to handle scaling arrays of data.

---

## 🛠 Tech Stack

- **Backend Framework:** Django 4.2+, Django REST Framework
- **Asynchronous Protocol:** Django Channels, Daphne Server
- **Message Broker:** Redis
- **Database:** SQLite (default for development), easily migratable to PostgreSQL
- **Admin Theme:** `django-unfold` (TailwindCSS integration for Django Admin)
- **Payment Gateway:** Stripe
- **Authentication:** `djangorestframework-simplejwt`

---

## 💻 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/tntanvir/Smart-it-Backend.git
cd Smart-it-Backend
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
Make sure you have all required dependencies installed:
```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers stripe channels daphne channels-redis django-unfold python-dotenv
```

### 4. Environment Variables
Create a `.env` file in the root backend directory alongside `manage.py` and populate it with your secure credentials:
```env
STRIPE_SECRET_KEY=sk_test_...
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 5. Setup Database & Admin
Run migrations to set up the SQLite database and create a superuser for the admin dashboard:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run Redis Server
Django Channels requires Redis as a channel layer backend to handle WebSockets. Ensure you have Redis running on your machine:
```bash
# Example via Docker
docker run -p 6379:6379 -d redis:5
```

### 7. Run the Development Server
Since WebSockets are used, the project runs on **Daphne** (the ASGI server) rather than the standard WSGI server:
```bash
python manage.py runserver 8001
# OR
daphne -b 127.0.0.1 -p 8001 SmartITSupport.asgi:application
```

---

## 📡 API Postman Documentation

This repository includes a completely comprehensive Postman Collection:
**`TechBridgeSupport_Complete_Collection.postman_collection.json`**

To test the APIs:
1. Open Postman.
2. Go to `File` -> `Import`.
3. Select `TechBridgeSupport_Complete_Collection.postman_collection.json`.
4. Run the endpoints sequentially to test the full Ticket Workflow (Registration -> Ticket Creation -> Accept -> Chat -> Complete -> Pay -> Review).

---

## 📂 Project Structure

```
backend/
│
├── analyze/              # Dashboard aggregation views (Admin/Tech/Customer)
├── authsystem/           # OTP verification, JWT login, and profile APIs
├── message/              # Live Chat WebSockets and REST APIs
├── payment/              # Stripe checkout and webhook listeners
├── SmartITSupport/       # Main Django configuration & URL routing
├── technician/           # Technician specific actions (accepting/completing jobs)
├── templates/            # HTML templates for the django-unfold admin overrides
├── tickets/              # Core ticket CRUD and operations
│
├── .env                  # Environment Variables (Ignored in Git)
├── .gitignore            # Git exclusion rules
├── db.sqlite3            # Local Database
├── manage.py             # Django entry point
└── README.md             # Project documentation
```
