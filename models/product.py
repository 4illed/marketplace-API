class Product:
    def __init__(
        self, id: int, name: str, description: str, price: float, category: str
    ):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category

    def __repr__(self) -> str:
        return (
            f"Product(id={self.id}, name='{self.name}', description='{self.description}', "
            f"price={self.price}, category='{self.category}')"
        )
