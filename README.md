# 🚪 ProTech Garage Doors - Repair & Installation

## نظرة عامة / Overview

**ProTech Garage Doors** هو موقع إلكتروني متكامل لشركة متخصصة في صيانة وتركيب أبواب الجراج. يوفر الموقع عرضاً احترافياً للخدمات والمنتجات مع نظام استفسارات متقدم وإشعارات واتساب.

**ProTech Garage Doors** is a complete website for a company specialized in garage door repair and installation. The website provides a professional display of services and products with an advanced inquiry system and WhatsApp notifications.

---

## 🌟 الميزات الرئيسية / Key Features

### 🔧 نظام الخدمات / Services System
- عرض شامل للخدمات المقدمة (إصلاح، تركيب، صيانة)
- تصنيف الخدمات حسب النوع
- صور للخدمات مع معرض before/after
- أسعار ابتدائية للخدمات
- خدمات مميزة

### 🚪 نظام المنتجات / Products System
- فتاحات أبواب الجراج (Openers)
  - Chain Drive, Belt Drive, Wall Mount
  - مواصفات تفصيلية (Wi-Fi, Battery Backup, Camera)
  - معلومات القوة الحصانية والسرعة
  
- أبواب الجراج (Doors)
  - أنماط متعددة (Long Panel, Contemporary, Carriage House)
  - مواد مختلفة (Steel, Aluminum, Wood)
  - معلومات العزل (R-Value)
  - خيارات الألوان والنوافذ

- الإكسسوارات وقطع الغيار
- منتجات مميزة والأكثر مبيعاً

### 📱 نظام الاستفسارات / Inquiry System
- نموذج تواصل متقدم
- أنواع استفسارات متعددة:
  - تقدير مجاني / Free Estimate
  - طلب خدمة / Service Request
  - استفسار عن منتج / Product Info
  - حالة طارئة / Emergency
- ربط الاستفسار بخدمة أو منتج محدد
- تتبع حالة الاستفسار (جديد، تم التواصل، قيد المعالجة، مكتمل)
- ملاحظات إدارية
- نظام مرفقات

### 💬 تكامل WhatsApp / WhatsApp Integration
- إرسال إشعار تلقائي عند استلام استفسار جديد
- رسائل منسقة احترافياً
- معلومات كاملة عن الاستفسار
- دعم ثنائي اللغة (عربي/إنجليزي)
- إعادة إرسال من لوحة التحكم

### 📊 لوحة تحكم متقدمة / Advanced Admin Panel
- إحصائيات شاملة:
  - عدد المنتجات والخدمات
  - الاستفسارات (جديدة، قيد المعالجة، مكتملة)
  - المنتجات الأكثر مشاهدة
  - إحصائيات أسبوعية
- إدارة كاملة للمحتوى
- نظام بحث وفلترة متقدم
- Actions جماعية
- معاينة رسائل WhatsApp

---

## 🛠️ التقنيات المستخدمة / Technologies Used

- **Backend:** Django 4.2+
- **Database:** SQLite (Development), PostgreSQL (Production recommended)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Admin:** Django Admin (Customized)
- **Language:** Python 3.8+

---

## 📦 متطلبات النظام / System Requirements

```
Python >= 3.8
Django >= 4.2
Pillow (for images)
```

---

## 🚀 التثبيت والتشغيل / Installation & Setup

### 1. تحضير البيئة / Environment Setup

```bash
# Clone the repository
git clone <repository_url>
cd protech-repair

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. إعداد قاعدة البيانات / Database Setup

```bash
# Run migrations
python manage.py migrate

# Populate initial data
python manage.py populate_services
python manage.py populate_products

# Create superuser
python manage.py createsuperuser
```

### 3. تشغيل الخادم / Run Server

```bash
# Development server
python manage.py runserver

# The site will be available at: http://localhost:8000
# Admin panel at: http://localhost:8000/admin
```

---

## ⚙️ الإعدادات / Configuration

### WhatsApp Integration

في `core/settings.py`:

```python
# WhatsApp Configuration
WHATSAPP_ENABLED = True  # Enable WhatsApp notifications
WHATSAPP_API_URL = 'https://api.example.com/whatsapp'  # Your API URL
WHATSAPP_API_TOKEN = 'your-token-here'  # Your API token
WHATSAPP_PHONE_NUMBER = '+1234567890'  # Owner's WhatsApp number
```

**خيارات WhatsApp API:**
- Twilio API
- WhatsApp Business API
- Third-party services

### Email Configuration

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
ADMIN_EMAIL = 'admin@protechgaragedoors.com'
```

---

## 📁 هيكل المشروع / Project Structure

```
protech-repair/
├── core/                    # Project settings and configuration
│   ├── settings.py         # Main settings
│   ├── urls.py             # Main URLs
│   ├── views.py            # Homepage view
│   └── admin.py            # Custom admin site
│
├── services/               # Services app
│   ├── models.py           # Service, ServiceCategory, ServiceImage
│   ├── admin.py            # Services admin
│   ├── views.py            # Services views
│   ├── urls.py             # Services URLs
│   └── management/         # Management commands
│       └── commands/
│           └── populate_services.py
│
├── products/               # Products app
│   ├── models.py           # Product, ProductCategory, OpenerSpecs, DoorSpecs
│   ├── admin.py            # Products admin
│   ├── views.py            # Products views
│   ├── urls.py             # Products URLs
│   └── management/
│       └── commands/
│           └── populate_products.py
│
├── inquiries/              # Inquiries app (Contact system)
│   ├── models.py           # ContactInquiry, InquiryNote, InquiryAttachment
│   ├── forms.py            # Contact forms
│   ├── admin.py            # Inquiries admin
│   ├── views.py            # Inquiries views
│   ├── urls.py             # Inquiries URLs
│   ├── utils.py            # WhatsApp & Email utilities
│   └── signals.py          # Auto-send notifications
│
├── users/                  # Users app
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, Images)
├── media/                  # User uploaded files
└── requirements.txt        # Python dependencies
```

---

## 📊 Models Overview

### Services App

#### ServiceCategory
- name, name_en
- slug, description, icon
- order, is_active

#### Service
- title, title_en, slug
- category (ForeignKey)
- description, short_description, features
- image, icon, starting_price
- is_featured, order, is_active

#### ServiceImage
- service (ForeignKey)
- image, title, caption
- is_before_after, order

---

### Products App

#### ProductCategory
- name, name_en
- slug, description, icon
- order, is_active

#### Product
- name, name_en, slug, model_number
- category, product_type (opener/door/accessory/part)
- brand, description, features, specifications
- price, image
- is_featured, is_best_seller, is_new
- views_count

#### OpenerSpecifications
- product (OneToOne)
- drive_type (chain/belt/screw/wall_mount/jackshaft)
- horsepower
- has_wifi, has_battery_backup, has_camera, has_smart_features
- lifting_capacity, speed, noise_level
- warranty_years

#### DoorSpecifications
- product (OneToOne)
- panel_style, material
- width_options, height_options
- insulation_type, r_value
- color_options, texture_options
- has_windows, window_options
- warranty_years

---

### Inquiries App

#### ContactInquiry
- name, email, phone, address
- inquiry_type (free_estimate/service_request/product_info/general/emergency)
- service_needed (ForeignKey), product_interest (ForeignKey)
- message
- status (new/contacted/in_progress/completed/cancelled)
- whatsapp_sent, whatsapp_sent_at, whatsapp_error
- admin_notes
- ip_address, user_agent

#### InquiryNote
- inquiry (ForeignKey)
- note, created_by, created_at

#### InquiryAttachment
- inquiry (ForeignKey)
- file, description, uploaded_at

---

## 🎨 الواجهات / Templates (TODO)

يجب إنشاء القوالب التالية:

### Homepage
- `templates/home.html`
  - Hero section with contact form
  - Featured services
  - Featured products
  - Call-to-action sections

### Services
- `templates/services/service_list.html`
- `templates/services/service_detail.html`

### Products
- `templates/products/product_list.html`
- `templates/products/product_detail.html`
- `templates/products/openers.html`
- `templates/products/doors.html`

### Inquiries
- `templates/inquiries/contact_form.html`
- `templates/inquiries/thank_you.html`

---

## 🔐 الأمان / Security

- ✅ IP address tracking for inquiries
- ✅ User agent tracking
- ✅ CSRF protection
- ✅ Form validation
- ✅ Admin-only views
- ⚠️ For production:
  - Set `DEBUG = False`
  - Update `SECRET_KEY`
  - Configure `ALLOWED_HOSTS`
  - Use HTTPS
  - Configure proper database (PostgreSQL recommended)

---

## 📱 الصفحات الرئيسية / Main Pages

1. **Homepage** `/` - عرض الخدمات والمنتجات المميزة
2. **Services** `/services/` - قائمة الخدمات
3. **Service Detail** `/services/<slug>/` - تفاصيل الخدمة
4. **Products** `/products/` - قائمة المنتجات
5. **Openers** `/products/openers/` - فتاحات الأبواب
6. **Doors** `/products/doors/` - أبواب الجراج
7. **Product Detail** `/products/<slug>/` - تفاصيل المنتج
8. **Contact** `/inquiries/contact/` - نموذج التواصل
9. **Admin Panel** `/admin/` - لوحة التحكم

---

## 🎯 البيانات الأولية / Initial Data

### Services (8 خدمات):
1. إصلاح زنبرك الباب / Spring Repair
2. إصلاح فتاحة الباب / Opener Repair
3. إصلاح الكابلات والبكرات / Cable & Roller Repair
4. تركيب باب جراج جديد / New Door Installation
5. تركيب فتاحة الباب / Opener Installation
6. صيانة دورية / Regular Maintenance
7. استبدال اللوحات التالفة / Panel Replacement
8. برمجة جهاز التحكم عن بعد / Remote Programming

### Products (5 منتجات):
**Openers:**
1. Chain Drive 1/2 HP (LiftMaster 8500W)
2. Belt Drive Smart with Wi-Fi (LiftMaster 8160WB)
3. Wall Mount with Camera (LiftMaster 87504-267)

**Doors:**
4. Long Panel Garage Door (Clopay LP-100)
5. Contemporary Garage Door (Clopay MOD-200)

---

## 📞 الدعم / Support

للمزيد من المعلومات أو المساعدة، يرجى التواصل.

For more information or support, please contact.

---

## 📝 الترخيص / License

هذا المشروع مطور خصيصاً لـ ProTech Garage Doors.

This project is specifically developed for ProTech Garage Doors.

---

## 🚧 التطوير المستقبلي / Future Development

- [ ] إنشاء قوالب HTML كاملة
- [ ] تصميم responsive
- [ ] تكامل نظام الدفع (اختياري)
- [ ] معرض الأعمال السابقة
- [ ] نظام التقييمات
- [ ] Blog/Articles
- [ ] Multi-language support

---

**🎉 مشروع ProTech Garage Doors جاهز للعمل!**

**🎉 ProTech Garage Doors Project is Ready!**

---

**Contact Information:**
- Phone: (714) 515-0313 / (951) 466-7900
- Email: info@ProtechGarageDoorsRepair.com
- Location: Corona, CA 92880
- License: #1070155

---
