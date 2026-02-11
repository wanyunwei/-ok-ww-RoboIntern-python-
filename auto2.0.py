# 仅对wuwa进行自动化，其他的游戏以时间隔开，这样不容易坏了一个就都不行了
# 目前的使用前提：（未优化）
# 1.游戏内分辨率1920×1080,暂时未做到修正
# 2.游戏内编队能打日常，且无死亡
# 3.暂不支持热更新与版本更新
import os
import time
import pyautogui
import subprocess
import pygetwindow as gw
from pyautogui import moveTo

image_status_dict = {
        r"C:\Users\chen0\Documents\python_code\wuwa_auto2.0\wuwaAuto\version_update.png": 2,
        r"C:\Users\chen0\Documents\python_code\wuwa_auto2.0\wuwaAuto\hot_update.png": 3,
        r"C:\Users\chen0\Documents\python_code\wuwa_auto2.0\wuwaAuto\wuwa_login.png": 1,
    }


class app:
    name: str
    path: str
    title: str
wuwa = app()
wuwa.path = r'C:\Program Files\Wuthering Waves\Wuthering Waves Game\Wuthering Waves.exe'
wuwa.name = 'Wuthering Waves.exe'
wuwa.title = '鸣潮'
okww = app()
okww.path = r"C:\Users\chen0\Saved Games\okww\ok-ww\ok-ww.exe"
okww.name = 'ok-ww.exe'
okww.title = 'ok-ww.exe'

# 静音
def mute_compurter():
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    # 获取默认的音频端点设备
    speakers = AudioUtilities.GetSpeakers()
    # 直接使用 EndpointVolume 属性获取音量接口
    volume_interface = speakers.EndpointVolume
    volume_interface.SetMute(1, None)
    print("已静音")
# 检测图片是否在屏幕上
def check_image(image_path ,check_interval =2,time_out = 120,confidence=0.6 ):
    start_time = time.time()
    elapsed_time = 0
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > time_out:
            break
        try:

            location = pyautogui.locateOnScreen(image_path ,confidence=confidence)

            if location:
                print(f"已找到图片{image_path}")
                return True
        except pyautogui.ImageNotFoundException:
            print(F"已耗时{elapsed_time:.1f}s,未找到图片{image_path}")


        time.sleep(check_interval)

# 启动程序
def start_app_no_wait(app_path):
    try:
        subprocess.Popen(app_path)
        print(f"已尝试启动程序{app_path}")
        return True
    except:
        print("start_app_no_wait启动程序出错")
        return False
# 检测程序是否启动成功,循环检测
def is_app_running(app_name, psutil=None,timeout=120, check_interval=5):
    import psutil
    """
    检查指定名称的应用程序是否正在运行，支持超时和定期检查

    参数:
        app_name (str): 应用程序名称（如："chrome.exe", "notepad.exe", "wuwa.exe"等）
        psutil: psutil模块对象，用于进程操作
        timeout (int): 超时时间（秒），默认为60秒
        check_interval (int): 检查间隔（秒），默认为5秒

    返回:
        bool: 如果应用程序在超时时间内启动成功返回True，否则返回False
    """
    start_time = time.time()
    last_check_time = 0
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time


        if elapsed_time > timeout:
            print(f"{app_name}启动超时")
            return False

        # 更新时间
        if current_time - last_check_time > check_interval or last_check_time == 0:
            last_check_time = current_time
            try:
                for proc in psutil.process_iter(['name']):
                    try:
                        if app_name.lower() in proc.info['name'].lower():
                            print(f"{app_name}启动成功,耗时{elapsed_time:.1f}s")
                            return True
                    except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                print(f"{app_name}尚未启动，已耗时{elapsed_time:.1f}s")
            except Exception as e:
                print(f"{app_name}检查过程中发生错误{str(e)}")

        time.sleep(0.5)
# 检查窗口出现
def wait_for_window_by_title(app_title, timeout=120, check_interval=2, ):
    print(f"正在等待{app_title}窗口出现")

    start_time = time.time()

    for i in range(int(timeout / check_interval)):
        current_time = time.time()
        elapsed_time = current_time - start_time

        windows = gw.getAllWindows()

        for window in windows:
            if window.title and app_title in window.title:
                print(f"[{elapsed_time:.1f}s] 找到窗口：{window.title}")
                print(
                    f"[{elapsed_time:.1f}s] "
                    f"窗口位置：左：{window.left},上：{window.top},右：{window.right},下：{window.bottom}\n"
                    f"窗口大小{window.width}×{window.height}"
                )
                return True
        if i % 3 == 0:
            print(f"正在等待{app_title}窗口出现，已等待{elapsed_time:.1f}s")
        time.sleep(check_interval)

    print(f"等待窗口{app_title}出现超时")
    return False
# 点击图片的函数
def click_img(img_path, confidence=0.6):
    time.sleep(1)
    img_location=pyautogui.locateCenterOnScreen(img_path, confidence=confidence)
    pyautogui.click(img_location)
def double_click_img(img_path, confidence=0.6):
    time.sleep(1)
    img_location=pyautogui.locateCenterOnScreen(img_path, confidence=confidence)
    pyautogui.doubleClick(img_location)

# 启动wuwa
# 启动√
# 登录---处理热更新的情况×    ---处理正常的情况√    ----处理登录失效的情况×
# 确定登录状态
def check_login_status(image_dict, timeout=120, check_interval=1):
    """
    检测登录状态，根据找到的图片返回对应的状态码
    :param image_dict: dict, 键为图片路径，值为该图片对应的状态码（例如：2,3,1）
    :param timeout: int, 超时时间（秒），默认120秒
    :param check_interval: float, 每次检测间隔（秒），默认1秒
    :return: 状态码（int） 或 None（超时未找到）
    """
    for img_path in image_dict:
        if not os.path.exists(img_path):
            print(f"警告：图片文件不存在 - {img_path}")
            # 你可以选择直接返回错误，或继续但跳过该文件
            # 这里选择跳过，但至少会提醒
            # 或者可以 raise FileNotFoundError

    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print(f"超时 {timeout}s，未检测到任何登录状态图片")
            return None

        # 本轮检测所有图片
        for img_path, status in image_dict.items():
            try:
                location = pyautogui.locateOnScreen(img_path)
                if location:   # 找到图片
                    print(f"已找到图片 {img_path}\n返回状态 {status}\n(\n状态1：正常登录\n状态2:版本更新\n状态3热更新\n)")
                    return status
            except pyautogui.ImageNotFoundException:
                # 图片未找到，继续检查下一张
                continue

        # 本轮未找到任何图片，打印耗时并等待
        print(f"未检测到登录状态图片，已耗时 {elapsed:.1f}s")
        time.sleep(check_interval)
# 进行登录
def wuwaLogin():
    state=check_login_status(image_status_dict)
    if state == 1:
        click_img('./wuwaAuto/wuwa_login.png')
    elif state == 2:
        pass
    elif state == 3:
        pass
    # 逻辑：先关掉公告，再等待五分钟（等他热更新完，要是多于五分钟，再显示超时），然后点击热更新完出现的“确定”按钮，等他自己重启，编译着色器，然后登录

    else:
        print("登录错误")

# 检测角色是否死亡×
# 检测角色是否达标×
def openWuwa():
    start_app_no_wait(wuwa.path)
    is_app_running(wuwa.name)
    wait_for_window_by_title(wuwa.title)
    wuwaLogin()
# 自动点击开始每日，因为位置不在中心，所以不能套用上面的函数
def click_begin_daily():
    try:
        img_location = pyautogui.locateOnScreen('./wuwaAuto/dailyBeginDark.png', confidence=0.9)
        if img_location:
            # 计算相对位置点击
            click_x = img_location.left + img_location.width * 0.85
            click_y = img_location.top + img_location.height * 0.5
            pyautogui.click(click_x, click_y)
            print(f"点击位置: ({click_x}, {click_y})")
            return True
        else:
            print("未找到dailyBeginDark.png图片")
            return False
    except Exception as e:
        print(f"点击开始每日出错: {e}")
        return False
# 打开okww
def openOkww():
    start_app_no_wait(okww.path)
    check_image('./wuwaAuto/dailyAndWeeklyDark.png')
    time.sleep(2)
    click_img('./wuwaAuto/dailyAndWeeklyDark.png')
    time.sleep(2)
    check_image('./wuwaAuto/dailyBeginDark.png')
    click_begin_daily()
# 检测任务是否完成
def check_game_over_once():
            """单次检测游戏是否结束"""
            try:
                game_over_location = pyautogui.locateOnScreen('./wuwaAuto/gameOverDark.png', confidence=0.9)
                if game_over_location:
                    return 1
            except Exception as e:

                return False
def is_game_over():

    max_detection_time = 2400  # 最大检测时间40min
    detection_interval = 20  # 每20秒检测一次
    start_time = time.time()
    detection_count = 0

    while True:
        try:
            detection_count += 1
            current_time = time.time()
            elapsed_time = current_time - start_time

            # 检查是否超时
            if elapsed_time > max_detection_time:
                print(f"检测超时（{max_detection_time}秒），停止检测")
                break

            # 检测任务是否完成
            if check_game_over_once():
                print(f"第{detection_count}次检测：发现任务完成图片！")
                print(f"检测耗时：{elapsed_time:.2f}秒")

                # 等待10秒确保游戏结束

                break

            # 每隔一段时间打印状态
            if detection_count % 1 == 0:
                print(f"第{detection_count}次检测：未发现任务完成图片，已检测{elapsed_time:.0f}秒")

            # 等待下次检测
            time.sleep(detection_interval)

        except KeyboardInterrupt:
            print("\n用户中断程序")
            break
        except Exception as e:
            print(f"检测过程中出现异常: {e}")
            # 继续检测

    print("程序结束")
# 关闭程序
def close_app_by_keyboard():

    time.sleep(0.1)
    pyautogui.keyDown("alt")
    time.sleep(0.1)
    pyautogui.press("F4")
    time.sleep(0.1)
    pyautogui.keyUp('alt')

def main():
    mute_compurter()
    openWuwa()
    openOkww()
    print("所有程序已启动，开始检测任务是否完成")
    is_game_over()
    time.sleep(1)
    close_app_by_keyboard()
    close_app_by_keyboard()


if __name__ == "__main__":
    main()
