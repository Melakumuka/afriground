"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

// Mock dataset
const MOCK_DATASETS = [
  { id: "ds-1", satellite: "Aqua", product_type: "L1B_RAD", capture_time: "2024-05-12T14:30:00Z", cloud_cover: 12.5, size: "1.2 GB", status: "AVAILABLE" },
  { id: "ds-2", satellite: "Terra", product_type: "L0_RAW", capture_time: "2024-05-11T16:15:00Z", cloud_cover: 45.0, size: "850 MB", status: "AVAILABLE" },
  { id: "ds-3", satellite: "Aqua", product_type: "L1B_RAD", capture_time: "2024-05-10T14:28:00Z", cloud_cover: 5.2, size: "1.1 GB", status: "DELIVERING" },
];

export default function DataCatalog() {
  const t = useTranslations("Dashboard");
  const [datasets, setDatasets] = useState(MOCK_DATASETS);
  const [deliveryTarget, setDeliveryTarget] = useState("");
  const [isDelivering, setIsDelivering] = useState<string | null>(null);

  const handleDeliver = (id: string) => {
    setIsDelivering(id);
    setTimeout(() => {
      setDatasets(datasets.map(d => d.id === id ? { ...d, status: "DELIVERING" } : d));
      setIsDelivering(null);
    }, 1500);
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Earth Observation Data Catalog</h1>
            <p className="text-gray-500">Search and deliver captured datasets to your infrastructure.</p>
          </div>
          <div className="flex gap-4">
            <select 
              value={deliveryTarget} 
              onChange={e => setDeliveryTarget(e.target.value)}
              className="p-2 border border-gray-300 rounded-lg text-sm bg-gray-50"
            >
              <option value="">Select Delivery Destination...</option>
              <option value="s3">AWS S3 (s3://my-org-bucket)</option>
              <option value="gcp">Google Cloud Storage (gs://my-org-data)</option>
            </select>
          </div>
        </div>

        {/* Data Grid */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="p-4 font-semibold text-gray-700">Satellite</th>
                <th className="p-4 font-semibold text-gray-700">Product Type</th>
                <th className="p-4 font-semibold text-gray-700">Capture Time (UTC)</th>
                <th className="p-4 font-semibold text-gray-700">Cloud Cover</th>
                <th className="p-4 font-semibold text-gray-700">Size</th>
                <th className="p-4 font-semibold text-gray-700">Status</th>
                <th className="p-4 font-semibold text-gray-700 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((dataset) => (
                <tr key={dataset.id} className="border-b border-gray-100 last:border-0 hover:bg-gray-50 transition-colors">
                  <td className="p-4 font-medium text-gray-900">{dataset.satellite}</td>
                  <td className="p-4 text-gray-600 font-mono text-sm">{dataset.product_type}</td>
                  <td className="p-4 text-gray-600">{new Date(dataset.capture_time).toLocaleString()}</td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${dataset.cloud_cover > 30 ? 'bg-red-400' : 'bg-green-400'}`} 
                          style={{ width: `${dataset.cloud_cover}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-500">{dataset.cloud_cover}%</span>
                    </div>
                  </td>
                  <td className="p-4 text-gray-600">{dataset.size}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      dataset.status === 'AVAILABLE' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700 animate-pulse'
                    }`}>
                      {dataset.status}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <button 
                      onClick={() => handleDeliver(dataset.id)}
                      disabled={!deliveryTarget || dataset.status === 'DELIVERING' || isDelivering === dataset.id}
                      className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                      {isDelivering === dataset.id ? "Pushing..." : "Deliver"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </main>
  );
}
