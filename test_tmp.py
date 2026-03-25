from pydantic import BaseModel
from typing import List, Dict, Any

class IdentityMatch(BaseModel):
    source_persona: str
    target_persona: str

weights = {"crypto": 0.5, "lexical": 0.1}

def test(persona_data):
    matches = []
    crypto_v = 1.0 if persona_data.get('gpg_key') == '0xdeadbeef' else 0.0
    lexical_v = persona_data.get('lex_sim', 0.0)
    c_attr = (weights['crypto'] * crypto_v) + (weights['lexical'] * lexical_v)
    print(f"c_attr: {c_attr}")
    if c_attr > 0.4:
        matches.append(IdentityMatch(source_persona=persona_data['name'], target_persona="linked"))
    print(f"Leads: {len(matches)}")

test({"name": "shadow", "gpg_key": "0xdeadbeef", "lex_sim": 0.8})
