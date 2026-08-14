"use client";

import { useState } from "react";

// Mock tickets
const MOCK_TICKETS = [
  { id: "TKT-1042", subject: "S-Band Interference during Terra pass", category: "Technical", priority: "High", status: "Investigating", created_at: "2024-05-12T10:00:00Z" },
  { id: "TKT-1041", subject: "Update billing address for invoice #442", category: "Billing", priority: "Normal", status: "Resolved", created_at: "2024-05-10T09:15:00Z" },
  { id: "TKT-1040", subject: "API Key generation failed", category: "Technical", priority: "Urgent", status: "Open", created_at: "2024-05-12T14:20:00Z" },
];

export default function SupportPortal() {
  const [tickets, setTickets] = useState(MOCK_TICKETS);
  const [isCreating, setIsCreating] = useState(false);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Support & Ticketing</h1>
            <p className="text-gray-500">Manage technical incidents and billing inquiries.</p>
          </div>
          <button 
            onClick={() => setIsCreating(!isCreating)}
            className="px-5 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            {isCreating ? "Cancel" : "Open New Ticket"}
          </button>
        </div>

        <div className="flex gap-6 items-start">
          
          {/* Ticket List */}
          <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 bg-gray-50 border-b border-gray-200 font-semibold text-gray-700">
              Active Tickets
            </div>
            <div className="divide-y divide-gray-100">
              {tickets.map((t) => (
                <div key={t.id} className="p-5 hover:bg-gray-50 transition-colors cursor-pointer flex justify-between items-center">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <span className="font-mono text-sm text-gray-500">{t.id}</span>
                      <h3 className="font-semibold text-gray-900">{t.subject}</h3>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>{t.category}</span>
                      <span>•</span>
                      <span>Opened: {new Date(t.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                      t.priority === 'Urgent' ? 'bg-red-100 text-red-700' :
                      t.priority === 'High' ? 'bg-orange-100 text-orange-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {t.priority}
                    </span>
                    <span className={`text-sm font-medium ${
                      t.status === 'Resolved' ? 'text-green-600' : 'text-blue-600'
                    }`}>
                      {t.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* New Ticket Form Panel */}
          {isCreating && (
            <div className="w-96 bg-white p-6 rounded-xl shadow-lg border border-gray-200 animate-in slide-in-from-right-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Create Support Ticket</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select className="w-full p-2.5 border border-gray-300 rounded-lg">
                    <option>Technical Support</option>
                    <option>Billing & Contracts</option>
                    <option>Scheduling & Bookings</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select className="w-full p-2.5 border border-gray-300 rounded-lg">
                    <option>Normal</option>
                    <option>High</option>
                    <option>Urgent</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                  <input type="text" className="w-full p-2.5 border border-gray-300 rounded-lg" placeholder="Brief summary" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea className="w-full p-2.5 border border-gray-300 rounded-lg h-32" placeholder="Provide details..." />
                </div>
                <button 
                  onClick={() => setIsCreating(false)}
                  className="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
                >
                  Submit Ticket
                </button>
              </div>
            </div>
          )}

        </div>
      </div>
    </main>
  );
}
