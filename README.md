# منصة دلال السعودية - Dalal Saudi Arabia Platform

## نظرة عامة

منصة دلال السعودية هي منصة إلكترونية متكاملة لبيع وشراء السيارات والعقارات وحجز الفنادق في المملكة العربية السعودية. تم تطويرها باستخدام Django وتتضمن ميزات متقدمة مثل نظام المراسلة والمزادات والخرائط التفاعلية.

## الميزات الرئيسية

### 🚗 قسم السيارات
- عرض السيارات الجديدة والمستعملة
- معلومات تفصيلية (الماركة، الموديل، السنة، المسافة المقطوعة)
- صور متعددة عالية الجودة
- نظام تقييم وتعليقات

### 🏠 قسم العقارات
- شقق، فلل، أراضي، محلات تجارية
- معلومات شاملة (المساحة، عدد الغرف، الموقع)
- جولات افتراضية
- خرائط تفاعلية

### 🏨 قسم الفنادق
- حجز الفنادق والشقق المفروشة
- تقييمات النزلاء
- صور وتفاصيل الغرف
- نظام حجز متقدم

### 💬 نظام المراسلة
- دردشة فورية بين المستخدمين
- ربط المحادثات بالمنتجات
- إشعارات فورية
- واجهة سهلة الاستخدام

### 🔨 نظام المزادات
- إنشاء مزادات على المنتجات
- مزايدة فورية
- عد تنازلي للوقت
- تحديد الفائز تلقائياً

### 🗺️ نظام الخرائط
- عرض مواقع المنتجات على الخريطة
- البحث الجغرافي
- الاتجاهات والمسارات
- المنتجات القريبة

### 👨‍💼 لوحة الإدارة
- موافقة المسؤول على المنتجات
- إدارة المستخدمين
- إحصائيات وتقارير
- إعدادات النظام

## التقنيات المستخدمة

- **Backend:** Django 4.2, Python 3.8+
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Database:** PostgreSQL, Redis
- **Maps:** Leaflet.js, OpenStreetMap
- **Real-time:** AJAX, WebSocket
- **Deployment:** Nginx, Gunicorn

## متطلبات النظام

- Python 3.8+
- PostgreSQL 12+
- Redis 6.0+
- Ubuntu 20.04+ (مُوصى به)
- 4GB RAM (الحد الأدنى)
- 50GB Storage

## التثبيت والتشغيل

### 1. تحضير البيئة
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات
sudo apt install python3 python3-pip python3-venv postgresql redis-server nginx
```

### 2. إعداد قاعدة البيانات
```bash
# إنشاء قاعدة بيانات
sudo -u postgres createdb dalal_saudi
sudo -u postgres createuser dalal_user
sudo -u postgres psql -c "ALTER USER dalal_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dalal_saudi TO dalal_user;"
```

### 3. تثبيت المشروع
```bash
# تحميل المشروع
git clone <repository_url>
cd dalal_saudi_project

# إنشاء بيئة افتراضية
python3 -m venv venv
# source venv/bin/activate
venv\Scripts\activate

# تثبيت المتطلبات
pip install -r requirements.txt
```

### 4. تكوين الإعدادات
```bash
# نسخ ملف الإعدادات
cp dalal_saudi/settings.py.example dalal_saudi/settings.py

# تحرير الإعدادات (قاعدة البيانات، المفتاح السري، إلخ)
nano dalal_saudi/settings.py
```

### 5. تشغيل المشروع
```bash
# تطبيق الهجرات
python manage.py makemigrations
python manage.py migrate

# إنشاء مستخدم مسؤول
python manage.py createsuperuser

# جمع الملفات الثابتة
python manage.py collectstatic

# تشغيل الخادم
python manage.py runserver 0.0.0.0:8000
```

## هيكل المشروع

```
dalal_saudi_project/
├── dalal_saudi/          # إعدادات المشروع
├── users/                # إدارة المستخدمين
├── products/             # إدارة المنتجات
├── categories/           # إدارة الفئات
├── messaging/            # نظام المراسلة
├── auctions/             # نظام المزادات
├── locations/            # نظام المواقع
├── admin_panel/          # لوحة الإدارة
├── reviews/              # نظام التقييمات
├── orders/               # إدارة الطلبات
├── templates/            # قوالب HTML
├── static/               # ملفات CSS/JS
├── media/                # ملفات المستخدمين
└── requirements.txt      # متطلبات Python
```

## الاستخدام

### للمستخدمين العاديين
1. إنشاء حساب جديد أو تسجيل الدخول
2. تصفح المنتجات أو البحث عنها
3. التواصل مع البائعين عبر نظام المراسلة
4. المشاركة في المزادات
5. عرض المواقع على الخريطة

### للبائعين
1. إضافة منتجات جديدة مع الصور والتفاصيل
2. تحديد الموقع الجغرافي للمنتج
3. إنشاء مزادات (اختياري)
4. التواصل مع المشترين المهتمين
5. إدارة المنتجات والطلبات

### للمسؤولين
1. مراجعة والموافقة على المنتجات الجديدة
2. إدارة المستخدمين والصلاحيات
3. مراقبة النشاط والإحصائيات
4. إدارة إعدادات النظام

## الأمان

- تشفير كلمات المرور باستخدام Django's PBKDF2
- حماية من هجمات CSRF و XSS
- تحقق من صحة البيانات المدخلة
- نظام صلاحيات متقدم
- تسجيل العمليات الحساسة

## الدعم والصيانة

- مراقبة الأداء والأخطاء
- نسخ احتياطية دورية لقاعدة البيانات
- تحديثات أمنية منتظمة
- دعم فني متواصل

## الترخيص

هذا المشروع مطور خصيصاً لأغراض تجارية. جميع الحقوق محفوظة.

## التواصل

للاستفسارات والدعم الفني، يرجى التواصل عبر:
- البريد الإلكتروني: support@dalalsaudi.com
- الهاتف: +966-XX-XXX-XXXX

---

**تم التطوير بواسطة:** Manus AI  
**الإصدار:** 1.0  
**تاريخ الإصدار:** يونيو 2025


doman 
dalalalsaudia.com


ip :167.99.0.225                          pass : osam0Esmael



 HOSTENGER ACCOUNT 

 USER : 89fares@gmail.com   PASS : 7i-Fz7c#i_m86j2

 go dady account 
 USER : 89fares@gmail.com   PASS : Marshoud@1234


digitalocean
accunt : 
user : 89fares@gmail.com                      pass: 7i-Fz7c#i_m86jK

ssh root@167.99.0.225                       pass : osam0Esmael 

adduser sammy          pass :osama

su sammy
cd ~/myprojectdir

user : AdminCars      pass : cars@2024


dalal_saudi
source myprojectenv/bin/activate
n/gunicorn --version
gunicorn (version 23.0.0)

python -m venv venv
>venv\scripts\activate
>pip3 install django
>django-admin startproject dicussion_board
>django-admin startproject dicussion_board .
>py manage.py runserver
py manage.py startapp
>c
cyrl c
>py manage.py runserver 5000
>django-admin startapp boards
------>python manage.py makemigrations
------>python manage.py migrate

python manage.py createsuperuser


python manage.py collectstatic

su sammy
cd ~/myprojectdir
source myprojectenv/bin/activate

deactivate
sudo apt install gunicornsudo apt install gunicorn

sudo apt install snap
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot/usr/bin/certbot
sudo certbot --nginx
sudo systemctl restart gunicorn
sudo systemctl daemon-reload 
sudo systemctl restart gunicorn.socket gunicorn.service
sudo nginx -t && sudo systemctl restart nginx
sudo nano /etc/nginx/sites-available/myproject
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled

sudo nano /etc/nginx/sites-available/myproject

