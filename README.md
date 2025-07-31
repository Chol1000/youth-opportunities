# Youth Opportunities - Uniting Talent & Hope

[![Live Demo](https://img.shields.io/badge/Live%20Demo-chol1000.pythonanywhere.com-blue)](https://chol1000.pythonanywhere.com)
[![Django](https://img.shields.io/badge/Django-5.2.1-green)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org/)
[![MySQL](https://img.shields.io/badge/Database-MySQL-orange)](https://mysql.com/)

## 📋 Table of Contents
- [About](#about)
- [Mission Statement](#mission-statement)
- [Problem Statement](#problem-statement)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Live Demo](#live-demo)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development Model](#development-model)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)

## 🎯 About

Youth Opportunities Uniting Talent & Hope is a comprehensive platform designed to empower young people globally by linking them to valuable opportunities like scholarships, internships, and jobs. Founded in 2024, this youth-led platform goes beyond simple opportunity listing to provide a guided, community-driven empowerment forum that helps youth prepare for and succeed in their applications.

## 🌟 Mission Statement

Our mission is to empower young people globally by linking them to valuable opportunities like scholarships, internships, and jobs, and providing them with the training, mentorship, and support they need to leverage those opportunities to their advantage. We aim to close the readiness and opportunity gap by developing an online space where youth can:

- Access curated opportunities
- Create comprehensive profiles
- Be matched with rigorously curated resources
- Receive guidance and support
- Interact with peers in a positive and safe community

This mission directly addresses the top priority youth issues identified by the African Leadership University (ALU) Grand Challenges: **Youth Unemployment**, **Access to Education**, and **Technology**.

## 🚨 Problem Statement

Around the world, millions of young individuals encounter great hindrances in accessing transformative opportunities. Key challenges include:

- **WHO**: Global youth, especially those from disadvantaged or underserved communities
- **WHAT**: Limited access to timely, relevant opportunities and inadequate preparation guidance
- **WHEN**: This is a long-standing and increasing problem as labor markets evolve and competition rises
- **WHERE**: Worldwide, with emphasis on Africa and other developing regions
- **WHY**: Most existing systems merely list opportunities but fail to prepare youth to capitalize on them
- **HOW**: Through our comprehensive platform that provides not just access but also mentorship, tools, and peer support

## ✨ Features

### 🌟 Currently Implemented Features
- **Opportunity Discovery**: Browse scholarships, internships, jobs, grants, fellowships, conferences, workshops, trainings, competitions, and announcements
- **Advanced Search & Filtering**: Filter opportunities by type, location, deadline, and organization
- **Featured Opportunities**: Highlighted opportunities in hero carousel for maximum visibility
- **User Authentication**: Secure registration and login system with role-based access
- **Admin Dashboard**: Comprehensive admin panel for content management and moderation
- **Responsive Design**: Mobile-first design that works seamlessly on all devices
- **Real-time Updates**: Live trending opportunities ticker showing latest active opportunities
- **Interactive Carousel**: Featured opportunities showcase with navigation controls
- **Newsletter Subscription**: Stay updated with latest opportunities via email
- **Feedback System**: User feedback and support system with categorized feedback types
- **Success Stories**: Dedicated section for sharing user success stories
- **Multi-page Structure**: Dedicated pages for each opportunity type

### 🎨 User Experience Features
- **Dark/Light Theme**: Toggle between themes for comfortable viewing with persistent preferences
- **Multi-language Support**: Interface available in 11 languages including English, Chinese, Spanish, French, Arabic, Hindi, Portuguese, Russian, German, Japanese, and Swahili
- **Mobile Navigation**: Collapsible mobile menu with bottom navigation bar
- **Status Indicators**: Visual status indicators for opportunities (Active, Expired, Rolling, Ongoing, etc.)
- **Social Media Integration**: Social sharing and follow buttons
- **Search Modals**: Advanced search functionality with modal interfaces

### 🔒 Security Features
- **CSRF Protection**: Cross-Site Request Forgery protection with Django middleware
- **XSS Prevention**: Input sanitization and output escaping
- **Content Security Policy**: Strict CSP headers for preventing code injection
- **Secure Headers**: HSTS, X-Frame-Options, X-Content-Type-Options, and Referrer-Policy
- **Input Validation**: Comprehensive server-side and client-side validation
- **Security Middleware**: Custom security headers and input sanitization middleware

### 🚧 Planned Features (Not Yet Implemented)
- **Mentorship System**: Connect youth with professional mentors
- **Community Forums**: Discussion boards for peer support and Q&A
- **Profile Building Tools**: Comprehensive user profiles with CV/resume builders
- **Application Tracking**: Track application status and deadlines
- **Personalized Recommendations**: AI-powered opportunity matching
- **Direct Messaging**: Communication between users and mentors
- **Achievement Badges**: Gamification elements to encourage engagement
- **Calendar Integration**: Deadline reminders and scheduling tools

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
1. **Browse Opportunities**: Visit the homepage to see featured opportunities in the hero carousel
2. **Explore Categories**: Navigate through dedicated pages for scholarships, internships, jobs, grants, fellowships, conferences, workshops, trainings, competitions, and announcements
3. **Search & Filter**: Use the advanced search functionality to find specific opportunities by type, location, deadline, or organization
4. **Theme Switching**: Toggle between light and dark themes for comfortable viewing
5. **Language Selection**: Choose from 11 available languages for the interface
6. **Newsletter Subscription**: Subscribe to receive updates about new opportunities
7. **Feedback Submission**: Provide feedback through the integrated feedback system
8. **Success Stories**: Read inspiring success stories from other users

### For Administrators
1. **Access Admin Panel**: Visit `/admin` and login with superuser credentials
2. **Opportunity Management**: 
   - Add new opportunities with detailed information
   - Set opportunity types, deadlines, and featured status
   - Upload featured images and organization logos
   - Manage opportunity approval status
3. **User Management**: View and manage user accounts and roles
4. **Content Moderation**: Review and moderate user-generated content
5. **Analytics**: Monitor platform usage and engagement metrics
6. **Newsletter Management**: Manage newsletter subscriptions and campaigns
7. **Feedback Review**: Review and respond to user feedback

### Current API Endpoints
- `GET /api/opportunities/` - List all approved opportunities with filtering
- `POST /api/feedback/` - Submit user feedback
- `POST /api/newsletter/subscribe/` - Subscribe to newsletter
- `GET /api/users/` - User management (admin only)
- `POST /api/auth/login/` - User authentication
- `POST /api/auth/register/` - User registration

### Planned API Endpoints (Future Implementation)
- `GET /api/mentors/` - List available mentors
- `POST /api/mentorship/request/` - Request mentorship
- `GET /api/forums/` - Forum discussions
- `POST /api/forums/` - Create forum posts
- `GET /api/profile/` - User profile management
- `POST /api/applications/` - Track opportunity applications

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

## 🔄 Development Model

This project follows the **Agile Software Development Model** to ensure flexibility, adaptability, and continuous improvement. The Agile approach allows us to:

- Develop features incrementally while learning from user feedback
- Adapt to changing requirements without redesigning the entire system
- Deliver working software early and iterate based on real-world usage
- Maintain a user-centered approach aligned with global youth needs

### Agile Implementation Steps:
1. **Requirement Gathering and Prioritization**
2. **Sprint Planning and MVP Development**
3. **Iterative Prototyping and Testing**
4. **Deployment and Feedback Collection**
5. **Continuous Improvement and Feature Enhancement**

## 🗺️ Future Roadmap

### Phase 1: Core Platform Enhancement (Current)
- ✅ Opportunity listing and browsing
- ✅ User authentication and admin panel
- ✅ Responsive design and theming
- ✅ Multi-language support
- ✅ Newsletter and feedback systems
- 🔄 Community forums and discussions

### Phase 2: Community Features (Planned)
- 🔄 Mentorship matching system

### Phase 3: Advanced Features (Future)
- 📋 AI-powered opportunity recommendations
- 📋 Application tracking and reminders
- 📋 Achievement and gamification system
- 📋 Mobile application development
- 📋 Integration with external opportunity APIs

### Phase 4: Scale and Impact (Long-term)
- 📋 Partnership with educational institutions
- 📋 Corporate mentorship programs
- 📋 Success tracking and impact measurement
- 📋 Regional expansion and localization

## 🤝 Contributing

We welcome contributions to help build this platform for global youth empowerment! Please follow these steps:

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
- Consider the global youth audience in all design decisions
- Prioritize accessibility and mobile-first design

### Priority Areas for Contribution
- **Mentorship System**: Help implement the mentor-mentee matching functionality
- **Community Forums**: Build discussion boards and peer support features
- **Mobile Optimization**: Enhance mobile user experience
- **Accessibility**: Improve platform accessibility for users with disabilities
- **Internationalization**: Add support for more languages and regions
- **Testing**: Add comprehensive test coverage
- **Documentation**: Improve user guides and developer documentation

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
- Verify CSRF token is included in forms

**Theme/Language Not Persisting**
- Check if localStorage is enabled in browser
- Clear browser cache and cookies
- Ensure JavaScript is enabled

**Opportunities Not Loading**
- Check database connection
- Verify opportunities are marked as 'approved' in admin panel
- Check browser console for JavaScript errors

**Mobile Navigation Issues**
- Clear browser cache
- Ensure viewport meta tag is present
- Check for JavaScript errors in mobile browser



## 🎯 Project Hypothesis

If we create and launch a scalable, community-based platform that links global youth to opportunity listings, mentorship, and skill-building tools—and also facilitates peer collaboration and community-based sharing—then more youth will not only be able to find these opportunities but will also have the support and preparation necessary to thrive in them.

**Expected Outcomes:**
- Higher application success rates
- Improved career-readiness among youth
- More engaged global youth community
- Decreased youth unemployment
- Expanded access to quality education
- Enhanced economic mobility for underserved communities

## 👨‍💻 Author

**Chol Atem Giet Monykuch**
- Email: c.monykuch@alustudent.com
- GitHub: [Chol1000](https://github.com/Chol1000)
- Organization: African Leadership University (ALU)
- Project: Youth Opportunities Uniting Talent & Hope

## 🙏 Acknowledgments

- **African Leadership University (ALU)** for identifying the Grand Challenges that inspired this project
- **Django Community** for the excellent web framework
- **PythonAnywhere** for reliable hosting services
- **Font Awesome** for comprehensive icon library
- **Google Fonts** for beautiful typography (Poppins & Open Sans)
- **Global Youth Community** for inspiring this mission
- **Mentors and Educators** who guide young people worldwide
- **All contributors and supporters** of this project

## 📚 References

- African Leadership University. (n.d.). The 14 grand challenges. ALU.
- International Labour Organization. (2020). Global employment trends for youth 2020: Africa edition. ILO.
- McKinsey & Company. (2022). Reimagining youth employment in Africa: Technology and mentorship as catalysts.
- United Nations Development Programme. (2022). Youth empowerment strategy 2022–2025. UNDP.
- UNESCO. (2022). Global education monitoring report.
- World Bank. (2023). Youth unemployment statistics.

---

**Built with ❤️ for the global youth community**

*"Empowering young people globally by linking them to valuable opportunities and providing the support they need to succeed."*

For support or questions, please open an issue or contact us through the feedback system on the website.
