import uuid
from typing import List, Union, Mapping

from cuddlez.database.modals.base import Base


class Item(Base):
    def __init__(
            self,
            *,
            item_id: str,
            amount: int = 0
    ):
        self.item_id = item_id
        self.amount = amount

    def to_dict(self) -> dict:
        return {'itemId': self.item_id, 'amount': self.amount}

    @classmethod
    def from_dict(cls, data: Union[dict, Mapping[str, any]]):
        return Item(item_id=data['itemId'], amount=data['amount'])


class CuddlezUser(Base):
    def __init__(
            self,
            *,
            user_id: Union[int, str],
            wallet: int = 0,
            bank: int = 0,
            inventory: List[Item] = None,
            rizzing: Union[str, uuid.UUID] = None,
    ):
        self.user_id = str(user_id)
        self.wallet = wallet
        self.bank = bank
        self.inventory = inventory or []
        self.rizzing = str(rizzing)

    def to_dict(self) -> dict:
        return {
            '_id': self.user_id,
            'wallet': self.wallet,
            'bank': self.bank,
            'inventory': list(map(lambda v: v.to_dict(), self.inventory)),
            'rizzing': self.rizzing
        }

    @classmethod
    def from_dict(cls, data: Union[dict, Mapping[str, any]]):
        user_id = data['_id']
        wallet, bank = data['wallet'], data['bank']
        inventory = [Item.from_dict(item) for item in data['inventory']]
        rizzing = data['rizzing']
        return CuddlezUser(user_id=user_id, wallet=wallet, bank=bank, inventory=inventory, rizzing=rizzing)
