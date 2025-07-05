from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

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
                        ui.html(f'<div class="mb-2 p-2 rounded-lg max-w-[70%] {bubble_color}" style="word-break: break-word;">{msg}</div>')
    def setup_ui(self):
        with ui.row().classes('w-full h-screen no-wrap'):
            # Left Column
            with ui.column().classes('w-1/3 min-w-[340px] max-w-[400px] p-4 gap-2'):
                ui.button('View Memory', on_click=self.on_view_memory).props('color=primary')
                with ui.card().classes('mt-4 bg-transparent border border-primary'):
                    ui.label('Persona Response Tuning').classes('text-primary')
                    prompt_mode = ui.select(['Smart (Default)', 'Witty', 'Sarcastic', 'Verbose'], value='Smart (Default)', label='Prompt ...')
                    wit_slider = ui.slider(min=0, max=1, value=0.5, on_change=self.on_slider_change).props('label=Wit/Sarcasm:')
                    verb_slider = ui.slider(min=0, max=1, value=0.2, on_change=self.on_slider_change).props('label=Verbosity:')
                with ui.card().classes('mt-2 bg-transparent border border-primary'):
                    voice_toggle = ui.checkbox('Enable Voice', value=True, on_change=self.on_toggle_change)
                    tts_toggle = ui.checkbox('Enable TTS', value=True, on_change=self.on_toggle_change)
                    auto_scroll_toggle = ui.checkbox('Auto-scroll Chat', value=True, on_change=self.on_toggle_change)
                    intent_toggle = ui.checkbox('Intent Detection', value=False, on_change=self.on_toggle_change)
                    emotion_toggle = ui.checkbox('Emotion Detection', value=False, on_change=self.on_toggle_change)
            # Right Column
            with ui.column().classes('w-2/3 h-full p-4 gap-2'):
                with ui.row().classes('w-full justify-between'):
                    ui.button('Refresh', on_click=self.on_refresh).props('color=primary')
                    ui.button('Clear Chat', on_click=self.on_clear_chat).props('color=primary')
                    ui.button('System Info', on_click=self.on_system_info).props('color=primary')
                    ui.button('Show Last Prompt', on_click=self.on_show_last_prompt).props('color=primary')
                    ui.button('Debug/Transparency', on_click=self.on_debug).props('color=primary')
                self.chat_area = ui.column().classes('w-full h-[70vh] bg-dark rounded-lg mt-2 overflow-y-auto').style('overflow-y: auto;')
                with ui.row().classes('w-full items-end mt-2'):
                    self.input_box = ui.input('Ask anything').props('rounded outlined').classes('w-full')
                    self.input_box.on('keydown.enter', lambda e: self.on_send())
                    send_btn = ui.button(icon='send', on_click=self.on_send).props('color=primary')
        self.voice_button = ui.button(icon='mic', on_click=self.on_voice_toggle).props('fab color=primary size=xl').classes('fixed bottom-8 right-8 shadow-lg z-50')

NexusUI()
ui.run(title='NEXUS AI Dev Agent', reload=True) 