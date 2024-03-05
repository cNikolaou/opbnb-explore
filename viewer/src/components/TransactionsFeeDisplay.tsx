import { useEffect, useState } from 'react';

import type {
  ResponseData,
  HighestGasPaidTransactions,
} from '../pages/api/transactions-fee-metrics';

export default function TransactionsFeeDisplay() {
  const [highestGasPaidTransactions, setHighestGasPaidTransactions] =
    useState<HighestGasPaidTransactions[]>();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/transactions-fee-metrics');
        const data: ResponseData = await res.json();
        setHighestGasPaidTransactions(data.highestGasPaidTransactions);
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
        <h2>Highest Gas Paid Transactions</h2>
        <table className="table-auto">
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
    </>
  );
}
