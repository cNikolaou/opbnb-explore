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
      <div>
        <table className="table-auto">
          <thead>
            <tr>
              <th>Address</th>
              <th>Transactions</th>
            </tr>
          </thead>
          <tbody>
            {mostActiveAddresses &&
              mostActiveAddresses.map((address) => (
                <tr key={address.address}>
                  <td>{address.address}</td>
                  <td>{address.transaction_count}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
