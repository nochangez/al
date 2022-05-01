# coding=utf-8


from data.services.database_controller import DatabaseController


class GoodsController:
    def __init__(self):
        self.__database_controller = DatabaseController()

    async def get_goods(self):
        get_goods_query = f"SELECT * FROM goods"
        goods = await self.__database_controller.get_data_execute_query(get_goods_query)

        return goods

    async def get_good_by_id(self, good_id: int):
        get_good_query = f"SELECT * FROM goods WHERE id='{good_id}'"
        good = await self.__database_controller.get_data_execute_query(get_good_query)

        return good[0]

    async def does_good_exist_id(self, good_id):
        get_good_query = f"SELECT * FROM goods WHERE id='{good_id}'"
        found_goods = await self.__database_controller.get_data_execute_query(get_good_query)

        return True if len(found_goods) != 0 else False

    async def does_good_exist_name(self, good_name: str):
        get_good_query = f"SELECT * FROM goods WHERE good_name='{good_name}'"
        found_goods = await self.__database_controller.get_data_execute_query(get_good_query)

        return True if len(found_goods) != 0 else False

    async def get_good_by_name(self, good_name: str):
        get_good_query = f"SELECT * FROM goods WHERE good_name='{good_name}'"
        good = await self.__database_controller.get_data_execute_query(get_good_query)

        return good[0]

    async def add_good(self, good_name: str, price: float):
        add_good_query = "INSERT INTO goods (good_name, price) VALUES " \
                         f"('{good_name}', '{price}')"
        await self.__database_controller.execute_query(add_good_query)

    async def del_good(self, good_id: int):
        del_good_query = f"DELETE FROM goods WHERE id='{good_id}'"
        await self.__database_controller.execute_query(del_good_query)

    async def change_good_name(self, good_id: int, good_name: str):
        change_good_query = f"UPDATE goods SET good_name='{good_name}' WHERE id='{good_id}'"
        await self.__database_controller.execute_query(change_good_query)

    async def change_good_price(self, good_id: int, good_price: float):
        change_good_query = f"UPDATE goods SET price='{good_price}' WHERE id='{good_id}'"
        await self.__database_controller.execute_query(change_good_query)
