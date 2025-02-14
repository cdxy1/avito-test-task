from pydantic import BaseModel


class BuySchema(BaseModel):
    item: str


class SendSchema(BaseModel):
    user: str
    amount: int
