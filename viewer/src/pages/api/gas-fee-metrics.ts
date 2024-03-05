import type { NextApiRequest, NextApiResponse } from 'next';

import { pool, prisma } from '../../lib/db';

type AvgEffectiveGasPrice = {
  block_range_start: string;
  block_range_end: string;
  avg_effective_gas_price: number;
};

export type ResponseData = {
  baseFeePerGas: string;
  latestBlockNumber: string;
  avgEffectiveGasPrice: AvgEffectiveGasPrice[];
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>,
) {
  const latestProcessedBlock = await prisma.blocks.findFirst({
    orderBy: { number: 'desc' },
  });

  const lastNumber = 7200;
  const groupInterval = 300;
  const endBlockNumber = latestProcessedBlock?.number || BigInt(1000);
  const startBlockNumber = endBlockNumber - BigInt(lastNumber);

  const query = `
    SELECT
      FLOOR((block_number - $1) / $3) * $3 + $1 AS block_range_start,
      FLOOR((block_number - $1) / $3) * $3 + $3 - 1 + $1 AS block_range_end,
      AVG(effective_gas_price) AS avg_effective_gas_price
    FROM
      receipts
    WHERE
      block_number >= $1 AND
      block_number <= $2
    GROUP BY
      FLOOR((block_number - $1) / $3)
    ORDER BY
      block_range_start ASC;
  `;

  const client = await pool.connect();
  const result = await client.query(query, [
    startBlockNumber,
    endBlockNumber,
    groupInterval,
  ]);

  console.log(result.rows);

  client.release();

  res.status(200).json({
    baseFeePerGas: String(latestProcessedBlock?.base_fee_per_gas),
    latestBlockNumber: String(latestProcessedBlock?.number),
    avgEffectiveGasPrice: result.rows,
  });
}
