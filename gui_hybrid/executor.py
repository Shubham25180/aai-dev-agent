import pyautogui

class Executor:
    """
    Executes GUI actions using pyautogui.
    """
    def move_and_click(self, x, y):
        """Move mouse to (x, y) and click."""
        pyautogui.moveTo(x, y)
        pyautogui.click()

    def type_text(self, text):
        """Type text at the current cursor location."""
        pyautogui.typewrite(text) 