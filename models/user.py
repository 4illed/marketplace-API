class User:
    def __init__(
        self, id: int, name: str, email: str, address: str = None, phone: str = None
    ):
        self.id = id
        self.name = name
        self.email = email
        self.address = address
        self.phone = phone

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, name='{self.name}', email='{self.email}', "
            f"address='{self.address}', phone='{self.phone}')"
        )
