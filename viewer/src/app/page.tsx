'use client';
import TransactionsDataDisplay from '../components/TransactionsDataDisplay';
import AggregateMetricsDisplay from '../components/AggregateMetricsDisplay';
import GasInfoDisplay from '../components/GasInfoDisplay';

export default function Home() {
  return (
    <>
      <h1>Metrics for the last 2 hours</h1>
      <GasInfoDisplay />
      <AggregateMetricsDisplay />
      <TransactionsDataDisplay />
    </>
  );
}
