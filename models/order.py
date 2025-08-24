from datetime import datetime


class Order:
    def __init__(self, id: int, user_id: int, order_date: datetime, status: str):
        self.id = id
        self.user_id = user_id
        self.order_date = order_date
        self.status = status

    def __repr__(self) -> str:
        return (
            f"Order(id={self.id}, user_id={self.user_id}, "
            f"order_date='{self.order_date}', status='{self.status}')"
        )
