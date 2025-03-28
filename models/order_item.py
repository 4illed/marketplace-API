class OrderItem:
    def __init__(
        self, id: int, order_id: int, product_id: int, quantity: int, price: float
    ):
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def __repr__(self) -> str:
        return (
            f"OrderItem(id={self.id}, order_id={self.order_id}, "
            f"product_id={self.product_id}, quantity={self.quantity}, price={self.price})"
        )
