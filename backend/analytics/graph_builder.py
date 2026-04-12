from dal.models.graph import ContiguousGraphModel
from dal.schemas.package import BinarySchemaValidator
class GraphBuilder: pass
class BinaryGraphBuilder:
    def __init__(self):
        self.schema = BinarySchemaValidator()
        self.model = ContiguousGraphModel()
    def ingest_and_build(self, node_id: bytes, type_code: int, weight: float):
        node_payload = self.schema.pack_node(node_id, type_code, weight)
        if self.schema.validate(node_payload):
            self.model.append_node(node_payload)
            return True
        return False
