"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function NewProfilePage({ params }: { params: { id: string, locale: string } }) {
  const router = useRouter();
  const [name, setName] = useState('');
  const [satelliteId, setSatelliteId] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // In a real app, POST to API here
    // await fetch(`/api/v1/stations/${params.id}/profiles`, { ... })
    setTimeout(() => {
      setLoading(false);
      router.push(`/${params.locale}/station/${params.id}/profiles`);
    }, 1000);
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Create Operation Profile</h1>
        <p className="mt-2 text-sm text-gray-700">
          Map a satellite to your local hardware preset.
        </p>
      </div>

      <form className="space-y-6 bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6" onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Profile/Preset Name (Local MCS Name)
          </label>
          <div className="mt-1">
            <input
              type="text"
              name="name"
              id="name"
              className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
              placeholder="e.g., SENTINEL-2A_XBAND"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
        </div>

        <div>
          <label htmlFor="satellite" className="block text-sm font-medium text-gray-700">
            Satellite ID
          </label>
          <div className="mt-1">
            <input
              type="text"
              name="satellite"
              id="satellite"
              className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
              value={satelliteId}
              onChange={(e) => setSatelliteId(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => router.back()}
            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>
    </div>
  );
}
