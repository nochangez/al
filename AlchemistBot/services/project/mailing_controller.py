# coding=utf-8


from data.services.database_controller import DatabaseController


class MailingController:
    def __init__(self):
        self.__database_controller = DatabaseController()

    async def get_mailing(self):
        get_mailing_query = "SELECT * FROM mailing"
        mailing = await self.__database_controller.get_data_execute_query(get_mailing_query)

        return mailing

    async def update_mailing(self, mailing_text: str):
        if len(await self.get_mailing()) != 0:
            update_mailing_query = f"UPDATE mailing SET mailing='{mailing_text}'"
            await self.__database_controller.execute_query(update_mailing_query)
        else:
            create_mailing_query = f"INSERT INTO mailing (mailing) VALUES ('{mailing_text}')"
            await self.__database_controller.execute_query(create_mailing_query)

    async def del_mailing(self):
        del_mailing_text = "DELETE FROM mailing"
        await self.__database_controller.execute_query(del_mailing_text)
