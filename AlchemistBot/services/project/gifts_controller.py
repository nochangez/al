# coding=utf-8


from data.services.database_controller import DatabaseController


class GiftsController:
    def __init__(self):
        self.__database_controller = DatabaseController()

    async def get_gift_info(self):
        get_gift_query = f"SELECT * FROM gifts"
        gift = await self.__database_controller.get_data_execute_query(get_gift_query)

        return gift

    async def update_gift(self, gift: str, coordinates: str):
        if len(await self.get_gift_info()) != 0:
            update_gift_query = f"UPDATE gifts SET gift='{gift}'"
            update_coordinates_query = f"UPDATE gifts SET coordinates='{coordinates}'"

            await self.__database_controller.execute_query(update_gift_query)
            await self.__database_controller.execute_query(update_coordinates_query)
        else:
            create_gift_query = f"INSERT INTO gifts (gift, coordinates) VALUES ('{gift}', '{coordinates}')"
            await self.__database_controller.execute_query(create_gift_query)

    async def delete_gift(self):
        delete_gift_query = f"DELETE FROM gifts"
        await self.__database_controller.execute_query(delete_gift_query)
