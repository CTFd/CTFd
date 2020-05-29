from dataclasses import dataclass

@dataclass
class Session:
    id: int = None
    nonce: str = None
    hash: str = None