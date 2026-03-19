import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class ACInfinityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_bluetooth(self, discovery_info):
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=discovery_info.address,
            data={"mac": discovery_info.address},
        )

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["mac"],
                data={"mac": user_input["mac"]},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("mac"): str
            }),
        )
