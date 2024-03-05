import { useEffect, useState } from 'react';

import type {
  ResponseData,
  HighestGasPaidTransactions,
  HighestValueTransactions,
} from '../pages/api/transaction-metrics';

export default function TransactionsDataDisplay() {
  const [avgTransactionValue, setAvgTransactionValue] = useState<number>();
  const [transactionSuccessRate, setTransactionSuccessRate] = useState<
    number | null
  >();
  const [highestGasPaidTransactions, setHighestGasPaidTransactions] =
    useState<HighestGasPaidTransactions[]>();
  const [highestValueTransactions, setHighestValueTransactions] =
    useState<HighestValueTransactions[]>();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/transaction-metrics');
        const data: ResponseData = await res.json();
        setAvgTransactionValue(data.avgTransactionValue);
        setTransactionSuccessRate(data.transactionSuccessRate);
        setHighestGasPaidTransactions(data.highestGasPaidTransactions);
        setHighestValueTransactions(data.highestValueTransactions);
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
        <h2>Highest Gas Paid Transactions</h2>
        <table className="table-auto w-full">
          <thead>
            <tr>
              <th>Transaction</th>
              <th>From</th>
              <th>To</th>
            </tr>
          </thead>
          <tbody>
            {highestGasPaidTransactions &&
              highestGasPaidTransactions?.map((trn) => (
                <tr key={trn.transaction_hash}>
                  <td>{trn.transaction_hash}</td>
                  <td>{trn.from_address}</td>
                  <td>{trn.to_address}</td>
                </tr>
              ))}
          </tbody>
        </table>
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
