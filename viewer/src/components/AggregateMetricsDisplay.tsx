import { useEffect, useState } from 'react';

import type { ResponseData as BlockMetricsResposne } from '../pages/api/block-metrics';
import type {
  ResponseData as ContractMetricsResponse,
  ContractsCreated,
} from '../pages/api/contract-metrics';

export default function AggregateMetricsDisplay() {
  const [avgBlockTime, setAvgBlockTime] = useState<number>();
  const [avgTransactionsPerBlock, setAvgTransactionsPerBlock] =
    useState<number>();
  const [contractsCreated, setContractsCreated] =
    useState<ContractsCreated[]>();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const blockRes = await fetch('/api/block-metrics');
        const blockData: BlockMetricsResposne = await blockRes.json();
        setAvgBlockTime(blockData.avgBlockTime);
        setAvgTransactionsPerBlock(blockData.avgTransactionsPerBlock);

        const contractRes = await fetch('/api/contract-metrics');
        const contractData: ContractMetricsResponse = await contractRes.json();
        setContractsCreated(contractData.contractsCreated);
      } catch (e) {
        console.error(e);
      }
    };

    fetchData();

    const intervalId = setInterval(fetchData, 20000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <>
      <div className="mx-auto max-w-md text-left mb-5">
        <div>Block Time (avg.): {avgBlockTime}</div>
        <div>Transactions per Block (avg.): {avgTransactionsPerBlock}</div>
        <div>Contracts Created: {contractsCreated?.length}</div>
      </div>
    </>
  );
}
