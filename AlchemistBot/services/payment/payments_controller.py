# coding=utf-8


from data.services.database_controller import DatabaseController


class PaymentsController:
    def __init__(self):
        self.__database_controller = DatabaseController()

    async def get_payments(self):
        get_payments_query = "SELECT * FROM payments"
        payments = await self.__database_controller.get_data_execute_query(get_payments_query)

        return payments

    async def add_payment(self, customer_id: int, payment_value: float):
        add_payment_query = "INSERT INTO payments (customer_id, payment_value) VALUES " \
                            f"('{customer_id}', '{payment_value}')"
        await self.__database_controller.execute_query(add_payment_query)
