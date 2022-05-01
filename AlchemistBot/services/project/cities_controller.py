# coding=utf-8


from data.services.database_controller import DatabaseController


class CitiesController:
    def __init__(self):
        self.__database_controller = DatabaseController()

    async def get_cities(self):
        get_cities_query = "SELECT * FROM cities"
        cities = await self.__database_controller.get_data_execute_query(get_cities_query)

        return cities

    async def does_city_exist(self, city_id: int):
        get_city_query = f"SELECT * FROM cities WHERE id='{city_id}'"
        city = await self.__database_controller.get_data_execute_query(get_city_query)

        return True if len(city) != 0 else False

    async def add_city(self, city_name: str):
        add_city_query = f"INSERT INTO cities (city) VALUES ('{city_name}')"
        await self.__database_controller.execute_query(add_city_query)

    async def del_city(self, city_id: int):
        del_city_query = f"DELETE FROM cities WHERE id='{city_id}'"
        await self.__database_controller.execute_query(del_city_query)
