"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";

export default function StationRegistrationWizard() {
  const params = useParams();
  const router = useRouter();
  const locale = params.locale as string || "en";
  
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [station, setStation] = useState({ name: "", country: "", code: "" });
  const [hardware, setHardware] = useState({ 
    antenna_size: "7.3", 
    min_elevation: "5.0", 
  });
  const [rf, setRf] = useState({ 
    band: "S", 
    tx_authorized: false,
    max_tx_power: "87",
    gain: "18.0",
    polarization: "RHCP_LHCP"
  });

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      // Step 1: Mock creating station (In real app, we'd call the API)
      // For now, we simulate a small delay to show the UX
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Step 2: Add Station Capability
      /*
      const capRes = await fetch("http://localhost:8000/api/v1/stations/mock-id/capabilities", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          band: rf.band,
          frequency_min_hz: 2000000000,
          frequency_max_hz: 2300000000,
          polarization: rf.polarization,
          max_tx_power_dbm: parseFloat(rf.max_tx_power),
          tx_authorized: rf.tx_authorized,
          gain_dbi: parseFloat(rf.gain)
        })
      });
      if (!capRes.ok) throw new Error("Failed to register capabilities");
      */

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
          <h2 className="text-2xl font-bold text-white mb-2">Station Registered</h2>
          <p className="text-steel-2 mb-8">Your digital twin capabilities have been successfully registered with the cloud.</p>
          <button 
            onClick={() => router.push(`/${locale}`)}
            className="w-full py-3 bg-signal hover:bg-signal-soft text-black font-semibold transition-colors"
          >
            Return Home
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
          <h1 className="text-4xl font-display font-bold mb-4">Station Digital Twin Registration</h1>
          <p className="text-steel-2 text-lg">Declare your ground station hardware capabilities to join the routing network.</p>
        </div>

        {/* Wizard Steps */}
        <div className="flex gap-4 mb-8">
          <div className={`h-2 flex-1 transition-colors ${step >= 1 ? 'bg-signal' : 'bg-graphite-600'}`} />
          <div className={`h-2 flex-1 transition-colors ${step >= 2 ? 'bg-signal' : 'bg-graphite-600'}`} />
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
              <h2 className="text-2xl font-bold border-b border-graphite-500 pb-4 mb-6">Step 1: Station Details</h2>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-steel-2 mb-2">Station Name</label>
                  <input 
                    type="text" 
                    value={station.name}
                    onChange={e => setStation({...station, name: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                    placeholder="e.g. EMS-GRS 730 Ground Station"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-steel-2 mb-2">Country</label>
                  <input 
                    type="text" 
                    value={station.country}
                    onChange={e => setStation({...station, country: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                    placeholder="e.g. Ethiopia"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-steel-2 mb-2">Station Code</label>
                  <input 
                    type="text" 
                    value={station.code}
                    onChange={e => setStation({...station, code: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                    placeholder="e.g. ET-ENTOTO-01"
                  />
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold border-b border-graphite-500 pb-4 mb-6">Step 2: Hardware Capabilities</h2>
              
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-steel-2 mb-2">Antenna Diameter (m)</label>
                  <input 
                    type="number" 
                    value={hardware.antenna_size}
                    onChange={e => setHardware({...hardware, antenna_size: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-steel-2 mb-2">Min Elevation (deg)</label>
                  <input 
                    type="number" 
                    value={hardware.min_elevation}
                    onChange={e => setHardware({...hardware, min_elevation: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6 mt-6 pt-6 border-t border-graphite-500">
                <div>
                  <label className="block text-sm font-medium text-steel-2 mb-2">Band</label>
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
                  <label className="block text-sm font-medium text-steel-2 mb-2">Gain (dBi)</label>
                  <input 
                    type="number" 
                    value={rf.gain}
                    onChange={e => setRf({...rf, gain: e.target.value})}
                    className="w-full bg-graphite-500 border border-graphite-400 p-3 text-white focus:border-signal outline-none transition-colors"
                  />
                </div>
              </div>
              
              <label className="flex items-center gap-3 mt-4 p-4 border border-graphite-500 bg-graphite-500 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={rf.tx_authorized}
                  onChange={e => setRf({...rf, tx_authorized: e.target.checked})}
                  className="w-5 h-5 text-signal bg-graphite border-graphite-400 focus:ring-signal"
                />
                <div>
                  <div className="font-semibold text-white">TX Authorized (Uplink)</div>
                  <div className="text-xs text-steel-2">Does this station have a valid transmitting license?</div>
                </div>
              </label>
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

            {step < 2 ? (
              <button 
                onClick={() => setStep(step + 1)}
                disabled={!station.name && step === 1}
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
                {isSubmitting ? 'Registering...' : 'Register Twin'}
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
