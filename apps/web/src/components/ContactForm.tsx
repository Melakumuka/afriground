"use client";

import { useState, type FormEvent } from "react";

export default function ContactForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setStatus("sending");
    setError("");
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, message }),
      });
      const data = (await res.json().catch(() => null)) as { error?: string } | null;
      if (!res.ok) {
        setStatus("error");
        setError(data?.error ?? `Transmission failed (${res.status})`);
        return;
      }
      setStatus("sent");
    } catch {
      setStatus("error");
      setError("Transmission failed. Please try again or email ops@afriground.space directly.");
    }
  };

  return (
    <div className="console-panel rounded-sm p-6 sm:p-8 bg-graphite-800 border border-graphite-600">
      <div className="flex items-center gap-3 mb-6">
        <span className="signal-indicator" />
        <span className="mono-label text-signal-soft">CONTACT TRANSMISSION · SECURE FORM</span>
      </div>

      {status === "sent" ? (
        <div className="border border-green/40 bg-green/10 px-5 py-6">
          <p className="font-mono text-sm text-green-soft font-semibold tracking-wider">
            ▸ MESSAGE TRANSMITTED
          </p>
          <p className="mt-2 text-sm text-steel-2">
            Thank you, {name.trim() || "friend"}. The AfriGround team will respond to{" "}
            <span className="text-white">{email}</span> within one business day.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="contact-name" className="mono-label text-steel-2 block mb-2">
              FULL NAME <span className="text-graphite-mute">(OPTIONAL)</span>
            </label>
            <input
              id="contact-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={120}
              placeholder="e.g. Dr. Amara Okafor"
              className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none"
            />
          </div>
          <div>
            <label htmlFor="contact-email" className="mono-label text-steel-2 block mb-2">
              EMAIL ADDRESS *
            </label>
            <input
              id="contact-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              maxLength={254}
              placeholder="you@mission.example"
              className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none"
            />
          </div>
          <div>
            <label htmlFor="contact-message" className="mono-label text-steel-2 block mb-2">
              MESSAGE *
            </label>
            <textarea
              id="contact-message"
              required
              minLength={10}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              maxLength={4000}
              rows={7}
              placeholder="Tell us about your mission, bandwidth needs, or partnership interest..."
              className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none resize-y"
            />
          </div>

          {status === "error" && (
            <div className="border border-signal/50 bg-signal/10 px-4 py-3">
              <p className="mono-label text-signal-soft">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={status === "sending"}
            className="w-full py-3.5 bg-signal hover:bg-signal-soft text-graphite font-semibold rounded-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {status === "sending" ? "TRANSMITTING ..." : "SEND TO AFRIGROUND →"}
          </button>
        </form>
      )}
    </div>
  );
}