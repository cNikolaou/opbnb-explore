import type { NextApiRequest, NextApiResponse } from 'next';

import { pool } from '../../lib/db';

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
  const client = await pool.connect();

  const latestProcessedBlockQuery = `
    SELECT
      number, base_fee_per_gas
    FROM
      blocks
    ORDER BY
      number DESC
    LIMIT 1;
  `;

  const latestProcessedBlockResult = await client.query(
    latestProcessedBlockQuery,
  );

  const latestProcessedBlock = BigInt(
    latestProcessedBlockResult.rows[0].number,
  );

  const lastNumber = 7200;
  const groupInterval = 300;
  const endBlockNumber = latestProcessedBlock;
  const startBlockNumber = endBlockNumber - BigInt(lastNumber);

  const gasFeeAvgQuery = `
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

  const gasFeeAvgResult = await client.query(gasFeeAvgQuery, [
    startBlockNumber,
    endBlockNumber,
    groupInterval,
  ]);

  console.log(gasFeeAvgResult.rows);

  client.release();

  res.status(200).json({
    baseFeePerGas: latestProcessedBlockResult.rows[0].base_fee_per_gas,
    latestBlockNumber: latestProcessedBlockResult.rows[0].number,
    avgEffectiveGasPrice: gasFeeAvgResult.rows,
  });
}
