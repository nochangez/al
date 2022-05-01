# coding=utf-8


from data.services.database_controller import DatabaseController


class PaymentsController:
    def __init__(self):
        self.__database_controller = DatabaseController()

    async def get_payments(self):
        get_pays_query = "SELECT * FROM payments"
        pays = await self.__database_controller.get_data_execute_query(get_pays_query)

        return pays

    async def get_payments_by_date(self, date: str):
        get_pays_by_date_query = f"SELECT * FROM payments WHERE payment_date LIKE '%{date}%'"
        pays = await self.__database_controller.get_data_execute_query(get_pays_by_date_query)

        return pays
