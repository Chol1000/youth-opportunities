# Youth Opportunities - Connecting Talent with Opportunities

[![Live Demo](https://img.shields.io/badge/Live%20Demo-chol1000.pythonanywhere.com-blue)](https://chol1000.pythonanywhere.com)
[![Django](https://img.shields.io/badge/Django-5.2.1-green)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org/)
[![MySQL](https://img.shields.io/badge/Database-MySQL-orange)](https://mysql.com/)

## 📋 Table of Contents
- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Live Demo](#live-demo)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)


## 🎯 About

Youth Opportunities is a comprehensive platform designed to connect young talents with life-changing opportunities worldwide. Founded in 2024, this youth-led platform shares global opportunities including internships, scholarships, fellowships, jobs, conferences, and more, inspiring growth, exposure, and hope for a brighter future.

## ✨ Features

### 🌟 Core Features
- **Opportunity Discovery**: Browse scholarships, internships, jobs, grants, fellowships, and more
- **Advanced Search**: Filter opportunities by type, location, deadline, and organization
- **Featured Opportunities**: Highlighted opportunities for maximum visibility
- **User Authentication**: Secure registration and login system
- **Admin Dashboard**: Comprehensive admin panel for content management
- **Responsive Design**: Mobile-first design that works on all devices

### 🎨 User Experience
- **Dark/Light Theme**: Toggle between themes for comfortable viewing
- **Multi-language Support**: Available in 11 languages including English, Chinese, Spanish, French, Arabic, Hindi, Portuguese, Russian, German, Japanese, and Swahili
- **Real-time Updates**: Live trending opportunities ticker
- **Interactive Carousel**: Featured opportunities showcase
- **Newsletter Subscription**: Stay updated with latest opportunities
- **Feedback System**: User feedback and support system

### 🔒 Security Features
- **CSRF Protection**: Cross-Site Request Forgery protection
- **XSS Prevention**: Input sanitization and output escaping
- **Content Security Policy**: Strict CSP headers
- **Secure Headers**: HSTS, X-Frame-Options, and more
- **Input Validation**: Server-side and client-side validation

## 🛠 Tech Stack

### Backend
- **Framework**: Django 5.2.1
- **Database**: MySQL
- **API**: Django REST Framework
- **Authentication**: Token-based authentication
- **File Handling**: Django file uploads with Pillow

### Frontend
- **Languages**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with CSS Variables
- **Icons**: Font Awesome 6.0
- **Fonts**: Google Fonts (Poppins, Open Sans)
- **Responsive**: Mobile-first design

### Additional Tools
- **Rich Text Editor**: CKEditor
- **CORS**: Django CORS Headers
- **Environment**: python-dotenv
- **Cleanup**: django-cleanup

## 🌐 Live Demo

Visit the live application: [https://chol1000.pythonanywhere.com](https://chol1000.pythonanywhere.com)

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- MySQL 5.7 or higher
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/youth-opportunities.git
cd youth-opportunities
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r backend/api/requirements.txt
```

### Step 4: Database Setup
1. **Install MySQL** (if not already installed)
2. **Create Database**:
```sql
CREATE DATABASE youth_opportunities;
CREATE USER 'youth_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON youth_opportunities.* TO 'youth_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 5: Environment Configuration
Create a `.env` file in the root directory (same level as backend folder):
```env
DJANGO_SECRET_KEY=your-super-secret-key-here
DB_USER=youth_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
FRONTEND_BASE_URL=http://localhost:8000
```

### Step 6: Database Migration
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 8: Collect Static Files
```bash
python manage.py collectstatic
```

### Step 9: Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see the application running.

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the root directory (same level as backend folder) with the following variables:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Configuration
DB_USER=youth_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration (Optional)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend URLs
FRONTEND_BASE_URL=http://localhost:8000
```

### Database Configuration
The project uses MySQL by default. To use a different database, modify the `DATABASES` setting in `backend/config/settings.py`.

### Static Files
Static files are served from the `frontend/static` directory during development. For production, run `collectstatic` to gather all static files.

## 📖 Usage

### For Users
1. **Browse Opportunities**: Visit the homepage to see featured opportunities
2. **Search**: Use the search functionality to find specific opportunities
3. **Filter**: Filter by type, location, or deadline
4. **Register**: Create an account to save favorites (if implemented)
5. **Subscribe**: Subscribe to newsletter for updates

### For Administrators
1. **Access Admin Panel**: Visit `/admin` and login with superuser credentials
2. **Add Opportunities**: Create new opportunities through the admin interface
3. **Manage Users**: View and manage user accounts
4. **Content Management**: Edit, approve, or delete opportunities

### API Endpoints
- `GET /api/opportunities/` - List all approved opportunities
- `POST /api/feedback/` - Submit feedback
- `POST /api/newsletter/subscribe/` - Subscribe to newsletter

## 📚 API Documentation

### Opportunities API
```http
GET /api/opportunities/?status=approved
```
Returns a list of approved opportunities with filtering options.

**Query Parameters:**
- `status`: Filter by approval status
- `opportunity_type`: Filter by type (scholarship, job, internship, etc.)
- `location`: Filter by location

### Feedback API
```http
POST /api/feedback/
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Feedback Subject",
    "message": "Your feedback message",
    "feedback_type": "general"
}
```

### Newsletter API
```http
POST /api/newsletter/subscribe/
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com"
}
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
- Ensure MySQL is running
- Check database credentials in `.env` file
- Verify database exists and user has proper permissions

**Static Files Not Loading**
- Run `python manage.py collectstatic`
- Check `STATIC_URL` and `STATIC_ROOT` settings

**CSRF Token Errors**
- Ensure CSRF middleware is enabled
- Check `CSRF_TRUSTED_ORIGINS` in settings



## 👨‍💻 Author

**Chol Atem Giet**
- Email: c.monykuch@alustudent.com
- GitHub: [Chol1000](https://github.com/Chol1000)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Font Awesome for the icons
- Google Fonts for typography
- All contributors and supporters of this project

---

**Built with ❤️ for the youth community worldwide**

For support or questions, please open an issue or contact us through the feedback system on the website.
