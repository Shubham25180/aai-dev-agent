class LLMPlanner:
    """
    Plans GUI actions using LLM based on user intent and screen context.
    """
    def __init__(self, llm=None):
        self.llm = llm

    def plan_action(self, user_intent, screen_context):
        """
        Generate action plan using LLM or fallback logic.
        
        Args:
            user_intent (str): What the user wants to do
            screen_context (dict): OCR text and detected buttons
            
        Returns:
            dict: Action plan with 'action' and relevant parameters
        """
        if self.llm:
            # Use connected LLM for planning
            prompt = f"""
            User wants to: {user_intent}
            Screen context: {screen_context}
            
            Plan a GUI action. Return JSON with:
            - action: "click" or "type"
            - coords: [x, y] for clicks
            - text: text to type
            - confidence: 0-1
            """
            try:
                response = self.llm.generate(prompt)
                # Simple parsing - in production, use proper JSON parsing
                if "click" in response.lower() and "coords" in response:
                    # Extract coordinates (simplified)
                    import re
                    coords_match = re.search(r'\[(\d+),\s*(\d+)\]', response)
                    if coords_match:
                        x, y = int(coords_match.group(1)), int(coords_match.group(2))
                        return {'action': 'click', 'coords': [x, y], 'confidence': 0.8}
                elif "type" in response.lower():
                    # Extract text to type (simplified)
                    import re
                    text_match = re.search(r'"([^"]+)"', response)
                    if text_match:
                        return {'action': 'type', 'text': text_match.group(1), 'confidence': 0.7}
            except Exception as e:
                print(f"[Planner] LLM planning failed: {e}")
        
        # Fallback: simple heuristic planning
        return self._fallback_plan(user_intent, screen_context)
    
    def _fallback_plan(self, user_intent, screen_context):
        """
        Simple fallback planning without LLM.
        """
        buttons = screen_context.get('buttons', [])
        ocr_text = screen_context.get('ocr_text', '')
        
        # Try to find matching button
        for button in buttons:
            if any(word.lower() in button.get('text', '').lower() 
                   for word in user_intent.lower().split()):
                return {
                    'action': 'click',
                    'coords': button.get('coords', [100, 100]),
                    'confidence': 0.6
                }
        
        # Default fallback
        return {
            'action': 'click',
            'coords': [100, 100],
            'confidence': 0.3
        } 