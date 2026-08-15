export type GroundStationNode = {
  id: string;
  name: string;
  country: string;
  lat: number;
  lng: number;
  dishSize: string;
  bands: string[];
  gtPerformance: string;
  minElevation: string;
  status: "Operational" | "Maintenance";
  description: string;
  topCoords: { top: string; left: string };
};

export const STATIONS: GroundStationNode[] = [
  {
    id: "entoto",
    name: "Entoto Space Observatory (ENT-1)",
    country: "Ethiopia 🇪🇹",
    lat: 9.076,
    lng: 38.74,
    dishSize: "12.0m Parabolic",
    bands: ["S-band", "X-band"],
    gtPerformance: "32.5 dB/K @ 8.2 GHz",
    minElevation: "5.0°",
    status: "Operational",
    description: "High-altitude equatorial hub providing high-elevation pass coverage over East and Central Africa with ultra-clear sky conditions.",
    topCoords: { top: "45%", left: "68%" }
  },
  {
    id: "hart",
    name: "Hartebeesthoek Space Station (HBK-1)",
    country: "South Africa 🇿🇦",
    lat: -25.886,
    lng: 27.707,
    dishSize: "9.3m Dual Feed",
    bands: ["S-band", "X-band", "Ka-band"],
    gtPerformance: "34.1 dB/K @ 26.0 GHz",
    minElevation: "3.5°",
    status: "Operational",
    description: "Southern hemisphere deep space and LEO downlink hub with multi-band Ka-band capability and fiber cloud backhaul.",
    topCoords: { top: "82%", left: "56%" }
  },
  {
    id: "malindi",
    name: "Malindi Space Center (MAL-1)",
    country: "Kenya 🇰🇪",
    lat: -2.996,
    lng: 40.194,
    dishSize: "10.0m Prime Focus",
    bands: ["S-band", "X-band"],
    gtPerformance: "30.8 dB/K @ 8.1 GHz",
    minElevation: "4.0°",
    status: "Operational",
    description: "Coastal Indian Ocean equatorial tracking station ideal for launch support, early orbit phase (LEOP), and LEO data downlinks.",
    topCoords: { top: "56%", left: "70%" }
  },
  {
    id: "abuja",
    name: "Abuja Regional Gateway (ABJ-1)",
    country: "Nigeria 🇳🇬",
    lat: 9.076,
    lng: 7.398,
    dishSize: "7.3m Az/El Quad",
    bands: ["S-band", "X-band"],
    gtPerformance: "28.5 dB/K @ 8.0 GHz",
    minElevation: "5.0°",
    status: "Operational",
    description: "West Africa hub optimized for Earth observation satellite data downlink, emergency payload stream, and weather monitoring.",
    topCoords: { top: "45%", left: "42%" }
  },
  {
    id: "cairo",
    name: "Cairo North Gateway (CAI-1)",
    country: "Egypt 🇪🇬",
    lat: 30.044,
    lng: 31.235,
    dishSize: "11.2m Cassegrain",
    bands: ["X-band", "Ka-band"],
    gtPerformance: "33.0 dB/K @ 8.4 GHz",
    minElevation: "3.0°",
    status: "Operational",
    description: "North African Mediterranean gateway linking European orbital passes with African ground backhaul networks.",
    topCoords: { top: "22%", left: "62%" }
  },
  {
    id: "dakar",
    name: "Dakar Atlantic Hub (DKR-1)",
    country: "Senegal 🇸🇳",
    lat: 14.716,
    lng: -17.467,
    dishSize: "5.5m Fast Steer",
    bands: ["S-band", "UHF/VHF"],
    gtPerformance: "24.2 dB/K @ 2.2 GHz",
    minElevation: "5.0°",
    status: "Operational",
    description: "Westernmost African ground terminal providing early detection and contact passes over the Atlantic Ocean corridor.",
    topCoords: { top: "40%", left: "22%" }
  }
];
