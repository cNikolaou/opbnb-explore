import type { NextApiRequest, NextApiResponse } from 'next';

import { pool } from '../../lib/db';

export type ContractsCreated = {
  cotract_address: string;
};

export type ResponseData = {
  contractsCreated: ContractsCreated[];
  mostActiveContracts: null;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>,
) {
  const client = await pool.connect();

  // Array of new contracts that were created
  const contractsCreatedQuery = `
    SELECT
      DISTINCT r.contract_address
    FROM
      receipts r JOIN blocks b ON b.number = r.block_number
    WHERE
      r.contract_address IS NOT NULL
    AND
      b.timestamp > EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours');
  `;

  const contractsCreatedResposne = await client.query(contractsCreatedQuery);

  // TODO: Implement mostActiveContractsQuery that requires that addresses
  // of all contracts to be known before running the query.
  const mostActiveContractsQuery = ``;

  const mostActiveContractsResponse = await client.query(
    mostActiveContractsQuery,
  );

  client.release();

  res.status(200).json({
    contractsCreated: contractsCreatedResposne.rows,
    mostActiveContracts: null,
  });
}
