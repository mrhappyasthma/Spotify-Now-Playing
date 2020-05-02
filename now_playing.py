import ctypes
import os

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetClassName = ctypes.windll.user32.GetClassNameW
OpenProcess = ctypes.windll.kernel32.OpenProcess
CloseHandle = ctypes.windll.kernel32.CloseHandle
GetProcessImageFileName = ctypes.windll.psapi.GetProcessImageFileNameW

titles = []

# Iterate all windows searching for Spotify.exe. If it exists, extract the
# song name from the window title.
#
# Return `False` to stop iterating. Returning `True` is equivalent to "continue".
def foreach_window(hwnd, lParam):
  if not IsWindowVisible(hwnd):
    return True

  # Determine if the window is of type `Chrome_WidgetWin_0`, which Spotify uses.
  buffer_length = 500
  buffer = ctypes.create_unicode_buffer(buffer_length)
  GetClassName(hwnd, buffer, buffer_length)
  if buffer.value != 'Chrome_WidgetWin_0':
    return True

  # Determine if this process is Spotify.exe
  lpdw_process_id = ctypes.c_ulong()
  GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_process_id))
  PROCESS_VM_READ = 0x0010
  PROCESS_QUERY_INFORMATION = 0x0400
  process_handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, lpdw_process_id)
  buffer = ctypes.create_unicode_buffer(buffer_length)
  GetProcessImageFileName(process_handle, buffer, buffer_length)
  executable_name = os.path.basename(buffer.value)
  CloseHandle(process_handle)
  if executable_name != "Spotify.exe":
    return True

  # Extract the window title bar text, which contains the song name.
  buffer = ctypes.create_unicode_buffer(buffer_length)
  GetWindowText(hwnd, buffer, buffer_length)
  text = buffer.value
  if len(text) > 0 and text != "Spotify Premium" and text != "Spotify Free":
    titles.append(text)
    return False

  # It's unlikely we get here, but if for some reason the window text parsing
  # fails, we can keep iterating through the windows.
  return True


# Enumerate all of the windows looking for Spotify.
EnumWindows(EnumWindowsProc(foreach_window), 0)

print titles[0] if len(titles) == 1 else 'No song playing...'
