# 🎬🌿 Movie Folder Covers

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![No Internet](https://img.shields.io/badge/no%20internet-required-success)

تطبيق سطح مكتب **عربي** و**مجاني** لنظام Windows يتيح لك تعيين صورة غلاف
لأي مجلد فيلم بحيث تظهر الصورة كأيقونة المجلد في مستكشف الملفات — **دون
المساس بأي ملف على مجلدات الشبكة**.

![لقطة شاشة](assets/screenshot.png)

---

## ✨ المميزات

- 🎨 **واجهة خضراء أنيقة** مع دعم كامل للعربية
- 🔒 **آمن على مجلدات الشبكة** — يكتشف UNC و Mapped drives ويتخطاها
- 🤖 **اكتشاف تلقائي ذكي** للصور (`poster`, `cover`, `folder`, `movie`...)
- 🖼️ **أيقونات احترافية** بأحجام 256, 64, 48, 32, 16
- ⚡ **معالجة في الخلفية** — الواجهة لا تتجمد
- ♻️ **إزالة كاملة** لاستعادة المجلد لشكله الطبيعي
- 💾 **حفظ محلي فقط** في `%LOCALAPPDATA%\MovieFolderCovers`
- 🌐 **بدون إنترنت** — لا تليمترية ولا تتبّع

---

## 📸 كيف يعمل

1. اختر مجلد فيلم عبر **"➕ إضافة مجلد"**
2. اضغط **"🔄 تحديث الأغلفة"**
3. سيقوم البرنامج بـ:
   - قراءة الصور داخل المجلد (أو استخدام الغلاف الذي اخترته)
   - توليد أيقونة `.ico` بأحجام متعددة
   - إنشاء `desktop.ini` داخل المجلد لربط الأيقونة
   - حفظ نسخة في `%LOCALAPPDATA%`

> قد تحتاج `F5` في مستكشف الملفات لرؤية التغيير.

---

## 🚀 التثبيت

### المتطلبات
- **Windows 10 / 11**
- **Python 3.9+**

### من المصدر

```bash
git clone https://github.com/USERNAME/movie-folder-covers.git
cd movie-folder-covers
pip install -r requirements.txt
python movie_folder_covers.py
