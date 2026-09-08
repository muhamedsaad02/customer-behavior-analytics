import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

# ============================================================
# الإعدادات العامة
# ============================================================
N_USERS = 28000          # عدد العملاء الفريدين
N_SESSIONS = 100000      # عدد الجلسات الكلي (بعض العملاء هيرجعوا أكتر من مرة)
START_DATE = datetime(2025, 3, 1)
END_DATE = datetime(2025, 8, 31)

channels = ['Organic', 'Paid Ads', 'Social', 'Email']
channel_weights = [0.35, 0.30, 0.20, 0.15]

campaign_types = ['Discount', 'New Launch', 'Influencer', 'None']
campaign_weights = [0.30, 0.20, 0.15, 0.35]

devices = ['Mobile', 'Desktop']
device_weights = [0.65, 0.35]

# مدن حقيقية بدل الأسماء المجردة - كل مدينة ليها تصنيف Metro/Non-Metro ثابت ومنطقي
city_info = {
    'Cairo':        {'tier': 'Metro',     'weight': 0.28},
    'Giza':         {'tier': 'Metro',     'weight': 0.14},
    'Alexandria':   {'tier': 'Metro',     'weight': 0.13},
    'Mansoura':     {'tier': 'Non-Metro', 'weight': 0.07},
    'Tanta':        {'tier': 'Non-Metro', 'weight': 0.06},
    'Zagazig':      {'tier': 'Non-Metro', 'weight': 0.05},
    'Ismailia':     {'tier': 'Non-Metro', 'weight': 0.05},
    'Assiut':       {'tier': 'Non-Metro', 'weight': 0.05},
    'Luxor':        {'tier': 'Non-Metro', 'weight': 0.04},
    'Aswan':        {'tier': 'Non-Metro', 'weight': 0.04},
    'Port Said':    {'tier': 'Non-Metro', 'weight': 0.04},
    'Suez':         {'tier': 'Non-Metro', 'weight': 0.03},
    'Damietta':     {'tier': 'Non-Metro', 'weight': 0.02},
}
cities = list(city_info.keys())
city_weights = [city_info[c]['weight'] for c in cities]

categories = ['Clothing', 'Electronics', 'Home & Kitchen', 'Beauty', 'Sports', 'Books']

# أسعار منطقية لكل فئة (متوسط وانحراف معياري)
category_price_range = {
    'Clothing': (100, 800),
    'Electronics': (500, 5000),
    'Home & Kitchen': (150, 2000),
    'Beauty': (50, 500),
    'Sports': (100, 1500),
    'Books': (50, 300),
}

# ============================================================
# الخطوة 1: نعمل قايمة عملاء ثابتة (كل عميل له خصائص ثابتة معاه طول الوقت)
# ============================================================
user_ids = [f"U{100000+i}" for i in range(N_USERS)]
user_city = {uid: random.choices(cities, weights=city_weights)[0] for uid in user_ids}

# نحدد مين هيكون "returning" - يعني هيعمل أكتر من session
# نديله توزيع واقعي: 70% من العملاء session واحدة بس، والباقي بيرجعوا بمعدلات مختلفة
returning_prob = np.random.rand(N_USERS)
user_session_count = {}
for i, uid in enumerate(user_ids):
    if returning_prob[i] < 0.70:
        user_session_count[uid] = 1
    elif returning_prob[i] < 0.90:
        user_session_count[uid] = np.random.randint(2, 4)
    else:
        user_session_count[uid] = np.random.randint(4, 9)

# نبني قايمة الـ sessions المطلوب توليدها بناء على عدد مرات كل عميل
session_user_list = []
for uid, cnt in user_session_count.items():
    session_user_list.extend([uid] * cnt)

# لو العدد الكلي زاد أو قل عن N_SESSIONS، نظبطه
if len(session_user_list) > N_SESSIONS:
    session_user_list = random.sample(session_user_list, N_SESSIONS)
else:
    extra = N_SESSIONS - len(session_user_list)
    session_user_list.extend(random.choices(user_ids, k=extra))

random.shuffle(session_user_list)

# ============================================================
# الخطوة 2: نولد كل جلسة (session) بمنطق Funnel متسلسل صحيح
# ============================================================
rows = []
date_range_days = (END_DATE - START_DATE).days

# نتبع كام مرة كل يوزر ظهر قبل كده عشان نحدد New/Returning صح تاريخياً
user_seen_before = {}

for idx, uid in enumerate(session_user_list):
    session_id = f"S{200000+idx}"

    # تاريخ عشوائي داخل المدى
    rand_day = np.random.randint(0, date_range_days)
    session_date = START_DATE + timedelta(days=int(rand_day))

    # نضيف تأثير الويكند (السبت/الأحد نشاط أعلى شوية في المنطق بس مش هيأثر على التوليد هنا)
    channel = random.choices(channels, weights=channel_weights)[0]
    campaign = random.choices(campaign_types, weights=campaign_weights)[0]
    device = random.choices(devices, weights=device_weights)[0]
    city = user_city[uid]
    region = city_info[city]['tier']

    # تحديد User Type بناء على "هل ده أول ظهور للعميل ده ولا لأ" (منطقي وليس عشوائي)
    if uid not in user_seen_before:
        user_type = 'New'
        user_seen_before[uid] = True
    else:
        user_type = 'Returning'

    # مدة الجلسة بالدقايق - نديها توزيع واقعي (لوج نورمال) من 1 لحد 45 دقيقة
    session_duration = round(np.random.lognormal(mean=1.6, sigma=0.8), 1)
    session_duration = min(session_duration, 60.0)

    # ============================================================
    # منطق الـ Funnel المتسلسل - كل مرحلة تعتمد منطقياً على اللي قبلها
    # ============================================================
    visited_site = True  # أي صف موجود أصلاً معناه زار الموقع

    # احتمالية مشاهدة منتج أعلى لو الجلسة أطول أو الشانل مدفوع/حملة خصم
    p_view = 0.75
    if campaign == 'Discount':
        p_view += 0.08
    if session_duration > 10:
        p_view += 0.07
    viewed_product = np.random.rand() < min(p_view, 0.97)

    added_to_cart = False
    checkout_started = False
    purchase_completed = False
    order_value = 0.0
    discount_applied = False
    category = None

    if viewed_product:
        category = random.choice(categories)
        p_cart = 0.40
        if campaign == 'Discount':
            p_cart += 0.15
        if user_type == 'Returning':
            p_cart += 0.10
        added_to_cart = np.random.rand() < min(p_cart, 0.85)

    if added_to_cart:
        p_checkout = 0.55
        if user_type == 'Returning':
            p_checkout += 0.10
        checkout_started = np.random.rand() < min(p_checkout, 0.90)

    if checkout_started:
        p_purchase = 0.65
        if campaign == 'Discount':
            p_purchase += 0.10
        if device == 'Desktop':
            p_purchase += 0.05
        purchase_completed = np.random.rand() < min(p_purchase, 0.92)

    if purchase_completed:
        low, high = category_price_range[category]
        order_value = round(np.random.uniform(low, high), 2)
        discount_applied = campaign == 'Discount' and np.random.rand() < 0.7

    discount_pct = round(np.random.uniform(0.05, 0.25), 2) if discount_applied else 0.0
    revenue = round(order_value * (1 - discount_pct), 2) if purchase_completed else 0.0

    rows.append({
        'user_id': uid,
        'session_id': session_id,
        'date': session_date.strftime('%Y-%m-%d'),
        'channel': channel,
        'campaign_type': campaign,
        'device': device,
        'user_type': user_type,
        'city': city,
        'region': region,
        'session_duration_min': session_duration,
        'product_category': category if category else np.nan,
        'visited_site': visited_site,
        'viewed_product': viewed_product,
        'added_to_cart': added_to_cart,
        'checkout_started': checkout_started,
        'purchase_completed': purchase_completed,
        'order_value': order_value,
        'discount_applied': discount_applied,
        'discount_pct': discount_pct,
        'revenue': revenue,
    })

df = pd.DataFrame(rows)

# نرتب حسب التاريخ عشان يبقى شكلها منطقي زمنياً
df = df.sort_values('date').reset_index(drop=True)

# ============================================================
# زرع مشاكل تنظيف واقعية ومحسوبة (عشان يبقى فيه Data Cleaning حقيقي تتمرن عليه)
# ============================================================
n = len(df)

# 1) قيم فاضية في device (حوالي 1.5% من الصفوف)
missing_device_idx = np.random.choice(n, size=int(n * 0.015), replace=False)
df.loc[missing_device_idx, 'device'] = np.nan

# 2) قيم فاضية في channel (حوالي 1% من الصفوف)
missing_channel_idx = np.random.choice(n, size=int(n * 0.01), replace=False)
df.loc[missing_channel_idx, 'channel'] = np.nan

# 3) عدم اتساق في كتابة device (بعضها small case أو فيها مسافات زيادة)
inconsistent_device_idx = np.random.choice(
    df[df['device'].notna()].index, size=int(n * 0.03), replace=False
)
def mess_device(val):
    choice = random.choice(['lower', 'upper', 'space'])
    if choice == 'lower':
        return val.lower()
    elif choice == 'upper':
        return val.upper()
    else:
        return f" {val} "
df.loc[inconsistent_device_idx, 'device'] = df.loc[inconsistent_device_idx, 'device'].apply(mess_device)

# 4) عدم اتساق في كتابة channel (نفس الفكرة)
inconsistent_channel_idx = np.random.choice(
    df[df['channel'].notna()].index, size=int(n * 0.025), replace=False
)
df.loc[inconsistent_channel_idx, 'channel'] = df.loc[inconsistent_channel_idx, 'channel'].apply(mess_device)

# 5) صفوف مكررة بالكامل (نكرر عينة عشوائية من الصفوف ونضيفها في الآخر) - حوالي 1%
dup_rows = df.sample(n=int(n * 0.01), random_state=1)
df = pd.concat([df, dup_rows], ignore_index=True)

# 6) بعض قيم session_duration_min شاذة لكن منطقية الحدوث (جلسات طويلة جداً بالغلط أو صفر)
outlier_idx = np.random.choice(df.index, size=int(n * 0.005), replace=False)
df.loc[outlier_idx, 'session_duration_min'] = np.random.choice([0.0, 180.5, 240.0], size=len(outlier_idx))

# نعيد الترتيب بعد إضافة التكرار
df = df.sample(frac=1, random_state=7).reset_index(drop=True)

# ============================================================
# حفظ الملف
# ============================================================
output_path = '/mnt/user-data/outputs/customer_behavior_funnel_data.csv'
df.to_csv(output_path, index=False)

print("تم توليد الداتا بنجاح ✅")
print(f"عدد الصفوف: {len(df)}")
print(f"عدد الأعمدة: {len(df.columns)}")
print(f"عدد العملاء الفريدين: {df['user_id'].nunique()}")
print("\nتوزيع الـ Funnel:")
print(f"  Visited:   {df['visited_site'].sum()}")
print(f"  Viewed:    {df['viewed_product'].sum()}")
print(f"  Cart:      {df['added_to_cart'].sum()}")
print(f"  Checkout:  {df['checkout_started'].sum()}")
print(f"  Purchase:  {df['purchase_completed'].sum()}")
print("\nتوزيع User Type:")
print(df['user_type'].value_counts())
print("\nنموذج من الصفوف:")
print(df.head(10).to_string())

# فحص المنطقية - لازم كل الطلبات اللي مفيهاش purchase يكون order_value=0
inconsistent = df[(df['purchase_completed'] == False) & (df['order_value'] != 0)]
print(f"\nعدد الصفوف الغير منطقية (المفروض تكون صفر): {len(inconsistent)}")
