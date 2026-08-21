"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";

export default function MissionOnboardingWizard() {
  const params = useParams();
  const router = useRouter();
  const locale = params.locale as string || "en";
  
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [spacecraft, setSpacecraft] = useState({ name: "", norad_id: "" });
  const [profile, setProfile] = useState({ orbit_type: "LEO", inclination: "" });
  const [rf, setRf] = useState({ 
    band: "S", 
    uplink_mhz: "2025", 
    downlink_mhz: "2200", 
    max_tx_power: "50",
    polarization: "RHCP"
  });

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      // Step 1: Create Spacecraft
      const scRes = await fetch("http://localhost:8000/api/v1/missions/spacecraft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: spacecraft.name,
          norad_id: parseInt(spacecraft.norad_id) || 0,
          org_id: "demo",
          status: "operational"
        })
      });
      if (!scRes.ok) throw new Error("Failed to create spacecraft");
      
      // Step 2: Create Mission Profile
      const profRes = await fetch("http://localhost:8000/api/v1/missions/profiles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mission_id: "00000000-0000-0000-0000-000000000000", // mock ID for now
          name: `${spacecraft.name} Profile`,
          version: "1.0",
          orbit_type: profile.orbit_type
        })
      });
      if (!profRes.ok) throw new Error("Failed to create mission profile");
      
      // Step 3: Create RF Profile (ICD)
      const rfRes = await fetch("http://localhost:8000/api/v1/missions/rf-profiles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mission_profile_id: "00000000-0000-0000-0000-000000000000", // mock ID for now
          band: rf.band,
          uplink_frequency_hz: parseFloat(rf.uplink_mhz) * 1_000_000,
          downlink_frequency_hz: parseFloat(rf.downlink_mhz) * 1_000_000,
          max_tx_power_dbm: parseFloat(rf.max_tx_power),
          polarization: rf.polarization,
          uplink_modulation: "GMSK",
          downlink_modulation: "QPSK",
          symbol_rate: 32000.0,
          is_uplink_enabled: true
        })
      });
      if (!rfRes.ok) throw new Error("Failed to create RF profile (ICD)");

      setSuccess(true);
    } catch (e: any) {
      setError(e.message || "An unexpected error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-graphite flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-graphite-600 border border-graphite-500 p-8 text-center shadow-2xl">
          <div className="w-16 h-16 bg-green-soft/20 text-green-soft rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Satellite Registered</h2>
          <p className="text-steel-2 mb-8">Your satellite ICD and RF profile have been securely stored in the AfriGround registry.</p>
          <button 
            onClick={() => router.push(`/${locale}/booking`)}
            className="w-full py-3 bg-signal hover:bg-signal-soft text-black font-semibold transition-colors"
          >
            Go to Scheduling
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-graphite text-white pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-4xl font-display font-bold mb-4">Satellite Onboarding Wizard</h1>
          <p className="text-steel-2 text-lg">Define your spacecraft parameters and Interface Control Document (ICD) to enable ground station routing.</p>
        </div>

        {/* Wizard Steps */}
        <div className="flex gap-4 mb-8">
          <div className={`h-2 flex-1 transition-colors ${step >= 1 ? 'bg-signal' : 'bg-graphite-600'}`} />
          <div className={`h-2 flex-1 transition-colors ${step >= 2 ? 'bg-signal' : 'bg-graphite-600'}`} />
          <div className={`h-2 flex-1 transition-colors ${step >= 3 ? 'bg-signal' : 'bg-graphite-600'}`} />
        </div>

        {/* Error */}
        {error && (
          <div className="mb-8 p-4 bg-red-900/30 border border-red-500/50 text-red-200">
            {error}
          </div>
        )}

        <div className="bg-graphite-600 border border-graphite-500 p-8 shadow-2xl relative overflow-hidden">
          {step === 1 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold border-b border-graphite-500 pb-4 mb-6">Step 1: Spacecraft Details</h2>
              
              <div>
                <label className="block text-sm font-medium text-steel-2 mb-2">Spacecraft Name</label>
                <input 
                  type="text" 
                  value={spacecraft.name}
                  onChange={e => setSpacecraft({...spacecraft, name: e.target.value})}
                  className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  placeholder="e.g. Sentinel-2A"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-steel-2 mb-2">NORAD ID (if known)</label>
                <input 
                  type="text" 
                  value={spacecraft.norad_id}
                  onChange={e => setSpacecraft({...spacecraft, norad_id: e.target.value})}
                  className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  placeholder="e.g. 40012"
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold border-b border-graphite-500 pb-4 mb-6">Step 2: Mission Profile</h2>
              
              <div>
                <label className="block text-sm font-medium text-steel-2 mb-2">Orbit Type</label>
                <select 
                  value={profile.orbit_type}
                  onChange={e => setProfile({...profile, orbit_type: e.target.value})}
                  className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                >
                  <option value="LEO">LEO (Low Earth Orbit)</option>
                  <option value="MEO">MEO (Medium Earth Orbit)</option>
                  <option value="GEO">GEO (Geostationary)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-steel-2 mb-2">Inclination (degrees)</label>
                <input 
                  type="number" 
                  value={profile.inclination}
                  onChange={e => setProfile({...profile, inclination: e.target.value})}
                  className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  placeholder="98.0"
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold border-b border-graphite-500 pb-4 mb-6">Step 3: RF Parameters (ICD)</h2>
              
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-steel-2 mb-2">Primary Band</label>
                  <select 
                    value={rf.band}
                    onChange={e => setRf({...rf, band: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  >
                    <option value="S">S-Band</option>
                    <option value="X">X-Band</option>
                    <option value="UHF">UHF</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-steel-2 mb-2">Polarization</label>
                  <select 
                    value={rf.polarization}
                    onChange={e => setRf({...rf, polarization: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  >
                    <option value="RHCP">RHCP</option>
                    <option value="LHCP">LHCP</option>
                    <option value="Linear">Linear</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-steel-2 mb-2">Uplink (MHz)</label>
                  <input 
                    type="number" 
                    value={rf.uplink_mhz}
                    onChange={e => setRf({...rf, uplink_mhz: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-steel-2 mb-2">Downlink (MHz)</label>
                  <input 
                    type="number" 
                    value={rf.downlink_mhz}
                    onChange={e => setRf({...rf, downlink_mhz: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-steel-2 mb-2">Max TX Power (dBm)</label>
                <input 
                  type="number" 
                  value={rf.max_tx_power}
                  onChange={e => setRf({...rf, max_tx_power: e.target.value})}
                  className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                />
                <p className="text-xs text-steel-2 mt-2">Required for regulatory compliance checking.</p>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="mt-10 flex justify-between pt-6 border-t border-graphite-500">
            {step > 1 ? (
              <button 
                onClick={() => setStep(step - 1)}
                className="px-6 py-2 border border-graphite-400 text-steel-2 hover:text-white transition-colors"
              >
                Back
              </button>
            ) : <div />}

            {step < 3 ? (
              <button 
                onClick={() => setStep(step + 1)}
                disabled={!spacecraft.name && step === 1}
                className="px-6 py-2 bg-signal hover:bg-signal-soft text-black font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue
              </button>
            ) : (
              <button 
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="px-8 py-2 bg-signal hover:bg-signal-soft text-black font-bold transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    Submitting...
                  </>
                ) : 'Submit ICD'}
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
