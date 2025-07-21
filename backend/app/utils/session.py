import uuid

def resolve_session_id(request_session_id):
    return request_session_id or str(uuid.uuid4()) 