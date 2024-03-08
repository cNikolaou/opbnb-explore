import { useEffect, useState } from 'react';

import type {
  ResponseData,
  HighestValueTransactions,
} from '../pages/api/transactions-value-metrics';

export default function TransactionsValueDisplay() {
  const [avgTransactionValue, setAvgTransactionValue] = useState<number>(0);
  const [highestValueTransactions, setHighestValueTransactions] =
    useState<HighestValueTransactions[]>();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/transactions-value-metrics');
        const data: ResponseData = await res.json();
        setAvgTransactionValue(data.avgTransactionValue);
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
      <h2 className="text-xl font-semibold mb-4 text-center">
        Highest Value Tranfered Transactions
      </h2>
      <div className="relative overflow-x-auto">
        <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              <th scope="col" className="px-6 py-3">
                Transaction (avg. value:{' '}
                {Math.round(avgTransactionValue / 1e12) / 1e6} BNB)
              </th>
            </tr>
          </thead>
          <tbody>
            {highestValueTransactions &&
              highestValueTransactions?.map((trn) => (
                <tr
                  key={trn.transaction_hash}
                  className="bg-white border-b dark:bg-gray-800 dark:border-gray-700"
                >
                  <td className="px-6 py-4">
                    <a
                      href={`https://opbnb.bscscan.com/tx/${trn.transaction_hash}`}
                    >
                      {trn.transaction_hash}
                    </a>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
