from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def test_asyncio():
    engine = create_async_engine("duckdb:///:memory:")
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            session.add(AsyncAttrs())
        await session.flush()
        await session.commit()
        await session.close()
