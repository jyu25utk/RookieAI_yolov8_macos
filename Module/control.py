import os
import sys
import platform
import random
import time
from Module.config import Root
from Module.logger import logger

# Platform-specific mouse library import
try:
    import mouse
    mouse_available = True
except (ImportError, OSError) as e:
    mouse = None
    mouse_available = False
    logger.warning(f"Mouse library not available: {e}")

# Cross-platform imports
try:
    import pyautogui
    pyautogui.FAILSAFE = False  # Disable failsafe for automated mouse movement
except ImportError:
    pyautogui = None
    logger.warning("pyautogui not available")

try:
    from pynput import keyboard, mouse as pynput_mouse
    from pynput.mouse import Button, Listener as MouseListener
except ImportError:
    keyboard = None
    pynput_mouse = None
    logger.warning("pynput not available")

# Platform-specific imports
CURRENT_PLATFORM = platform.system().lower()
logger.info(f"Detected platform: {CURRENT_PLATFORM}")

# Windows-specific imports (only load on Windows)
if CURRENT_PLATFORM == "windows":
    try:
        import win32api
        import win32con
        import ctypes
        import importlib.machinery
        import importlib.util
        
        # Load Windows-specific hardware drivers
        try:
            msdk_dll = ctypes.windll.LoadLibrary(f"{Root}/DLLs/x64_msdk.dll")
            msdk_dll.M_Open_VidPid.restype = ctypes.c_uint64
            msdk_hdl = msdk_dll.M_Open_VidPid(0x1532, 0x98)
            logger.info("飞易来USB driver loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load 飞易来USB driver: {e}")
            msdk_dll = None
            msdk_hdl = None
        
        try:
            LG_driver = ctypes.CDLL(f"{Root}/DLLs/LGmouseControl/MouseControl.dll")
            logger.info("Logitech driver loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load Logitech driver: {e}")
            LG_driver = None
        
        try:
            kmNet = path_import("kmNet")
            logger.info("KmBoxNet loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load KmBoxNet: {e}")
            kmNet = None
            
    except ImportError as e:
        logger.warning(f"Windows-specific modules not available: {e}")
        win32api = None
        win32con = None
        msdk_dll = None
        LG_driver = None
        kmNet = None

# macOS-specific imports
elif CURRENT_PLATFORM == "darwin":
    try:
        import Quartz
        from Quartz import CGEventSourceCreate, kCGEventSourceStateHIDSystemState
        from Quartz import CGEventCreateMouseEvent, CGEventPost, kCGHIDEventTap
        from Quartz import kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGEventMouseMoved
        logger.info("macOS Quartz framework loaded successfully")
    except ImportError as e:
        logger.warning(f"macOS Quartz framework not available: {e}")
        Quartz = None

# Global key state tracking for cross-platform key monitoring
_key_states = {}
_key_listener = None

def path_import(module_name):
    """
    Import Windows-specific modules (only works on Windows)
    """
    if CURRENT_PLATFORM != "windows":
        raise ImportError(f"Module {module_name} is only available on Windows")
        
    logger.debug("******************* 开始动态加载模块 *************************")
    
    # 获取当前Python版本和平台
    py_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
    platform_tag = f"{platform.system().lower()}_{platform.architecture()[0]}"
    file_name = f"{module_name}.{py_version}-{platform_tag}.pyd"
    file_path = Root / "DLLs"/ "python_pyd" / file_name
        
    loader_details = (
        importlib.machinery.ExtensionFileLoader,
        importlib.machinery.EXTENSION_SUFFIXES
    )
    tools_finder = importlib.machinery.FileFinder(
        os.path.dirname(file_path), loader_details)
    logger.debug("FileFinder: ", tools_finder)
    
    toolbox_specs = tools_finder.find_spec(module_name)
    logger.debug("find_spec: ", toolbox_specs)

    if toolbox_specs is None or toolbox_specs.loader is None:
        raise ImportError(f"无法找到或加载模块: {module_name} ({file_name})")

    toolbox = importlib.util.module_from_spec(toolbox_specs)
    logger.debug("module: ", toolbox)
    toolbox_specs.loader.exec_module(toolbox)
    logger.info("导入成功 path_import(): ", toolbox)
    logger.debug("检查sys中是否包含了此模块: ", toolbox in sys.modules)
    logger.debug("******************* 动态加载模块完成 *************************\n")
    return toolbox

def _start_key_listener():
    """Start cross-platform key state monitoring"""
    global _key_listener
    if _key_listener is None and keyboard:
        def on_press(key):
            try:
                if hasattr(key, 'vk'):
                    _key_states[key.vk] = True
                elif hasattr(key, 'value') and hasattr(key.value, 'vk'):
                    _key_states[key.value.vk] = True
            except:
                pass
                
        def on_release(key):
            try:
                if hasattr(key, 'vk'):
                    _key_states[key.vk] = False
                elif hasattr(key, 'value') and hasattr(key.value, 'vk'):
                    _key_states[key.value.vk] = False
            except:
                pass
        
        _key_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        _key_listener.start()
        logger.info("Cross-platform key listener started")

def _get_key_state_cross_platform(vk_code):
    """Get key state using cross-platform method"""
    _start_key_listener()
    return _key_states.get(vk_code, False)

def emergencStop_valorant(last_state_w, last_state_a, last_state_s, last_state_d):
    """Emergency stop function with cross-platform key detection"""
    
    if CURRENT_PLATFORM == "windows" and win32api:
        # Use Windows API for better performance on Windows
        state_w = bool(win32api.GetAsyncKeyState(0x57) & 0x8000)  # W键
        state_a = bool(win32api.GetAsyncKeyState(0x41) & 0x8000)  # A键
        state_s = bool(win32api.GetAsyncKeyState(0x53) & 0x8000)  # S键
        state_d = bool(win32api.GetAsyncKeyState(0x44) & 0x8000)  # D键
    else:
        # Use cross-platform key detection
        state_w = _get_key_state_cross_platform(0x57)  # W键
        state_a = _get_key_state_cross_platform(0x41)  # A键
        state_s = _get_key_state_cross_platform(0x53)  # S键
        state_d = _get_key_state_cross_platform(0x44)  # D键

    stop = False

    # 检测按键是否从按下变为松开
    if not state_w and last_state_w:  # 如果按键W被松开
        logger.debug("W键弹起")
        if CURRENT_PLATFORM == "windows" and kmNet:
            kmNet.keydown(22)  #保持键盘s键按下
            time.sleep(0.03)
            kmNet.keyup(22)  # 键盘s键松开
        else:
            # Cross-platform key press
            if keyboard:
                with keyboard.Controller() as kb:
                    kb.press('s')
                    time.sleep(0.03)
                    kb.release('s')
        logger.debug("S键点击")
        stop = True
        
    if not state_a and last_state_a:  # 如果按键A被松开
        logger.debug("A键弹起")
        if CURRENT_PLATFORM == "windows" and kmNet:
            kmNet.keydown(7)   #保持键盘d键按下
            time.sleep(0.03)
            kmNet.keyup(7)   # 键盘d键松开
        else:
            if keyboard:
                with keyboard.Controller() as kb:
                    kb.press('d')
                    time.sleep(0.03)
                    kb.release('d')
        logger.debug("D键点击")
        stop = True
        
    if not state_s and last_state_s:  # 如果按键S被松开
        logger.debug("S键弹起")
        if CURRENT_PLATFORM == "windows" and kmNet:
            kmNet.keydown(26)  #保持键盘w键按下
            time.sleep(0.03)
            kmNet.keyup(26)  # 键盘w键松开
        else:
            if keyboard:
                with keyboard.Controller() as kb:
                    kb.press('w')
                    time.sleep(0.03)
                    kb.release('w')
        logger.debug("W键点击")
        stop = True
        
    if not state_d and last_state_d:  # 如果按键D被松开
        logger.debug("D键弹起")
        if CURRENT_PLATFORM == "windows" and kmNet:
            kmNet.keydown(4)  #保持键盘a键按下
            time.sleep(0.03)
            kmNet.keyup(4)  # 键盘a键松开
        else:
            if keyboard:
                with keyboard.Controller() as kb:
                    kb.press('a')
                    time.sleep(0.03)
                    kb.release('a')
        logger.debug("A键点击")
        stop = True

    if stop:
        time.sleep(0.003)  # 添加一个小的延时，避免CPU占用过高

    # 返回更新后的按键状态
    return state_w, state_a, state_s, state_d

def monitor(mode):
    """Monitor right mouse button state"""
    state = None
    match mode:
        case 'KmBoxNet':
            if CURRENT_PLATFORM == "windows" and kmNet:
                state = bool(kmNet.isdown_right())
            else:
                logger.warning("KmBoxNet not available on this platform")
                state = False
        case "win32":
            if CURRENT_PLATFORM == "windows" and win32api:
                state = bool(win32api.GetAsyncKeyState(0x02) & 0x8000)
            else:
                # Cross-platform right mouse button detection
                state = _get_key_state_cross_platform(0x02)
        case "cross_platform":
            # Use cross-platform method
            state = _get_key_state_cross_platform(0x02)
    return state

def click(mode):
    """Perform mouse click using specified method"""
    match mode:
        case "飞易来USB":
            if CURRENT_PLATFORM == "windows" and msdk_dll and msdk_hdl:
                msdk_dll.M_KeyDown2(ctypes.c_uint64(msdk_hdl), 1)
                time.sleep(random.uniform(0.12, 0.17))
                msdk_dll.M_KeyDown2(ctypes.c_uint64(msdk_hdl), 2)
                time.sleep(random.uniform(0.12, 0.17))
            else:
                logger.warning("飞易来USB not available on this platform, falling back to cross-platform")
                _click_cross_platform()
        case "win32":
            if CURRENT_PLATFORM == "windows" and win32api:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(random.uniform(0.12, 0.17))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                time.sleep(random.uniform(0.12, 0.17))
            else:
                _click_cross_platform()
        case "mouse":
            if mouse_available:
                mouse.click("left")
                time.sleep(random.uniform(0.12, 0.17))
            else:
                logger.warning("Mouse library not available, falling back to cross-platform")
                _click_cross_platform()
        case "Logitech":
            if CURRENT_PLATFORM == "windows" and LG_driver:
                LG_driver.click_Left_down()
                time.sleep(random.uniform(0.12, 0.17))
                LG_driver.click_Left_up()
                time.sleep(random.uniform(0.12, 0.17))
            else:
                logger.warning("Logitech driver not available on this platform, falling back to cross-platform")
                _click_cross_platform()
        case 'KmBoxNet':
            if CURRENT_PLATFORM == "windows" and kmNet:
                kmNet.left(1)
                time.sleep(random.uniform(0.12, 0.17))
                kmNet.left(0)
                time.sleep(random.uniform(0.12, 0.17))
            else:
                logger.warning("KmBoxNet not available on this platform, falling back to cross-platform")
                _click_cross_platform()
        case "cross_platform":
            _click_cross_platform()

def _click_cross_platform():
    """Cross-platform mouse click implementation"""
    if pyautogui:
        pyautogui.click()
        time.sleep(random.uniform(0.12, 0.17))
    elif pynput_mouse:
        mouse_controller = pynput_mouse.Controller()
        mouse_controller.click(Button.left, 1)
        time.sleep(random.uniform(0.12, 0.17))
    else:
        logger.error("No cross-platform mouse library available")

def move(mode, centerx, centery):
    """Move mouse using specified method"""
    match mode:
        case "飞易来USB":
            if CURRENT_PLATFORM == "windows" and msdk_dll and msdk_hdl:
                msdk_dll.M_MoveR2(ctypes.c_uint64(msdk_hdl), int(centerx), int(centery))
            else:
                logger.warning("飞易来USB not available on this platform, falling back to cross-platform")
                _move_cross_platform(centerx, centery)
        case "win32":
            if CURRENT_PLATFORM == "windows" and win32api:
                win32api.mouse_event(
                    win32con.MOUSEEVENTF_MOVE, int(centerx), int(centery), 0, 0
                )
            else:
                _move_cross_platform(centerx, centery)
        case "mouse":
            if mouse_available:
                mouse.move(int(centerx), int(centery), False)
            else:
                logger.warning("Mouse library not available, falling back to cross-platform")
                _move_cross_platform(centerx, centery)
        case "Logitech":
            if CURRENT_PLATFORM == "windows" and LG_driver:
                LG_driver.move_R(int(centerx), int(centery))
            else:
                logger.warning("Logitech driver not available on this platform, falling back to cross-platform")
                _move_cross_platform(centerx, centery)
        case 'KmBoxNet':
            if CURRENT_PLATFORM == "windows" and kmNet:
                kmNet.enc_move(int(centerx), int(centery))
            else:
                logger.warning("KmBoxNet not available on this platform, falling back to cross-platform")
                _move_cross_platform(centerx, centery)
        case "cross_platform":
            _move_cross_platform(centerx, centery)

def _move_cross_platform(centerx, centery):
    """Cross-platform mouse movement implementation"""
    if CURRENT_PLATFORM == "darwin" and Quartz:
        # Use macOS Quartz for precise mouse movement
        try:
            current_pos = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
            new_x = current_pos.x + int(centerx)
            new_y = current_pos.y + int(centery)
            
            event = CGEventCreateMouseEvent(
                None, kCGEventMouseMoved, (new_x, new_y), 0
            )
            CGEventPost(kCGHIDEventTap, event)
        except Exception as e:
            logger.warning(f"macOS Quartz mouse movement failed: {e}, falling back to pyautogui")
            if pyautogui:
                pyautogui.move(int(centerx), int(centery))
    elif pyautogui:
        pyautogui.move(int(centerx), int(centery))
    elif pynput_mouse:
        mouse_controller = pynput_mouse.Controller()
        current_pos = mouse_controller.position
        mouse_controller.position = (current_pos[0] + int(centerx), current_pos[1] + int(centery))
    else:
        logger.error("No cross-platform mouse movement library available")

def press(mode, key):
    """Press key using specified method"""
    match mode:
        case "飞易来USB":
            if CURRENT_PLATFORM == "windows" and msdk_dll and msdk_hdl:
                msdk_dll.M_KeyDown2(ctypes.c_uint64(msdk_hdl), key)
            else:
                _press_cross_platform(key)
        case "win32":
            if CURRENT_PLATFORM == "windows" and win32api:
                win32api.keybd_event(key, 0, 0, 0)
            else:
                _press_cross_platform(key)
        case "mouse":
            if mouse_available:
                mouse.press(key)
            else:
                logger.warning("Mouse library not available, falling back to cross-platform")
                _press_cross_platform(key)
        case "Logitech":
            if CURRENT_PLATFORM == "windows" and LG_driver:
                LG_driver.press_key(key)
            else:
                _press_cross_platform(key)
        case "cross_platform":
            _press_cross_platform(key)

def release(mode, key):
    """Release key using specified method"""
    match mode:
        case "飞易来USB":
            if CURRENT_PLATFORM == "windows" and msdk_dll and msdk_hdl:
                msdk_dll.M_KeyUp2(ctypes.c_uint64(msdk_hdl), key)
            else:
                _release_cross_platform(key)
        case "win32":
            if CURRENT_PLATFORM == "windows" and win32api:
                win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
            else:
                _release_cross_platform(key)
        case "mouse":
            if mouse_available:
                mouse.release(key)
            else:
                logger.warning("Mouse library not available, falling back to cross-platform")
                _release_cross_platform(key)
        case "Logitech":
            if CURRENT_PLATFORM == "windows" and LG_driver:
                LG_driver.release_key(key)
            else:
                _release_cross_platform(key)
        case "cross_platform":
            _release_cross_platform(key)

def _press_cross_platform(key):
    """Cross-platform key press implementation"""
    if keyboard:
        kb = keyboard.Controller()
        # Convert VK code to key if needed
        if isinstance(key, int):
            # This is a simplified mapping - you might need to expand this
            key_map = {0x20: keyboard.Key.space, 0x0D: keyboard.Key.enter}
            key = key_map.get(key, str(chr(key)).lower() if 32 <= key <= 126 else None)
        if key:
            kb.press(key)
    else:
        logger.error("No cross-platform keyboard library available")

def _release_cross_platform(key):
    """Cross-platform key release implementation"""
    if keyboard:
        kb = keyboard.Controller()
        # Convert VK code to key if needed
        if isinstance(key, int):
            key_map = {0x20: keyboard.Key.space, 0x0D: keyboard.Key.enter}
            key = key_map.get(key, str(chr(key)).lower() if 32 <= key <= 126 else None)
        if key:
            kb.release(key)
    else:
        logger.error("No cross-platform keyboard library available")

# Platform compatibility check
def check_platform_compatibility():
    """Check if current platform is supported and log available features"""
    logger.info(f"Platform: {CURRENT_PLATFORM}")
    
    if CURRENT_PLATFORM == "windows":
        logger.info("Windows platform detected - full hardware support available")
        if win32api:
            logger.info("✓ Windows API available")
        if msdk_dll:
            logger.info("✓ 飞易来USB driver available")
        if LG_driver:
            logger.info("✓ Logitech driver available")
        if kmNet:
            logger.info("✓ KmBoxNet available")
    elif CURRENT_PLATFORM == "darwin":
        logger.info("macOS platform detected - using cross-platform methods")
        if Quartz:
            logger.info("✓ macOS Quartz framework available")
    else:
        logger.info("Linux/Other platform detected - using cross-platform methods")
    
    if pyautogui:
        logger.info("✓ PyAutoGUI available")
    if keyboard and pynput_mouse:
        logger.info("✓ pynput available")
    if mouse:
        logger.info("✓ mouse library available")

# Initialize platform compatibility check
check_platform_compatibility()
