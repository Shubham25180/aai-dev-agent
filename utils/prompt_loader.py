import json
import os

PROMPT_BLOCKS_PATH = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'prompt_blocks.json')

class PromptLoader:
    def __init__(self, prompt_blocks_path: str = PROMPT_BLOCKS_PATH):
        self.prompt_blocks_path = prompt_blocks_path
        self._load_blocks()

    def _load_blocks(self):
        with open(self.prompt_blocks_path, 'r', encoding='utf-8') as f:
            self.blocks = json.load(f)

    def get_block(self, block_name: str) -> str:
        return self.blocks.get(block_name, "")

    def update_block(self, block_name: str, new_value: str):
        self.blocks[block_name] = new_value
        with open(self.prompt_blocks_path, 'w', encoding='utf-8') as f:
            json.dump(self.blocks, f, indent=2)

    def assemble_prompt(self, user_input: str, session_context: str = "", speaker_profile: str = "", behavior_override: str = "") -> str:
        prompt = (
            self.get_block("base_memory") + "\n\n" +
            (session_context or self.get_block("session")) + "\n\n" +
            (speaker_profile or self.get_block("speaker_profile")) + "\n\n" +
            (behavior_override or self.get_block("behavior_override")) + "\n\n" +
            self.get_block("action_safety_policy") + "\n\n" +
            self.get_block("reflective_reasoning") + "\n\n" +
            "User input: " + user_input
        )
        return prompt

def build_nexus_prompt(
    system_prompt,
    recent_transcript=None,
    visual_context=None,
    emotion=None,
    speaker=None,
    session_context=None,
    memory_blocks=None,
    control_tags=None,
    max_utterances=2,
    max_memory_blocks=2,
    max_block_length=300
):
    """
    Assemble the full prompt for nexus's LLM, fusing multimodal and memory context.
    Limits context for speed and relevance.
    Args:
        system_prompt (str): The base/god-tier system prompt.
        recent_transcript (str, optional): Recent user/nexus utterances.
        visual_context (str, optional): Visual context summary from vision agent.
        emotion (str, optional): User's current emotional tone.
        speaker (str, optional): Speaker ID or profile.
        session_context (str, optional): Goals, session state, etc.
        memory_blocks (list[str], optional): Long-term memory/context blocks.
        control_tags (str, optional): Style, verbosity, or behavior overrides.
        max_utterances (int): Max recent utterances to include
        max_memory_blocks (int): Max memory/context blocks
        max_block_length (int): Max chars per block
    Returns:
        str: Assembled prompt for LLM call.
    """
    prompt_parts = [system_prompt.strip()]
    # Limit and truncate recent utterances
    if recent_transcript:
        if isinstance(recent_transcript, list):
            utterances = recent_transcript[-max_utterances:]
            utterances = [u[:max_block_length] for u in utterances]
            prompt_parts.append("[LastUtterances]: " + "\n".join(utterances))
        else:
            prompt_parts.append(f"[LastUtterance]: {str(recent_transcript)[:max_block_length]}")
    if visual_context:
        prompt_parts.append(f"[VisualContext]: {visual_context.strip()[:max_block_length]}")
    if emotion:
        prompt_parts.append(f"[UserEmotion]: {emotion.strip()[:max_block_length]}")
    if speaker:
        prompt_parts.append(f"[Speaker]: {speaker.strip()[:max_block_length]}")
    if session_context:
        prompt_parts.append(f"[SessionGoals]: {session_context.strip()[:max_block_length]}")
    if memory_blocks:
        for block in memory_blocks[-max_memory_blocks:]:
            prompt_parts.append(f"[Memory]: {block.strip()[:max_block_length]}")
    if control_tags:
        prompt_parts.append(f"[Control]: {control_tags.strip()[:max_block_length]}")
    return "\n".join(prompt_parts)

# Example usage:
# loader = PromptLoader()
# prompt = loader.assemble_prompt("What's the weather?", session_context="...", speaker_profile="...", behavior_override="...")
# prompt = build_nexus_prompt(system_prompt, recent_transcript, visual_context, emotion, speaker, session_context, memory_blocks, control_tags) 