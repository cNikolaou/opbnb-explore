'use client';
import TransactionsDataDisplay from '../components/TransactionsDataDisplay';

export default function Home() {
  return (
    <>
      <h1>Metrics for the last 2 hours</h1>
      <TransactionsDataDisplay />
    </>
  );
}
