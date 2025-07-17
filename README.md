# Telehealth Cancer Institute Backend

A scalable and secure backend for a telehealth platform, built with **Django REST Framework**. This service provides
user authentication, doctor-patient scheduling, appointment management, payments, and more.


## Features

- 🔐 JWT Authentication via secure HTTP-only cookies
- 📅 Doctor time slot and appointment management
- 🧾 Refund system for appointments
- 💳 Stripe payment integration
- 🛡️ Role-based access control (Admin, Doctor, Patient)
- 📩 Email notifications (e.g. refund, appointment confirmation)
- 📦 Docker-compatible deployment
- 🧪 CI with GitHub Actions & commit linting

---

## 🗂️ Project Structure

```
.
├── api/                   # Core apps logic: views, serializers, models
├── config/                # Django settings module
├── templates/emails/      # Email HTML templates
├── staticfiles/           # Static assets
├── requirements.txt       # Python dependencies
├── example.env            # Environment variable sample file
├── manage.py              # Django management script
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/zaidy-mughal/telehealth-backend.git
cd telehealth-backend
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file using the sample provided:

```bash
cp example.env .env
```

Update values such as:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
STRIPE_SECRET_KEY=sk_test_xxx
EMAIL_HOST_USER=your-email@example.com
...
...
```

### 5. Apply Migrations and Run Server

```bash
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 🛠️ Key Endpoints (Sample)

| Endpoint                                       | Method | Description                    |
|------------------------------------------------|--------|--------------------------------|
| `/api/auth/login/`                             | POST   | Login user with JWT cookies    |
| `/api/auth/logout/`                            | POST   | Logout and clear tokens        |
| `/api/appointments/`                           | GET    | List appointments              |
| `/api/patients/me/`                            | GET    | List Personal Details          |
| `/api/timeslots/bulk-create/`                  | POST   | Bulk slot creation for doctors |
| `/api/payment/stripe/create-checkout-seesion/` | POST   | Create Stripe Payment Intent   |

---

## 🧩 CI/CD

- **GitHub Actions**: Linting, testing
- **Commit Linting**: Enforced via `commitlint.config.js`

---

## 📬 Email Templates

Located in `templates/emails/` and used for:

- Appointment confirmations
- Refund notifications
- Welcome emails

---

## 🔐 Authentication

Uses [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) with cookie-based tokens for secure
session management. Cookies are:

- `jwt-access-token`
- `jwt-refresh-token`

---

## 💳 Payments

- Stripe integration for secure online payments
- Webhooks and refund flow supported

---

## 📄 License

This project is licensed under the MIT License.


