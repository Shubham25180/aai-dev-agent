# nexus Model Optimization Guide

## 1. Quantized Models

- Use int8 or gguf-quantized models (e.g., `llama3:8b-q4_0` in Ollama) for 2-4x faster inference and lower memory usage.
- Quantized models have minimal quality loss but major speed gains, especially on CPU.
- Example (Ollama):
  ```bash
  ollama run llama3:8b-q4_0
  ```
- For local LLM libraries, use quantized weights (e.g., `llama.cpp`, `ctransformers`).

## 2. Mixture of Experts (MoE) [Future-Ready]

- MoE models only activate a subset of "experts" per query, saving compute.
- In nexus, architect the brain to route queries to specialist sub-models (e.g., jokes, memory, code) as needed.
- For now, use a single quantized model; plan for modular routing as nexus grows.

## 3. Streaming Responses

- Enable streaming in Ollama or `llama.cpp` for real-time, token-by-token output.
- In Python, use `stream=True` or iterate over the model's output generator:
  ```python
  for token in model.generate_stream(...):
      print(token, end="", flush=True)
  ```
- Improves perceived speed and user experience.

## 4. Prompt Engineering for Speed

- Use a modular prompt loader to only send relevant context and rules per call.
- Summarize session memory and use a sliding window for recent turns.
- Avoid sending the full base prompt every time unless needed.

## 5. Hardware Tips

- Use a GPU if available for large models.
- For CPU, prefer quantized models and keep context windows short.

## 6. Monitoring

- Profile STT and LLM response times (already implemented in nexus).
- Use logs to identify and optimize bottlenecks.

---

**Summary:**

- Use quantized models for speed.
- Stream responses for instant feedback.
- Modularize prompts and context.
- Plan for specialist sub-models as nexus evolves.
