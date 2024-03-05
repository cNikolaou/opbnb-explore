import { useEffect, useState } from 'react';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

import type { ResponseData } from '../pages/api/gas-fee-metrics';

export default function GasInfoDisplay() {
  const [baseFeePerGas, setBaseFeePerGas] = useState('');
  const [latestBlockNumber, setlatestBlockNumber] = useState('');
  const [avgEffectiveGasPrice, setAvgEffectiveGasPrice] = useState<any[]>();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/gas-fee-metrics');
        const data: ResponseData = await res.json();
        setBaseFeePerGas(data.baseFeePerGas);
        setlatestBlockNumber(data.latestBlockNumber);

        let count = data.avgEffectiveGasPrice.length + 1;
        const avg = data.avgEffectiveGasPrice.map((d) => {
          count--;
          return {
            name: `${count * 5} minutes ago`,
            avg: Math.round(d.avg_effective_gas_price / 1e3),
          };
        });
        setAvgEffectiveGasPrice(avg);
      } catch (e) {
        console.error(e);
      }
    };

    fetchData();

    const intervalId = setInterval(fetchData, 10000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <>
      <div className="mx-auto max-w-md text-left mb-5">
        <div>Latest Block Number: {latestBlockNumber}</div>
        <div>Latest Block Base Gas Fee: {baseFeePerGas}</div>
      </div>

      <div className="flex justify-center items-center bg-gray-200 p-4">
        <LineChart
          width={500}
          height={300}
          data={avgEffectiveGasPrice}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
          style={{ backgroundColor: 'white' }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis tick={false} dataKey="name" label="Gas in Gwei" />
          <YAxis />
          <Tooltip
            formatter={(value, name, props) => [`${value} Gwei`, 'Average Gas']}
            itemStyle={{ color: 'black' }}
          />
          <Line
            type="monotone"
            dataKey="avg"
            stroke="#ffc658"
            strokeWidth={3}
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </div>
    </>
  );
}
