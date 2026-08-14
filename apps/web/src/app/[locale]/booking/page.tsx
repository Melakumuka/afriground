"use client";

import { useState } from "react";

export default function BookingWizard() {
  const [step, setStep] = useState(1);
  const [isChecking, setIsChecking] = useState(false);
  
  // Mock State
  const [selectedSat, setSelectedSat] = useState("");
  const [compatibility, setCompatibility] = useState<"pending" | "compatible" | "incompatible">("pending");
  const [quote, setQuote] = useState<any>(null);

  const handlePredict = () => {
    setIsChecking(true);
    // Simulate backend SGP4 prediction + Compatibility check
    setTimeout(() => {
      setCompatibility("compatible");
      setIsChecking(false);
      setStep(2);
    }, 1500);
  };

  const handleQuote = () => {
    setIsChecking(true);
    // Simulate Commercial Engine quote generation
    setTimeout(() => {
      setQuote({
        total: 150.00,
        breakdown: [
          { desc: "Pass Duration (10 min @ $15/min)", cost: 150.00 }
        ]
      });
      setIsChecking(false);
      setStep(3);
    }, 1000);
  };

  const handleConfirm = () => {
    setIsChecking(true);
    setTimeout(() => {
      setIsChecking(false);
      setStep(4);
    }, 1000);
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8 flex justify-center items-start">
      <div className="max-w-3xl w-full bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
        
        {/* Header / Stepper */}
        <div className="bg-blue-900 text-white p-8">
          <h1 className="text-2xl font-bold mb-4">Schedule a Satellite Pass</h1>
          <div className="flex gap-4">
            <StepBadge num={1} active={step >= 1} label="Prediction" />
            <div className="flex-1 border-t border-blue-700 mt-3" />
            <StepBadge num={2} active={step >= 2} label="Compatibility" />
            <div className="flex-1 border-t border-blue-700 mt-3" />
            <StepBadge num={3} active={step >= 3} label="Quote & Book" />
          </div>
        </div>

        <div className="p-8">
          {/* STEP 1: PREDICTION */}
          {step === 1 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <h2 className="text-xl font-semibold text-gray-800">Select Mission parameters</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Satellite</label>
                  <select 
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    value={selectedSat}
                    onChange={(e) => setSelectedSat(e.target.value)}
                  >
                    <option value="">Choose a satellite...</option>
                    <option value="sat1">Aqua (NORAD: 27424)</option>
                    <option value="sat2">Terra (NORAD: 25994)</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ground Station</label>
                  <select className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <option>Entoto Observatory - Antenna A (12m)</option>
                    <option>Entoto Observatory - Antenna B (7.3m)</option>
                  </select>
                </div>
              </div>

              <button 
                onClick={handlePredict}
                disabled={!selectedSat || isChecking}
                className="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {isChecking ? "Running SGP4 & Compatibility Engines..." : "Predict Passes"}
              </button>
            </div>
          )}

          {/* STEP 2: COMPATIBILITY & PASS SELECTION */}
          {step === 2 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div className="flex items-start gap-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="bg-green-100 p-2 rounded-full text-green-600">✓</div>
                <div>
                  <h3 className="font-semibold text-green-800">Hardware Compatible</h3>
                  <p className="text-sm text-green-600 mt-1">
                    Satellite RF config matches station capabilities (S-Band, QPSK).
                  </p>
                </div>
              </div>

              <h2 className="text-lg font-semibold text-gray-800 mt-6">Available Passes (Next 24h)</h2>
              
              {/* Mock Pass List */}
              <div className="space-y-3">
                <PassOption time="14:30 UTC" duration="10m 15s" maxEl="82.4°" selected />
                <PassOption time="16:15 UTC" duration="8m 45s" maxEl="45.1°" />
                <PassOption time="04:20 UTC (Tomorrow)" duration="11m 20s" maxEl="88.9°" />
              </div>

              <div className="flex gap-3 pt-4">
                <button onClick={() => setStep(1)} className="px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50">Back</button>
                <button onClick={handleQuote} className="flex-1 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700">
                  {isChecking ? "Generating Quote..." : "Continue to Booking"}
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: QUOTE & BOOK */}
          {step === 3 && quote && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <h2 className="text-xl font-semibold text-gray-800">Review & Confirm Booking</h2>
              
              <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
                <h3 className="font-medium text-gray-500 uppercase text-sm mb-4">Commercial Quote</h3>
                
                <div className="space-y-3 mb-6">
                  {quote.breakdown.map((item: any, i: number) => (
                    <div key={i} className="flex justify-between text-gray-700">
                      <span>{item.desc}</span>
                      <span className="font-mono">${item.cost.toFixed(2)}</span>
                    </div>
                  ))}
                  <div className="pt-3 border-t border-gray-200 flex justify-between font-bold text-lg text-gray-900">
                    <span>Total</span>
                    <span className="font-mono text-blue-700">${quote.total.toFixed(2)}</span>
                  </div>
                </div>

                <p className="text-xs text-gray-400">
                  By confirming, this capacity will be temporarily reserved on the station schedule.
                </p>
              </div>

              <div className="flex gap-3">
                <button onClick={() => setStep(2)} className="px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50">Back</button>
                <button onClick={handleConfirm} className="flex-1 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 shadow-lg shadow-green-200">
                  {isChecking ? "Confirming..." : "Confirm Booking"}
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: SUCCESS */}
          {step === 4 && (
            <div className="text-center py-12 animate-in zoom-in-95">
              <div className="mx-auto w-20 h-20 bg-green-100 text-green-500 rounded-full flex items-center justify-center text-4xl mb-6 shadow-sm border border-green-200">✓</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Booking Confirmed!</h2>
              <p className="text-gray-500 mb-8 max-w-md mx-auto">
                Your pass has been successfully scheduled. The station edge node will automatically configure itself 5 minutes prior to AOS.
              </p>
              <button onClick={() => setStep(1)} className="text-blue-600 font-medium hover:underline">
                Schedule another pass
              </button>
            </div>
          )}

        </div>
      </div>
    </main>
  );
}

function StepBadge({ num, label, active }: { num: number, label: string, active: boolean }) {
  return (
    <div className={`flex items-center gap-2 ${active ? 'opacity-100' : 'opacity-50'}`}>
      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${active ? 'bg-white text-blue-900' : 'border border-blue-400 text-blue-100'}`}>
        {num}
      </div>
      <span className="font-medium text-sm hidden sm:block">{label}</span>
    </div>
  );
}

function PassOption({ time, duration, maxEl, selected = false }: { time: string, duration: string, maxEl: string, selected?: boolean }) {
  return (
    <div className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'}`}>
      <div className="flex justify-between items-center">
        <div>
          <div className="font-bold text-gray-900">{time}</div>
          <div className="text-sm text-gray-500 mt-1">AOS ➔ LOS</div>
        </div>
        <div className="text-right">
          <div className="font-mono text-gray-800">{duration}</div>
          <div className="text-sm text-gray-500 mt-1">Max El: {maxEl}</div>
        </div>
      </div>
    </div>
  );
}
