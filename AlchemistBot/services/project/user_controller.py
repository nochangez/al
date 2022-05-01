# coding=utf-8


from data.services.database_controller import DatabaseController


class UserController:
    def __init__(self):
        self.__database_controller = DatabaseController()

    async def add_user(self, user_id: int, city: str, purchases: int = 0, balance: float = 0.0):
        add_user_query = "insert into users (user_id, city, purchases, balance) values " \
                         f"('{user_id}', '{city}', '{purchases}', '{balance}')"
        await self.__database_controller.execute_query(add_user_query)

    async def change_city(self, user_id: int, new_city: str):
        change_city_query = f"UPDATE users SET city='{new_city}' WHERE user_id='{user_id}'"
        await self.__database_controller.execute_query(change_city_query)

    async def change_balance(self, user_id: int, new_balance: float):
        change_balance_query = f"UPDATE users SET balance='{new_balance}' WHERE user_id='{user_id}'"
        await self.__database_controller.execute_query(change_balance_query)

    async def change_purchases(self, user_id: int, new_purchases: int):
        change_purchases_query = f"UPDATE users SET purchases='{new_purchases}' WHERE user_id='{user_id}'"
        await self.__database_controller.execute_query(change_purchases_query)

    async def add_purchase(self, user_id: int):
        add_purchase_query = f"UPDATE users SET purchases = purchases + 1 WHERE user_id='{user_id}'"
        await self.__database_controller.execute_query(add_purchase_query)

    async def get_user_info(self, user_id: int):
        get_user_info_query = f"SELECT * FROM users WHERE user_id='{user_id}'"
        user_info = await self.__database_controller.get_data_execute_query(get_user_info_query)

        return user_info[0] if len(user_info) != 0 else user_info

    async def get_users(self):
        get_users_query = "SELECT * FROM users"
        users = await self.__database_controller.get_data_execute_query(get_users_query)

        return users

    async def is_user(self, user_id: int):
        get_user_query = f"SELECT * FROM users WHERE user_id='{user_id}'"
        results = await self.__database_controller.get_data_execute_query(get_user_query)

        return True if len(results) != 0 else False

    async def delete_user(self, user_id: str):
        delete_user_query = f"DELETE FROM users WHERE user_id='{user_id}'"
        await self.__database_controller.execute_query(delete_user_query)
