import Link from 'next/link';
import { getTranslations } from 'next-intl/server';

export default async function StationProfilesPage({ params }: { params: { id: string, locale: string } }) {
  const t = await getTranslations({ locale: params.locale, namespace: "StationProfiles" });

  // In a real app, we would fetch from the API here
  // const res = await fetch(`${process.env.AFRIGROUND_API_URL}/api/v1/stations/${params.id}/profiles`, { ... })
  // const profiles = await res.json();
  const profiles = [
    { id: 'prof-1', name: 'SENTINEL-2A_XBAND', status: 'CERTIFIED', satellite_id: 'sat-123' }
  ];

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t("title")}</h1>
          <p className="mt-2 text-sm text-gray-700">
            {t("subtitle")}
          </p>
        </div>
        <Link
          href={`/${params.locale}/station/${params.id}/profiles/new`}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none"
        >
          {t("new_profile")}
        </Link>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul role="list" className="divide-y divide-gray-200">
          {profiles.map((profile) => (
            <li key={profile.id}>
              <div className="px-4 py-4 sm:px-6 hover:bg-gray-50 flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium text-indigo-600 truncate">{profile.name}</p>
                  <p className="mt-1 text-sm text-gray-500">
                    {t("name")}: {profile.satellite_id}
                  </p>
                </div>
                <div className="flex items-center">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    {profile.status}
                  </span>
                </div>
              </div>
            </li>
          ))}
          {profiles.length === 0 && (
            <li className="px-4 py-4 sm:px-6 text-sm text-gray-500 text-center">
              {t("no_profiles")}
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
