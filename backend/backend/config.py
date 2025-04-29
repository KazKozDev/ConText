TEXT_SIZE_THRESHOLD = 5000  # Characters threshold for optional future use
# Default chunking settings to stay well below typical model output limits.
CHUNK_SIZE = 2000  # ~500‑700 tokens — keeps translation output within context window
# Overlap to maintain context between chunks
CHUNK_OVERLAP = 100  # Characters of overlap between chunks 