from api import API
import asyncio

if __name__ == "__main__":
    CLS = API()
    asyncio.run(CLS.run())
