# import aiohttp
# import asyncio
# import ssl

# base_url = ("https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
#             "?sf={search_fields}&terms={search_term}&maxList={max_list}")

# codes = ["I10", "K21.9"]

# async def fetch(session, url):
#     async with session.get(url) as response:
#         return await response.json()

# async def main():
#     ssl_context = ssl.create_default_context()
#     ssl_context.check_hostname = False
#     ssl_context.verify_mode = ssl.CERT_NONE

#     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
#         tasks = []
#         for code in codes:
#             search_url = base_url.format(search_fields="code,desc", search_term=code, max_list=1)
#             tasks.append(fetch(session, search_url))

#         responses = await asyncio.gather(*tasks)

#         for response in responses:
#             print(response)

# # Run the main function
# asyncio.run(main())

import pandas as pd
print(pd.read_json("data.json"))