import jsonpatch
from typing import Dict, Any


def calculate_note_delta(old_content: str, new_content: str) -> Dict[str, Any]:
    """
    Calculates the JSON Patch (RFC 6902) between two forensic note states.
    Utilizes high-speed string registers for investigative version control.
    """
    # Wrap in dict for jsonpatch structural compatibility
    old_obj = {"c": old_content}
    new_obj = {"c": new_content}

    # Generate Atomic Delta
    patch = jsonpatch.make_patch(old_obj, new_obj)

    # Return the first delta object in the patch sequence
    if not patch.patch:
        return {}

    return patch.patch[0]


def apply_note_delta(content: str, delta: Dict[str, Any]) -> str:
    """
    Reconstructs historical note content using the delta patch.
    """
    obj = {"c": content}
    # Convert single delta back to patch sequence
    patch = jsonpatch.JsonPatch([delta])
    res = patch.apply(obj)
    return res["c"]
