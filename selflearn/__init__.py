"""
selflearn: fallback self-learning module for the benchmark recommender.

It sits outside the frozen retrieval system (retrieval_v2/, tag retrieval-v2.3-blend), which it only reads. It never
reads the independent test queries or their gold labels. When the frozen blend 0.5 ranking has low confidence, it
extracts the stated problem features, matches them to benchmark-family metadata, and keeps unverified suggestions in a
local store for human verification.
"""
