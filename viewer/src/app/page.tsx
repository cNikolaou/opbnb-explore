'use client';
import AggregateMetricsDisplay from '../components/AggregateMetricsDisplay';
import GasInfoDisplay from '../components/GasInfoDisplay';
import AddressActivityDisplay from '../components/AddressActivityDisplay';
import TransactionsValueDisplay from '../components/TransactionsValueDisplay';
import TransactionsFeeDisplay from '../components/TransactionsFeeDisplay';

export default function Home() {
  return (
    <>
      <h1>Metrics for the last 2 hours</h1>
      <GasInfoDisplay />
      <AggregateMetricsDisplay />
      <AddressActivityDisplay />
      <TransactionsValueDisplay />
      <TransactionsFeeDisplay />
    </>
  );
}
