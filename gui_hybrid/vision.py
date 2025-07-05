import pytesseract
from PIL import ImageGrab
from ultralytics import YOLO
import numpy as np

class Vision:
    """
    Vision module for GUI automation: OCR and YOLOv8 object detection.
    """
    def __init__(self):
        # Load YOLOv8 model (downloads weights if not present)
        self.yolo = YOLO('yolov8n.pt')  # Use nano for speed; can upgrade to yolov8s.pt, etc.
        
        # Check if Tesseract is available
        self.tesseract_available = self._check_tesseract()

    def _check_tesseract(self):
        """Check if Tesseract OCR is available."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except (pytesseract.TesseractNotFoundError, Exception):
            print("[Vision] Tesseract OCR not found. OCR functionality will be limited.")
            return False

    def capture_screen(self):
        """Capture the current screen as a PIL Image."""
        return ImageGrab.grab()

    def ocr_text(self, image):
        """Extract text from a PIL Image using Tesseract OCR or fallback."""
        if self.tesseract_available:
            try:
                return pytesseract.image_to_string(image)
            except Exception as e:
                print(f"[Vision] OCR failed: {e}")
                return self._fallback_ocr(image)
        else:
            return self._fallback_ocr(image)
    
    def _fallback_ocr(self, image):
        """
        Simple fallback OCR that returns basic screen info.
        In a real implementation, you could use other OCR libraries.
        """
        # Return basic screen information
        width, height = image.size
        return f"Screen size: {width}x{height} pixels"

    def detect_buttons_yolo(self, image):
        """
        Use YOLOv8 to detect buttons/objects in the screenshot.
        Returns: list of dicts with label, confidence, and coordinates.
        """
        # Convert PIL Image to numpy array (RGB)
        img_np = np.array(image.convert('RGB'))
        results = self.yolo(img_np)
        detections = []
        for r in results:
            for box in r.boxes:
                label = r.names[int(box.cls)]
                conf = float(box.conf)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({'label': label, 'confidence': conf, 'coords': (x1, y1, x2, y2)})
        return detections

    def detect_buttons(self, image):
        """
        Try YOLOv8 for button detection; fallback to OCR if needed.
        Returns: list of dicts with label and coordinates.
        """
        detections = self.detect_buttons_yolo(image)
        if detections:
            return detections
        # Fallback: use OCR to find text regions (very basic)
        text = self.ocr_text(image)
        return [{'label': t.strip(), 'coords': None} for t in text.split('\n') if t.strip()] 