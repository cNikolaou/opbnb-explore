'use client';
import AggregateMetricsDisplay from '../components/AggregateMetricsDisplay';
import GasInfoDisplay from '../components/GasInfoDisplay';
import AddressActivityDisplay from '../components/AddressActivityDisplay';
import TransactionsValueDisplay from '../components/TransactionsValueDisplay';
import TransactionsFeeDisplay from '../components/TransactionsFeeDisplay';

export default function Home() {
  return (
    <>
      <div className="container mx-auto px-4">
        <h1 className="text-center text-xl font-bold my-8">opBNB Metrics</h1>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-200 p-4">
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4 text-center">
                General Metrics
              </h2>
              <AggregateMetricsDisplay />
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-4 text-center">
                Gas Fees
              </h2>
              <GasInfoDisplay />
            </div>
          </div>
          <div className="bg-gray-200 p-4">
            <AddressActivityDisplay />
          </div>
          <div className="bg-gray-200 p-4">
            <TransactionsValueDisplay />
          </div>
          <div className="bg-gray-200 p-4">
            <TransactionsFeeDisplay />
          </div>
        </div>
      </div>
    </>
  );
}
