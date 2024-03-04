import logging

from web3 import Web3
from ethereumetl.jobs.export_all_common import export_all_common
from ethereumetl.cli.export_all import get_partitions
from ethereumetl.utils import check_classic_provider_uri

from settings import PROVIDER_URI


logger = logging.getLogger(__name__)


def get_valid_range(start_block_number: int, end_block_number: int):
    """
    Get the valid range of block numbers; no negative `start_block_number`
    and no `end_block_number` greater than the latest block number
    """
    w3 = Web3(Web3.HTTPProvider(PROVIDER_URI))

    # Get the earliest and latest block numbers and update the range appropriately
    earliest_block_number = w3.eth.get_block("earliest")["number"]
    start_block_number = max(start_block_number, earliest_block_number)

    latest_block_number = w3.eth.get_block("latest")["number"]
    end_block_number = min(end_block_number, latest_block_number)

    return start_block_number, end_block_number


def extract_data(
    start_block_number: int = 0,
    end_block_number: int = 0,
    block_batch_size: int = 100,
    output_dir: str = "data",
    max_workers: int = 5,
    concurrent_requests: int = 5,
):
    """
    Use ethereumetl to extract data from the opBNB blockchain.

    The following parameters control the extraction process:
      - block_batch_size: number of blocks to export in each partition
      - max_workers: maximum number of concurrent workers
      - concurrent_requests: number of requests in JSON RPC batches
    """

    start_block_number, end_block_number = get_valid_range(
        start_block_number, end_block_number
    )

    logger.info(
        f"Extracting data in block range [{start_block_number}, {end_block_number}]"
    )

    provider_uri = check_classic_provider_uri("ethereum", PROVIDER_URI)

    logger.info(f"Using the provider URI: {provider_uri}")

    partitions = get_partitions(
        start=str(start_block_number),
        end=str(end_block_number),
        partition_batch_size=block_batch_size,
        provider_uri=PROVIDER_URI,
    )

    logger.info("Extracting data...")

    # export data in the `./data` directory
    export_all_common(
        partitions=partitions,
        output_dir=output_dir,
        provider_uri=PROVIDER_URI,
        max_workers=max_workers,
        batch_size=concurrent_requests,
    )

    logger.info("Extraction complete!")


if __name__ == "__main__":
    extract_data(end_block_number=10, block_batch_size=10)
