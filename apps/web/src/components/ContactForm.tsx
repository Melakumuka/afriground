"use client";

import { useState, type FormEvent } from "react";
import { useT } from "@/lib/useT";

export default function ContactForm() {
  const { t } = useT("ContactForm");
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
        setError(data?.error || t("err_transmit", "传输失败（状态码 {status}）", "Transmission failed ({status})").replace("{status}", String(res.status)));
        return;
      }
      setStatus("sent");
    } catch {
      setStatus("error");
      setError(t("err_try_again", "传输失败，请重试，或直接发送邮件至 ops@afriground.space。", "Transmission failed. Please try again or email ops@afriground.space directly."));
    }
  };

  return (
    <div className="console-panel rounded-sm p-6 sm:p-8 bg-graphite-800 border border-graphite-600">
      <div className="flex items-center gap-3 mb-6">
        <span className="signal-indicator" />
        <span className="mono-label text-signal-soft">{t("header", "联系传输 · 安全表单", "CONTACT TRANSMISSION · SECURE FORM")}</span>
      </div>

      {status === "sent" ? (
        <div className="border border-green/40 bg-green/10 px-5 py-6">
          <p className="font-mono text-sm text-green-soft font-semibold tracking-wider">
            ▸ {t("sent", "消息已发送", "MESSAGE TRANSMITTED")}
          </p>
          <p className="mt-2 text-sm text-steel-2">
            {t("thanks", "谢谢您，{name}。AfriGround 团队将在一个工作日内回复 {email}。", "Thank you, {name}. The AfriGround team will respond to {email} within one business day.")
              .replace("{name}", name.trim() || t("friend", "朋友", "friend"))
              .replace("{email}", email)}
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="contact-name" className="mono-label text-steel-2 block mb-2">
              {t("full_name", "姓名", "FULL NAME")} <span className="text-graphite-mute">{t("optional", "（选填）", "(OPTIONAL)")}</span>
            </label>
            <input
              id="contact-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={120}
              placeholder={t("name_placeholder", "例如 张三", "e.g. Dr. Amara Okafor")}
              className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none"
            />
          </div>
          <div>
            <label htmlFor="contact-email" className="mono-label text-steel-2 block mb-2">
              {t("email_label", "电子邮箱 *", "EMAIL ADDRESS *")}
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
              {t("msg_label", "内容 *", "MESSAGE *")}
            </label>
            <textarea
              id="contact-message"
              required
              minLength={10}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              maxLength={4000}
              rows={7}
              placeholder={t("msg_placeholder", "请介绍您的任务、带宽需求或合作意向...", "Tell us about your mission, bandwidth needs, or partnership interest...")}
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
            {status === "sending" ? t("transmitting", "正在发送 ...", "TRANSMITTING ...") : t("send", "发送至 AFRIGROUND →", "SEND TO AFRIGROUND →")}
          </button>
        </form>
      )}
    </div>
  );
}