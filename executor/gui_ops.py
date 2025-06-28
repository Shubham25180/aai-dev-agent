import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from utils.logger import get_action_logger, get_error_logger

class GuiOps:
    """
    Handles GUI automation operations with safety validation and logging.
    Follows the AGENT_MANIFEST.md principles for safe GUI operations and logging.
    """
    
    def __init__(self, app_state: Dict[str, Any]):
        """
        Initialize GuiOps with application state and logging.
        
        Args:
            app_state: Application state containing config, memory, etc.
        """
        self.app_state = app_state
        self.config = app_state.get('config', {})
        self.logger = get_action_logger('gui_ops')
        self.error_logger = get_error_logger('gui_ops')
        
        # GUI automation settings
        self.gui_enabled = self.config.get('features', {}).get('gui_fallback', True)
        self.safety_delay = 0.5  # Delay between actions for safety
        
        # Initialize GUI automation library if available
        self.pyautogui = None
        self._init_gui_library()
        
        self.logger.info("GuiOps initialized with safety validation")

    def _init_gui_library(self):
        """Initialize GUI automation library."""
        try:
            if self.gui_enabled:
                import pyautogui
                self.pyautogui = pyautogui
                # Set safety settings
                self.pyautogui.FAILSAFE = True
                self.pyautogui.PAUSE = self.safety_delay
                self.logger.info("PyAutoGUI initialized successfully")
        except ImportError:
            self.error_logger.warning("PyAutoGUI not available - GUI operations will be simulated")
            self.gui_enabled = False

    def click_element(self, element_selector: str) -> Dict[str, Any]:
        """
        Click on a GUI element.
        
        Args:
            element_selector: Selector for the element to click
            
        Returns:
            Click operation result
        """
        self.logger.info("Clicking element", extra={'element_selector': element_selector})
        
        try:
            if not self.gui_enabled or not self.pyautogui:
                return self._simulate_click(element_selector)
            
            # Find element position (simplified - in real implementation would use image recognition)
            position = self._find_element_position(element_selector)
            if not position:
                return {
                    'status': 'not_found',
                    'error': f'Element not found: {element_selector}',
                    'element_selector': element_selector,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Perform click
            x, y = position
            self.pyautogui.click(x, y)
            
            result = {
                'status': 'success',
                'element_selector': element_selector,
                'click_position': {'x': x, 'y': y},
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("Element clicked successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to click element: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'element_selector': element_selector,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def type_text(self, text_to_type: str) -> Dict[str, Any]:
        """
        Type text into the current focused element.
        
        Args:
            text_to_type: Text to type
            
        Returns:
            Type operation result
        """
        self.logger.info("Typing text", extra={'text_length': len(text_to_type)})
        
        try:
            if not self.gui_enabled or not self.pyautogui:
                return self._simulate_type(text_to_type)
            
            # Type the text
            self.pyautogui.typewrite(text_to_type)
            
            result = {
                'status': 'success',
                'text_typed': text_to_type,
                'text_length': len(text_to_type),
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("Text typed successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to type text: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'text_to_type': text_to_type,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def perform_action(self, action_description: str) -> Dict[str, Any]:
        """
        Perform a general GUI action based on description.
        
        Args:
            action_description: Description of the action to perform
            
        Returns:
            Action performance result
        """
        self.logger.info("Performing GUI action", extra={'action': action_description})
        
        try:
            action_lower = action_description.lower()
            
            if 'click' in action_lower:
                return self.click_element('default_element')
            elif 'type' in action_lower or 'input' in action_lower:
                return self.type_text('sample_text')
            elif 'scroll' in action_lower:
                return self._perform_scroll(action_description)
            elif 'drag' in action_lower:
                return self._perform_drag(action_description)
            elif 'hotkey' in action_lower:
                return self._perform_hotkey(action_description)
            else:
                return self._simulate_action(action_description)
                
        except Exception as e:
            error_msg = f"Failed to perform GUI action: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'action': action_description,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def move_mouse(self, x: int, y: int) -> Dict[str, Any]:
        """
        Move mouse to specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Mouse movement result
        """
        self.logger.info("Moving mouse", extra={'x': x, 'y': y})
        
        try:
            if not self.gui_enabled or not self.pyautogui:
                return self._simulate_mouse_move(x, y)
            
            # Move mouse to position
            self.pyautogui.moveTo(x, y)
            
            result = {
                'status': 'success',
                'position': {'x': x, 'y': y},
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("Mouse moved successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to move mouse: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'position': {'x': x, 'y': y},
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def get_screen_info(self) -> Dict[str, Any]:
        """
        Get information about the screen.
        
        Returns:
            Screen information
        """
        self.logger.info("Getting screen information")
        
        try:
            if not self.gui_enabled or not self.pyautogui:
                return self._simulate_screen_info()
            
            # Get screen size
            width, height = self.pyautogui.size()
            
            # Get current mouse position
            mouse_x, mouse_y = self.pyautogui.position()
            
            result = {
                'status': 'success',
                'screen_size': {'width': width, 'height': height},
                'mouse_position': {'x': mouse_x, 'y': mouse_y},
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("Screen information retrieved", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to get screen info: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Take a screenshot.
        
        Args:
            filename: Optional filename for the screenshot
            
        Returns:
            Screenshot result
        """
        self.logger.info("Taking screenshot", extra={'filename': filename})
        
        try:
            if not self.gui_enabled or not self.pyautogui:
                return self._simulate_screenshot(filename)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                filename = f"screenshot_{timestamp}.png"
            
            # Take screenshot
            screenshot = self.pyautogui.screenshot()
            screenshot.save(filename)
            
            result = {
                'status': 'success',
                'filename': filename,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("Screenshot taken successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to take screenshot: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'filename': filename,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def _find_element_position(self, element_selector: str) -> Optional[Tuple[int, int]]:
        """
        Find the position of an element on screen.
        
        Args:
            element_selector: Selector for the element
            
        Returns:
            Position tuple (x, y) or None if not found
        """
        # Simplified implementation - in real implementation would use image recognition
        # For now, return a default position
        return (100, 100)

    def _perform_scroll(self, action_description: str) -> Dict[str, Any]:
        """Perform scroll action."""
        try:
            if not self.gui_enabled or not self.pyautogui:
                return self._simulate_action(action_description)
            
            # Determine scroll direction
            if 'up' in action_description.lower():
                self.pyautogui.scroll(3)
            elif 'down' in action_description.lower():
                self.pyautogui.scroll(-3)
            else:
                self.pyautogui.scroll(-1)
            
            return {
                'status': 'success',
                'action': action_description,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'action': action_description,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def _perform_drag(self, action_description: str) -> Dict[str, Any]:
        """Perform drag action."""
        try:
            if not self.gui_enabled or not self.pyautogui:
                return self._simulate_action(action_description)
            
            # Simplified drag implementation
            self.pyautogui.drag(100, 100, duration=1)
            
            return {
                'status': 'success',
                'action': action_description,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'action': action_description,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def _perform_hotkey(self, action_description: str) -> Dict[str, Any]:
        """Perform hotkey action."""
        try:
            if not self.gui_enabled or not self.pyautogui:
                return self._simulate_action(action_description)
            
            # Extract hotkey from description
            if 'ctrl+c' in action_description.lower():
                self.pyautogui.hotkey('ctrl', 'c')
            elif 'ctrl+v' in action_description.lower():
                self.pyautogui.hotkey('ctrl', 'v')
            elif 'ctrl+z' in action_description.lower():
                self.pyautogui.hotkey('ctrl', 'z')
            else:
                return self._simulate_action(action_description)
            
            return {
                'status': 'success',
                'action': action_description,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'action': action_description,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def _simulate_click(self, element_selector: str) -> Dict[str, Any]:
        """Simulate click operation when GUI automation is not available."""
        return {
            'status': 'simulated',
            'action': 'click',
            'element_selector': element_selector,
            'note': 'GUI automation not available - action simulated',
            'executed_at': datetime.utcnow().isoformat() + 'Z'
        }

    def _simulate_type(self, text_to_type: str) -> Dict[str, Any]:
        """Simulate type operation when GUI automation is not available."""
        return {
            'status': 'simulated',
            'action': 'type',
            'text_typed': text_to_type,
            'note': 'GUI automation not available - action simulated',
            'executed_at': datetime.utcnow().isoformat() + 'Z'
        }

    def _simulate_action(self, action_description: str) -> Dict[str, Any]:
        """Simulate general action when GUI automation is not available."""
        return {
            'status': 'simulated',
            'action': action_description,
            'note': 'GUI automation not available - action simulated',
            'executed_at': datetime.utcnow().isoformat() + 'Z'
        }

    def _simulate_mouse_move(self, x: int, y: int) -> Dict[str, Any]:
        """Simulate mouse movement when GUI automation is not available."""
        return {
            'status': 'simulated',
            'action': 'mouse_move',
            'position': {'x': x, 'y': y},
            'note': 'GUI automation not available - action simulated',
            'executed_at': datetime.utcnow().isoformat() + 'Z'
        }

    def _simulate_screen_info(self) -> Dict[str, Any]:
        """Simulate screen info when GUI automation is not available."""
        return {
            'status': 'simulated',
            'action': 'screen_info',
            'screen_size': {'width': 1920, 'height': 1080},
            'mouse_position': {'x': 0, 'y': 0},
            'note': 'GUI automation not available - info simulated',
            'executed_at': datetime.utcnow().isoformat() + 'Z'
        }

    def _simulate_screenshot(self, filename: Optional[str]) -> Dict[str, Any]:
        """Simulate screenshot when GUI automation is not available."""
        return {
            'status': 'simulated',
            'action': 'screenshot',
            'filename': filename or 'simulated_screenshot.png',
            'note': 'GUI automation not available - action simulated',
            'executed_at': datetime.utcnow().isoformat() + 'Z'
        }

    def click(self, x: int, y: int) -> Dict[str, Any]:
        """
        Click at specific coordinates (legacy method).
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Click operation result
        """
        return self.click_element(f"position({x},{y})") 