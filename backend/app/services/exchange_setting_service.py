from decimal import Decimal
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SettingValueType
from app.models.exchange_setting import ExchangeSetting


class ExchangeSettingService:

    ALLOWED_SETTING_TYPES = {
        SettingValueType.STRING,
        SettingValueType.BOOLEAN,
        SettingValueType.INTEGER,
        SettingValueType.DECIMAL,
        SettingValueType.JSON,
    }

    @staticmethod
    async def get_setting(
        db: AsyncSession,
        key: str,
    ) -> ExchangeSetting | None:

        key = key.strip().lower()

        result = await db.execute(
            select(ExchangeSetting).where(
                ExchangeSetting.key == key
            )
        )

        return result.scalar_one_or_none()


    @staticmethod
    async def list_settings(
        db: AsyncSession,
    ) -> list[ExchangeSetting]:
    
        result = await db.execute(
            select(ExchangeSetting).order_by(
                ExchangeSetting.key.asc()
            )
        )
    
        return list(result.scalars().all())
    
    
    @staticmethod
    async def get_string(
        db: AsyncSession,
        key: str,
    ) -> str | None:

        setting = await ExchangeSettingService.get_setting(db, key)

        return setting.value if setting else None

    @staticmethod
    async def get_boolean(
        db: AsyncSession,
        key: str,
    ) -> bool:

        value = await ExchangeSettingService.get_string(db, key)

        if value is None:
            return False

        return value.lower() in {
            "true",
            "1",
            "yes",
            "enabled",
        }

    
    @staticmethod
    async def get_integer(
        db: AsyncSession,
        key: str,
    ) -> int | None:

        value = await ExchangeSettingService.get_string(db, key)

        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Setting '{key}' is not a valid integer.")

    @staticmethod
    async def get_decimal(
        db: AsyncSession,
        key: str,
    ) -> Decimal | None:

        value = await ExchangeSettingService.get_string(db, key)

        if value is None:
            return None

        try:
            return Decimal(value)
        except Exception:
            raise ValueError(f"Setting '{key}' is not a valid decimal.")

    @staticmethod
    async def get_json(
        db: AsyncSession,
        key: str,
    ):

        value = await ExchangeSettingService.get_string(db, key)

        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"Setting '{key}' contains invalid JSON.")
    
    @staticmethod
    async def setting_exists(
        db: AsyncSession,
        key: str,
    ) -> bool:

        setting = await ExchangeSettingService.get_setting(db, key)

        return setting is not None


    @staticmethod
    async def create_setting(
        db: AsyncSession,
        *,
        key: str,
        value: str,
        value_type: str,
        description: str | None = None,
        is_public: bool = False,
    ) -> ExchangeSetting:

        key = key.strip().lower()

        if value_type not in ExchangeSettingService.ALLOWED_SETTING_TYPES:
            raise ValueError("Invalid exchange setting type.")

        existing = await ExchangeSettingService.get_setting(db, key)

        if existing:
            raise ValueError("Exchange setting already exists.")

        setting = ExchangeSetting(
            key=key,
            value=value,
            value_type=value_type,
            description=description,
            is_public=is_public,
        )

        db.add(setting)

        await db.flush()
        await db.refresh(setting)

        return setting

    @staticmethod
    async def update_setting(
        db: AsyncSession,
        *,
        key: str,
        value: str,
    ) -> ExchangeSetting:

        key = key.strip().lower()

        setting = await ExchangeSettingService.get_setting(db, key)

        if setting is None:
            raise ValueError("Exchange setting not found.")

        setting.value = value

        await db.flush()
        await db.refresh(setting)

        return setting

    @staticmethod
    async def delete_setting(
        db: AsyncSession,
        key: str,
    ) -> bool:

        key = key.strip().lower()

        setting = await ExchangeSettingService.get_setting(db, key)

        if setting is None:
            return False

        await db.delete(setting)
        await db.flush()

        return True


    @staticmethod
    async def list_public_settings(
        db: AsyncSession,
    ) -> list[ExchangeSetting]:

        result = await db.execute(
            select(ExchangeSetting)
            .where(ExchangeSetting.is_public.is_(True))
            .order_by(ExchangeSetting.key.asc())
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_public_settings_map(
        db: AsyncSession,
    ) -> dict[str, str]:

        settings = await ExchangeSettingService.list_settings(db)

        return {
            setting.key: setting.value
            for setting in settings
        }

    @staticmethod
    async def update_settings_bulk(
        db: AsyncSession,
        updates: dict[str, str],
    ) -> None:

        settings = await ExchangeSettingService.list_settings(db)

        setting_map = {
            s.key: s
            for s in settings
        }

        for key, value in updates.items():
            setting = setting_map.get(key)

            if setting:
                setting.value = value

        await db.flush()

    @staticmethod
    async def get_or_default(
        db: AsyncSession,
        key: str,
        default: str,
    ) -> str:

        value = await ExchangeSettingService.get_string(db, key)

        return value if value is not None else default    