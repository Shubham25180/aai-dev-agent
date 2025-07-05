class ChromaMemory:
    def __init__(self):
        self._memories = []

    def store(self, text: str):
        """Store a memory string."""
        self._memories.append(text)

    def retrieve(self, query: str, n_results: int = 3):
        """Retrieve up to n_results memories that are most relevant to the query (simple substring match for now)."""
        # Simple relevance: contains query substring (case-insensitive)
        matches = [m for m in self._memories if query.lower() in m.lower()]
        # If not enough matches, just return the most recent memories
        if len(matches) < n_results:
            matches += [m for m in reversed(self._memories) if m not in matches]
        return matches[:n_results]

    def add(self, *args, **kwargs):
        pass

    def search(self, *args, **kwargs):
        return []

    def clear(self):
        pass 