from pydantic import BaseModel

class ComponentRequest(BaseModel):
    component_name: str
    amount: float
    component_type: str
    month: str
    pay_cycle_type: str