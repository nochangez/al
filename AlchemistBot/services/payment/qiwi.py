# coding=utf-8


from pyqiwip2p import AioQiwiP2P

from data.config import tokens


class Payments:
    def __init__(self):
        self.__token = tokens['qiwi_token']
        self.__qiwi = AioQiwiP2P(auth_key=self.__token)

    async def get_payment_status(self, bill_id: str):
        status = await self.__qiwi.check(bill_id)
        return True if status.status == "PAID" else False

    async def create_payment(self, amount: float):
        bill = await self.__qiwi.bill(amount=amount, lifetime=5)
        bill_id = bill.bill_id
        pay_url = bill.pay_url

        return {
            'bill_id': bill_id,
            'pay_url': pay_url,
        }
