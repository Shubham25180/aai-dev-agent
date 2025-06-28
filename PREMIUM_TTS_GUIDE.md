# 🎤 Premium TTS Voices - Free Options Guide

## Overview

Get high-quality, natural-sounding TTS voices for NOVA without spending money! Here are the best free options:

## 🥇 **ElevenLabs (Recommended)**

**Free Tier:** 10,000 characters per month
**Quality:** ⭐⭐⭐⭐⭐ (Excellent)
**Setup Time:** 5 minutes

### Setup Steps:

1. **Sign up:** Go to [elevenlabs.io](https://elevenlabs.io) and create a free account
2. **Get API Key:** Go to Profile → API Key → Copy your key
3. **Install dependency:** `pip install requests`
4. **Set environment variable:**

   ```bash
   # Windows
   set ELEVENLABS_API_KEY=your_api_key_here

   # Or add to your .env file
   ELEVENLABS_API_KEY=your_api_key_here
   ```

### Popular Voices:

- **Rachel** (Professional female) - Perfect for NOVA
- **Domi** (Confident female) - Great for sarcastic responses
- **Antoni** (Professional male) - Deep, authoritative
- **Thomas** (Deep male) - Serious and professional

---

## 🥈 **Microsoft Azure Cognitive Services**

**Free Tier:** 500,000 characters per month
**Quality:** ⭐⭐⭐⭐⭐ (Excellent)
**Setup Time:** 10 minutes

### Setup Steps:

1. **Azure Account:** Create free Azure account (requires credit card but won't charge)
2. **Create Speech Service:** Azure Portal → Speech Services → Create
3. **Get Keys:** Copy Key 1 and Region
4. **Install:** `pip install azure-cognitiveservices-speech`

### Code Example:

```python
import azure.cognitiveservices.speech as speechsdk

def speak_with_azure(text):
    speech_config = speechsdk.SpeechConfig(
        subscription="your_key_here",
        region="your_region_here"
    )
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = speech_synthesizer.speak_text_async(text).get()
```

---

## 🥉 **Google Cloud Text-to-Speech**

**Free Tier:** 1 million characters per month
**Quality:** ⭐⭐⭐⭐ (Very Good)
**Setup Time:** 15 minutes

### Setup Steps:

1. **Google Cloud:** Create free account (requires credit card)
2. **Enable TTS API:** Google Cloud Console → APIs → Text-to-Speech
3. **Create Service Account:** IAM → Service Accounts → Create
4. **Download JSON Key:** Save as `google-tts-key.json`
5. **Install:** `pip install google-cloud-texttospeech`

### Code Example:

```python
from google.cloud import texttospeech

def speak_with_google(text):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-F"
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
```

---

## 🆓 **Completely Free Options**

### 1. **Coqui TTS (Local)**

- **Quality:** ⭐⭐⭐⭐
- **Setup:** `pip install TTS`
- **Pros:** Runs locally, no API limits
- **Cons:** Requires more setup

### 2. **gTTS (Google Translate TTS)**

- **Quality:** ⭐⭐⭐
- **Setup:** `pip install gTTS`
- **Pros:** Completely free, no API key needed
- **Cons:** Limited voice options

### 3. **pyttsx3 (Current)**

- **Quality:** ⭐⭐
- **Setup:** Already working
- **Pros:** No internet required
- **Cons:** Robotic sound

---

## 🚀 **Quick Integration for NOVA**

### Option 1: ElevenLabs (Easiest)

```python
# In your conversational_brain.py
from voice.premium_responder import PremiumResponder

# Initialize premium TTS
tts = PremiumResponder(voice_id="21m00Tcm4TlvDq8ikWAM")  # Rachel voice

# Use it for responses
tts.speak("Hello! I am NOVA, your sarcastic AI assistant.")
```

### Option 2: Azure (Best Quality)

```python
# Install: pip install azure-cognitiveservices-speech
import azure.cognitiveservices.speech as speechsdk

def speak_premium(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv('AZURE_SPEECH_KEY'),
        region=os.getenv('AZURE_SPEECH_REGION')
    )
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = speech_synthesizer.speak_text_async(text).get()
```

---

## 📊 **Comparison Table**

| Service    | Free Limit | Quality    | Setup Difficulty | Best For     |
| ---------- | ---------- | ---------- | ---------------- | ------------ |
| ElevenLabs | 10K chars  | ⭐⭐⭐⭐⭐ | Easy             | Quick setup  |
| Azure      | 500K chars | ⭐⭐⭐⭐⭐ | Medium           | Best quality |
| Google     | 1M chars   | ⭐⭐⭐⭐   | Medium           | High volume  |
| Coqui      | Unlimited  | ⭐⭐⭐⭐   | Hard             | Privacy      |
| gTTS       | Unlimited  | ⭐⭐⭐     | Easy             | Simple needs |

---

## 🎯 **Recommendation for NOVA**

**Start with ElevenLabs** because:

1. ✅ Easiest setup
2. ✅ Great voice quality
3. ✅ 10K characters is plenty for testing
4. ✅ Perfect for sarcastic AI personality
5. ✅ No credit card required

**Then upgrade to Azure** if you need:

- More characters per month
- Better voice variety
- Professional deployment

---

## 🔧 **Installation Commands**

```bash
# For ElevenLabs
pip install requests

# For Azure
pip install azure-cognitiveservices-speech

# For Google Cloud
pip install google-cloud-texttospeech

# For Coqui TTS
pip install TTS

# For gTTS
pip install gTTS
```

---

## 🎉 **Next Steps**

1. **Choose your preferred service** (ElevenLabs recommended)
2. **Follow the setup steps** above
3. **Test with a simple script** to verify it works
4. **Integrate with NOVA** by updating the TTS responder
5. **Enjoy premium-quality voice responses!**

Need help with any specific service? Just ask!
