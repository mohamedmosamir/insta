import instaloader
import getpass
import sys
import os
import time

MAX_TRIES = 3  # عدد المحاولات المسموح بها

def print_banner():
    banner = r"""



 __  .__   __.      _______.___________.    ___      
|  | |  \ |  |     /       |           |   /   \     
|  | |   \|  |    |   (----`---|  |----`  /  ^  \    
|  | |  . `  |     \   \       |  |      /  /_\  \   
|  | |  |\   | .----)   |      |  |     /  _____  \  
|__| |__| \__| |_______/       |__|    /__/     \__\ 
    ================================
     📸 InstaOSINT - أداة جمع معلومات إنستجرام
    ================================
    """
    print(banner)

def login(loader, username):
    session_path = f"session-{username}"

    # محاولة تحميل جلسة محفوظة
    if os.path.exists(session_path):
        try:
            loader.load_session_from_file(username, session_path)
            print("✅ تم تحميل الجلسة من الملف.")
            return True
        except Exception as e:
            print(f"⚠️ فشل تحميل الجلسة: {e}")

    # محاولة تسجيل الدخول عدة مرات
    for attempt in range(1, MAX_TRIES + 1):
        print(f"🔐 المحاولة {attempt}/{MAX_TRIES}")
        password = getpass.getpass(f"أدخل كلمة المرور لحساب {username}: ").strip()

        try:
            # اختبار كلمة المرور
            loader.context.log("📡 جاري التحقق من بيانات الدخول...")
            loader.login(username, password)
            print("✅ تم تسجيل الدخول بنجاح.")
            loader.save_session_to_file(session_path)
            print("💾 تم حفظ الجلسة.")
            return True
        except instaloader.exceptions.BadCredentialsException:
            print("❌ كلمة المرور غير صحيحة.")
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            print("⚠️ الحساب مفعّل عليه التحقق بخطوتين. الرجاء الدخول يدويًا أولاً من المتصفح.")
            return False
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")

        time.sleep(1)  # انتظار بسيط قبل المحاولة التالية

    print("🚫 تم استنفاد جميع المحاولات.")
    return False

def gather_info(loader, username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)

    info = {
        "اسم المستخدم": profile.username,
        "الاسم الكامل": profile.full_name,
        "عدد المتابعين": profile.followers,
        "عدد المتابَعين": profile.followees,
        "عدد المنشورات": profile.mediacount,
        "السيرة الذاتية": profile.biography,
        "الرابط في البايو": profile.external_url,
        "الحساب موثق؟": "نعم" if profile.is_verified else "لا",
        "حساب خاص؟": "نعم" if profile.is_private else "لا"
    }

    followers_list = []
    followees_list = []

    print("\n⏳ جاري جمع أسماء المتابعين...")
    try:
        for follower in profile.get_followers():
            followers_list.append(follower.username)
        print(f"✅ تم جمع {len(followers_list)} متابعين.")
    except Exception as e:
        print(f"⚠️ لم يتمكن من جمع المتابعين: {e}")

    print("⏳ جاري جمع أسماء الحسابات التي يتابعها المستخدم...")
    try:
        for followee in profile.get_followees():
            followees_list.append(followee.username)
        print(f"✅ تم جمع {len(followees_list)} حسابات متابَعة.")
    except Exception as e:
        print(f"⚠️ لم يتمكن من جمع المتابَعين: {e}")

    return info, followers_list, followees_list

def save_info(info, username):
    filename = f"{username}_info.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for key, value in info.items():
            file.write(f"{key}: {value}\n")
    print(f"✅ تم حفظ المعلومات في الملف: {filename}")

def save_list(usernames, filename):
    with open(filename, "w", encoding="utf-8") as file:
        for user in usernames:
            file.write(user + "\n")
    print(f"✅ تم حفظ القائمة في الملف: {filename}")

if __name__ == "__main__":
    print_banner()
    loader = instaloader.Instaloader()

    insta_username = input("أدخل اسم المستخدم لحسابك في إنستجرام (للدخول): ").strip()
    if not login(loader, insta_username):
        sys.exit(1)

    target_username = input("أدخل اسم المستخدم المستهدف: ").strip()
    info, followers, followees = gather_info(loader, target_username)

    for key, value in info.items():
        print(f"{key}: {value}")

    save_info(info, target_username)

    if followers:
        save_list(followers, f"{target_username}_followers.txt")
    if followees:
        save_list(followees, f"{target_username}_followees.txt")
