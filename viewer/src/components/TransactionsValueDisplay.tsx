import { useEffect, useState } from 'react';

import type {
  ResponseData,
  HighestValueTransactions,
} from '../pages/api/transactions-value-metrics';

export default function TransactionsValueDisplay() {
  const [avgTransactionValue, setAvgTransactionValue] = useState<number>();
  const [highestValueTransactions, setHighestValueTransactions] =
    useState<HighestValueTransactions[]>();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/transactions-value-metrics');
        const data: ResponseData = await res.json();
        setAvgTransactionValue(data.avgTransactionValue);
        setHighestValueTransactions(data.highestValueTransactions);
        console.log(data);
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
      <div>
        <div>Average Transaction Value: {avgTransactionValue}</div>
      </div>
      <div>
        <h2>Highest Value Tranfered Transactions</h2>
        <table className="table-auto">
          <thead>
            <tr>
              <th>Transaction</th>
              <th>From</th>
              <th>To</th>
            </tr>
          </thead>
          <tbody>
            {highestValueTransactions &&
              highestValueTransactions?.map((trn) => (
                <tr key={trn.transaction_hash}>
                  <td>{trn.transaction_hash}</td>
                  <td>{trn.from_address}</td>
                  <td>{trn.to_address}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
