import datetime

from web3 import Web3

import settings

w3 = Web3(Web3.HTTPProvider(settings.PROVIDER_URI))


def get_unix_timestamp(year, month, day):
    """Helper function to get the unix timestamp"""
    return int(datetime.datetime(year, month, day).timestamp())


def find_first_block_after_timestamp(timestamp):
    """Binary search to find the first block after the timestamp"""
    latest_block = w3.eth.get_block("latest")["number"]
    high = latest_block
    low = 0

    while low < high:
        mid = (high + low) // 2

        mid_block_timestamp = w3.eth.get_block(mid)["timestamp"]

        # print("Mid: ", mid, "  --  ", mid_block_timestamp)

        if mid_block_timestamp < timestamp:
            low = mid + 1
        else:
            high = mid

    return low


start_date_timestamp = get_unix_timestamp(2024, 2, 1)
end_date_timestamp = get_unix_timestamp(2024, 2, 5)

print(
    "Star timestamp: %s, End timestamp: %s" % (start_date_timestamp, end_date_timestamp)
)

start_block = find_first_block_after_timestamp(start_date_timestamp)
end_block = find_first_block_after_timestamp(end_date_timestamp)

print("Strat block: %s, End block: %s" % (start_block, end_block))
