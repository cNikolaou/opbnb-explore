import { useEffect, useState } from 'react';

import type {
  ResponseData,
  MostActiveAddresses,
} from '../pages/api/address-metrics';

export default function AddressActivityDisplay() {
  const [mostActiveAddresses, setMostActiveAddresses] =
    useState<MostActiveAddresses[]>();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/address-metrics');
        const data: ResponseData = await res.json();
        setMostActiveAddresses(data.mostActiveAddresses);
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
        Addresses with Most Activity
      </h2>
      <div className="relative overflow-x-auto">
        <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              <th scope="col" className="px-6 py-3">
                Address
              </th>
              <th scope="col" className="px-6 py-3">
                Transactions
              </th>
            </tr>
          </thead>
          <tbody>
            {mostActiveAddresses &&
              mostActiveAddresses.map((address) => (
                <tr
                  key={address.address}
                  className="bg-white border-b dark:bg-gray-800 dark:border-gray-700"
                >
                  <td className="px-6 py-4">
                    <a
                      href={`https://opbnb.bscscan.com/address/${address.address}`}
                    >
                      {address.address}
                    </a>
                  </td>
                  <td className="px-6 py-4">{address.transaction_count}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
