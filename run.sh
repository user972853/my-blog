#!/bin/bash
# اگر محیط مجازی وجود ندارد، ایجاد می‌کنیم
if [ ! -d "./venv" ]; then
    python3 -m venv venv
fi

# فعال‌سازی محیط مجازی
source venv/bin/activate

# نصب بسته‌های مورد نیاز به صورت مستقیم
pip install markdown jinja2 pyyaml


# اجرای اسکریپت پایتون
python generate.py
