from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

# --- Inject Material Icons, Sora Headings, Inter Body, and Enhanced Dark Theme ---
ui.add_head_html('''
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;700&family=Inter:wght@400;600;700&family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
<style>
  /* Force Material Icons font for all .material-icons elements */
  .material-icons {
    font-family: 'Material Icons' !important;
    font-style: normal;
    font-weight: normal;
    font-size: 28px;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    direction: ltr;
    -webkit-font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
  }
  html, body {
    background: #131313 !important;
    color: #f3f3f3 !important;
    font-family: 'Inter', 'Space Grotesk', Arial, sans-serif !important;
  }
  * {
    font-family: 'Inter', 'Space Grotesk', Arial, sans-serif !important;
  }
  h1, h2, h3, h4, h5, h6,
  .q-label, .q-field__label, .q-item__label, label,
  .text-primary, .text-lg, .text-xl, .text-2xl, .text-3xl, .text-4xl {
    font-family: 'Sora', Arial, sans-serif !important;
    font-weight: 700;
    letter-spacing: 0.01em;
  }
  .q-page, .q-layout, .q-page-container, .q-header, .q-footer, .q-drawer {
    background: #131313 !important;
    color: #f3f3f3 !important;
  }
  .bg-dark, .bg-grey-8, .bg-primary, .bg-transparent, .q-card, .q-dialog__inner, .q-menu {
    background: rgba(35, 39, 47, 0.85) !important;
    color: #f3f3f3 !important;
    border-radius: 14px !important;
    border: 1px solid #23272f !important;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 32px 0 rgba(0,0,0,0.12);
  }
  .q-btn, .q-btn--standard, .q-btn--unelevated, .q-btn--flat, .q-btn--outline {
    background: #23272f !important;
    color: #10a37f !important;
    border: 1px solid #10a37f !important;
    box-shadow: 0 2px 8px 0 rgba(16,163,127,0.08);
    border-radius: 8px !important;
    font-weight: 700;
    transition: background 0.2s, color 0.2s;
  }
  .q-btn:hover, .q-btn:focus {
    background: #10a37f !important;
    color: #fff !important;
  }
  .q-checkbox__bg, .q-checkbox__inner {
    background: #23272f !important;
    border: 2px solid #10a37f !important;
  }
  .q-checkbox__label, .q-checkbox__svg {
    color: #f3f3f3 !important;
    font-size: 1.1em;
    font-family: 'Sora', Arial, sans-serif !important;
  }
  .q-slider__track-container, .q-slider__track {
    background: #343541 !important;
    height: 6px !important;
    border-radius: 4px;
  }
  .q-slider__thumb {
    background: #3b82f6 !important;
    border: none !important;
    border-radius: 50% !important;
    width: 14px !important;
    height: 14px !important;
    box-shadow: none !important;
    transition: background 0.2s;
  }
  .q-slider__thumb:hover, .q-slider__thumb:focus {
    background: #60a5fa !important;
    /* Remove all transform/scale effects */
    transform: none !important;
    scale: none !important;
  }
  .q-slider__track {
    background: #23272f !important;
    height: 6px !important;
    border-radius: 4px;
  }
  .q-input, .q-field, .q-field__control, .q-field__native, .q-field__label, .q-select, .q-select__control {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }
  .q-input input, .q-field__native input, .q-field__native textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }
  .q-field--focused, .q-input--focused, .q-select--focused {
    border-color: #10a37f !important;
    box-shadow: 0 0 0 1.5px #10a37f !important;
  }
  .q-field__label, .q-label, .q-item__label, .q-item__section, .q-item__section--main, label, .q-select__label {
    color: #10a37f !important;
    font-weight: 700;
    font-size: 1.1em;
    letter-spacing: 0.02em;
    font-family: 'Sora', Arial, sans-serif !important;
  }
  .q-select__dropdown-icon, .q-select__control {
    color: #10a37f !important;
  }
  .q-dialog, .q-dialog__inner {
    background: rgba(35, 39, 47, 0.95) !important;
    color: #f3f3f3 !important;
    border-radius: 14px !important;
    border: 1px solid #10a37f !important;
    backdrop-filter: blur(8px);
  }
  .q-scrollarea__content, .q-scrollarea {
    background: #131313 !important;
  }
  .q-notification {
    background: #23272f !important;
    color: #10a37f !important;
    border: 1px solid #10a37f !important;
    font-weight: 700;
    font-family: 'Sora', Arial, sans-serif !important;
  }
  .q-dialog__backdrop {
    background: rgba(24,24,24,0.85) !important;
  }
  /* Chat bubbles */
  .bg-primary.text-white {
    background: #343541 !important;
    color: #fff !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px 0 rgba(16,163,127,0.10);
    font-family: 'Inter', 'Space Grotesk', Arial, sans-serif !important;
  }
  .bg-grey-8.text-white {
    background: #23272f !important;
    color: #f3f3f3 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px 0 rgba(16,163,127,0.05);
    font-family: 'Inter', 'Space Grotesk', Arial, sans-serif !important;
  }
  /* Scrollbar styling */
  ::-webkit-scrollbar {
    width: 8px;
    background: #23272f;
  }
  ::-webkit-scrollbar-thumb {
    background: #10a37f;
    border-radius: 8px;
  }
  .icon-btn {
    background: #23272f;
    border: 1.5px solid #10a37f;
    color: #10a37f;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
    font-size: 28px;
    margin-left: 8px;
  }
  .icon-btn:hover {
    background: #10a37f;
    color: #fff;
  }
  .fab-icon-btn {
    position: fixed;
    bottom: 32px;
    right: 32px;
    background: #23272f;
    border: 2px solid #10a37f;
    color: #10a37f;
    border-radius: 50%;
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px 0 rgba(16,163,127,0.15);
    font-size: 36px;
    cursor: pointer;
    z-index: 1000;
    transition: background 0.2s, color 0.2s;
  }
  .fab-icon-btn:hover {
    background: #10a37f;
    color: #fff;
  }
  .input-with-icon {
    position: relative;
    width: 100%;
  }
  .input-with-icon input {
    padding-right: 48px !important;
  }
  .send-inside-input {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none !important;
    border: none !important;
    color: #10a37f !important;
    border-radius: 0 !important;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 28px;
    transition: color 0.2s;
    z-index: 2;
    box-shadow: none !important;
  }
  .send-inside-input:hover {
    color: #fff !important;
    background: none !important;
  }
  .q-toggle {
    margin-bottom: 12px;
  }
  /* iOS-style toggle switch (exact match) */
  .q-toggle__track, .q-switch__track {
    background: #d1d5db !important; /* light gray for OFF */
    border-radius: 999px !important;
    border: none !important;
    opacity: 1 !important;
    height: 32px !important;
    min-width: 56px !important;
    box-shadow: none !important;
    transition: background 0.2s;
    position: relative;
  }
  .q-toggle--checked .q-toggle__track, .q-switch--true .q-switch__track {
    background: #3b82f6 !important; /* blue for ON */
    border: none !important;
  }
  /* Force thumb to always be white, all states */
  .q-toggle__thumb, .q-switch__thumb,
  .q-toggle--checked .q-toggle__thumb, .q-switch--true .q-switch__thumb {
    background: #fff !important;
    background-color: #fff !important;
    box-shadow: 0 2px 8px 0 rgba(0,0,0,0.18) !important;
    border: none !important;
  }
  .q-toggle, .q-switch {
    margin-bottom: 12px;
    position: relative;
    min-width: 56px;
    min-height: 32px;
  }
  .q-toggle__inner, .q-switch__inner, .q-toggle__focus-helper, .q-switch__focus-helper {
    outline: none !important;
    box-shadow: none !important;
  }
  /* --- Remove box/border from dropdown selected value --- */
  .q-select__control, .q-select, .q-field, .q-field__control {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }
  .q-field__native, .q-field__label, .q-select__dropdown-icon {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }
  /* Remove border/box from input placeholder (Ask anything) */
  .q-input, .q-input input, .q-field__native input, .q-field__native textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }
  .ios-toggle {
    display: inline-block;
    width: 56px;
    height: 32px;
    background: #d1d5db;
    border-radius: 999px;
    position: relative;
    transition: background 0.2s;
    vertical-align: middle;
  }
  input[type="checkbox"]:checked + label .ios-toggle {
    background: #3b82f6;
  }
  .ios-toggle:before {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 28px;
    height: 28px;
    background: #fff;
    border-radius: 50%;
    box-shadow: 0 2px 8px 0 rgba(0,0,0,0.18);
    transition: left 0.2s cubic-bezier(.4,0,.2,1);
  }
  input[type="checkbox"]:checked + label .ios-toggle:before {
    left: 26px;
  }
</style>
''')

# --- Theme ---
ui.dark_mode()

class NexusUI:
    def __init__(self):
        self.voice_enabled = True
        self.chat_messages = []
        self.chat_area = None
        self.input_box = None
        self.voice_button = None
        self.setup_ui()
        # Inject JS for mic button after UI is loaded
        def inject_js():
            ui.run_javascript('window.addEventListener("mic_click", () => { fetch("/mic_toggle"); });')
        ui.timer(0.5, inject_js, once=True)

    def on_refresh(self):
        ui.notify('Refreshed!')
    def on_clear_chat(self):
        self.chat_messages = []
        if self.chat_area:
            self.chat_area.clear()
        ui.notify('Chat cleared!')
    def on_system_info(self):
        ui.notify('System info: All systems nominal.')
    def on_show_last_prompt(self):
        ui.notify('Last prompt: "What is the meaning of life?"')
    def on_debug(self):
        ui.notify('Debug/Transparency panel coming soon!')
    def on_view_memory(self):
        with ui.dialog() as dialog, ui.card():
            ui.label('Memory Viewer (stub)').classes('text-lg')
            ui.button('Close', on_click=dialog.close)
    def on_send(self):
        if not self.input_box:
            return
        text = self.input_box.value.strip()
        if text:
            self.add_message(text, sent=True)
            self.input_box.value = ''
            self.input_box.update()
    def on_voice_toggle(self):
        self.voice_enabled = not self.voice_enabled
        icon = 'mic' if self.voice_enabled else 'mic_off'
        color = 'primary' if self.voice_enabled else 'grey'
        if self.voice_button:
            self.voice_button.props(f'icon={icon} color={color}')
        ui.notify(f'Voice {"enabled" if self.voice_enabled else "disabled"}!')
    def on_toggle_change(self, e: ValueChangeEventArguments):
        ui.notify(f'{e.sender._props["label"]}: {"On" if e.value else "Off"}')
    def on_slider_change(self, e: ValueChangeEventArguments):
        ui.notify(f'{e.sender._props["label"]} set to {e.value}')
    def add_message(self, text, sent=True):
        self.chat_messages.append((text, sent))
        if self.chat_area:
            self.chat_area.clear()
            with self.chat_area:
                for msg, is_sent in self.chat_messages:
                    align = 'justify-end' if is_sent else 'justify-start'
                    bubble_color = 'bg-primary text-white' if is_sent else 'bg-grey-8 text-white'
                    with ui.row().classes(f'w-full {align}'):
                        ui.html(f'<div class="mb-2 p-2 rounded-lg max-w-[70%] {bubble_color}" style="word-break: break-word; white-space: pre-line;">{msg}</div>')
    def setup_ui(self):
        with ui.row().classes('w-full h-screen no-wrap'):
            # Left Column
            with ui.column().classes('w-1/3 min-w-[340px] max-w-[400px] p-4 gap-2'):
                ui.button('View Memory', on_click=self.on_view_memory).props('color=primary')
                with ui.card().classes('mt-4 bg-transparent border border-primary'):
                    ui.label('Persona Response Tuning').classes('text-primary')
                    prompt_mode = ui.select(['Smart (Default)', 'Witty', 'Sarcastic', 'Verbose'], value='Smart (Default)', label='Prompt Mode').classes('w-full')
                    ui.label('Select Memories:').classes('text-primary')
                    ui.slider(min=0, max=10, value=0).props('label=Select Memories:')
                    ui.label('Wit/Sarcasm:').classes('text-primary')
                    wit_slider = ui.slider(min=0, max=20, value=10, on_change=self.on_slider_change).props('label=Wit/Sarcasm:')
                    ui.label('Verbosity:').classes('text-primary')
                    verb_slider = ui.slider(min=0, max=20, value=4, on_change=self.on_slider_change).props('label=Verbosity:')
                with ui.card().classes('mt-2 bg-transparent border border-primary'):
                    # Custom iOS-style toggles for settings
                    def custom_toggle(label, value, on_change, id_suffix):
                        checked = 'checked' if value else ''
                        toggle_id = f'toggle_{id_suffix}'
                        ui.html(f'''
                        <div style="display: flex; align-items: center; margin-bottom: 18px;">
                          <input type="checkbox" id="{toggle_id}" {checked} style="display:none;">
                          <label for="{toggle_id}" style="cursor:pointer;display:inline-block;">
                            <span class="ios-toggle"></span>
                          </label>
                          <span style="margin-left: 16px; font-size: 1.08em;">{label}</span>
                        </div>
                        ''')
                        # JS event to call Python handler
                        ui.run_javascript(f'''
                          document.getElementById('{toggle_id}').addEventListener('change', function(e) {{
                            fetch('/toggle_event/{id_suffix}/' + (e.target.checked ? '1' : '0'));
                          }});
                        ''')
                    # Add a custom handler for custom toggles
                    def on_custom_toggle(self, label, value):
                        ui.notify(f'{label}: {"On" if value else "Off"}')
                    # Capture self for endpoint closure
                    nexus_ui = self
                    @app.get('/toggle_event/{id_suffix}/{state}')
                    def toggle_event(id_suffix: str, state: str):
                        label_map = {
                            'voice': 'Enable Voice',
                            'tts': 'Enable TTS',
                            'auto': 'Auto-scroll Chat',
                            'intent': 'Intent Detection',
                            'emotion': 'Emotion Detection',
                        }
                        label = label_map.get(id_suffix, id_suffix)
                        value = (state == '1')
                        nexus_ui.on_custom_toggle(label, value)
                        return 'ok'
                    # Render toggles
                    custom_toggle('Enable Voice', True, self.on_toggle_change, 'voice')
                    custom_toggle('Enable TTS', True, self.on_toggle_change, 'tts')
                    custom_toggle('Auto-scroll Chat', True, self.on_toggle_change, 'auto')
                    custom_toggle('Intent Detection', False, self.on_toggle_change, 'intent')
                    custom_toggle('Emotion Detection', False, self.on_toggle_change, 'emotion')
                # Status and memory info as 2x2 grid of cards
                with ui.row().classes('w-full gap-4 mt-4'):
                    # 2x2 grid: left col (Memory, Agent), right col (Voice, LLM)
                    with ui.column().classes('w-1/2 gap-4'):
                        with ui.card().classes('status-card'):
                            ui.label('Memory').classes('text-primary')
                            ui.label('Short Term : 1 Entry')
                            ui.label('Long Term : N/A')
                            ui.label('Total size : 1 session , 2 core')
                        with ui.card().classes('status-card'):
                            ui.label('Agent Status : Processing')
                            ui.label('Response Time : 20s')
                            ui.label('Model: ollama')
                    with ui.column().classes('w-1/2 gap-4'):
                        with ui.card().classes('status-card'):
                            ui.label('Voice System Status : Active')
                            ui.label('TTS: edge-tts')
                            ui.label('STT: Wisper Ready')
                        with ui.card().classes('status-card'):
                            ui.label('LLM Status: Connected')
                            ui.label('Model: Unknown')
                            ui.label('Connection: Active')
            # Right Column
            with ui.column().classes('w-2/3 h-full p-4 gap-2'):
                with ui.row().classes('w-full justify-between'):
                    ui.button('Refresh', on_click=self.on_refresh).props('color=primary')
                    ui.button('Clear Chat', on_click=self.on_clear_chat).props('color=primary')
                    ui.button('System Info', on_click=self.on_system_info).props('color=primary')
                    ui.button('Show Last Prompt', on_click=self.on_show_last_prompt).props('color=primary')
                    ui.button('Debug/Transparency', on_click=self.on_debug).props('color=primary')
                self.chat_area = ui.column().classes('w-full h-[70vh] bg-dark rounded-lg mt-2 overflow-y-auto').style('overflow-y: auto;')
                # Input row: input and send icon button inside the same bar
                with ui.row().classes('w-full items-end mt-2'):
                    with ui.element('div').classes('input-with-icon w-full'):
                        self.input_box = ui.input('Ask anything').props('rounded outlined').classes('w-full')
                        self.input_box.on('keydown.enter', lambda e: self.on_send())
                        # Send icon button inside the input, right-aligned
                        ui.html('<button class="send-inside-input" onclick="document.querySelector(\'input[placeholder=Ask anything]\').dispatchEvent(new KeyboardEvent(\'keydown\', {key: \'Enter\'})); return false;"><span class="material-icons">send</span></button>')
        # Mic floating action button: icon only, styled as a circle, bottom right, custom HTML
        ui.html('<button class="fab-icon-btn" onclick="window.dispatchEvent(new CustomEvent(\'mic_click\'));"><span class="material-icons">mic</span></button>')

    def on_custom_toggle(self, label, value):
        ui.notify(f'{label}: {"On" if value else "Off"}')

NexusUI()
ui.run(title='NEXUS AI Dev Agent', reload=True) 