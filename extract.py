import logging

from web3 import Web3
from ethereumetl.jobs.export_all_common import export_all_common
from ethereumetl.cli.export_all import get_partitions
from ethereumetl.utils import check_classic_provider_uri

logger = logging.getLogger("extract")


PROVIDER_URI = "https://opbnb-mainnet-rpc.bnbchain.org"


def extract_data_up_to(
    block_number: int,
    block_batch_size: int = 100,
    output_dir: str = "data",
    max_workers: int = 5,
    concurrent_requests: int = 5,
):

    w3 = Web3(Web3.HTTPProvider(PROVIDER_URI))

    # Get the start and end block numbers
    earliest_block_number = w3.eth.get_block("earliest")["number"]
    latest_block_number = w3.eth.get_block("latest")["number"]
    up_to_block_number = min(block_number, latest_block_number)

    logger.info(f"Earliest block number: {earliest_block_number}")
    logger.info(f"Latest block number: {latest_block_number}")

    logger.info(
        f"Extracting data in the block range [{earliest_block_number} {up_to_block_number}]"
    )

    print(type(earliest_block_number))

    provider_uri = check_classic_provider_uri("ethereum", PROVIDER_URI)

    logger.info(f"Using the provider URI: {provider_uri}")

    # export data in the `./data` directory
    export_all_common(
        partitions=get_partitions(
            str(earliest_block_number),
            str(up_to_block_number),
            block_batch_size,
            PROVIDER_URI,
        ),
        output_dir=output_dir,
        provider_uri=PROVIDER_URI,
        max_workers=max_workers,
        batch_size=concurrent_requests,
    )


if __name__ == "__main__":
    extract_data_up_to(10)
