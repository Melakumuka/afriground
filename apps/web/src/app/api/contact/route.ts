import { NextRequest, NextResponse } from "next/server";
import nodemailer from "nodemailer";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(request: NextRequest) {
  const body = (await request.json().catch(() => null)) as {
    name?: string;
    email?: string;
    message?: string;
  } | null;

  const name = (body?.name ?? "").trim().slice(0, 120);
  const email = (body?.email ?? "").trim().slice(0, 254);
  const message = (body?.message ?? "").trim().slice(0, 4000);

  if (!EMAIL_RE.test(email)) {
    return NextResponse.json({ error: "A valid email address is required." }, { status: 400 });
  }
  if (message.length < 10) {
    return NextResponse.json({ error: "Message must be at least 10 characters." }, { status: 400 });
  }

  const host = process.env.SMTP_HOST;
  const port = Number(process.env.SMTP_PORT ?? "587");
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;
  const to = process.env.CONTACT_TO;
  const from = process.env.CONTACT_FROM ?? (user ?? "contact@afriground.space");

  if (!host || !user || !pass || !to) {
    return NextResponse.json(
      { error: "SMTP is not configured on this server. Ask ops to set SMTP_HOST, SMTP_USER, SMTP_PASS and CONTACT_TO." },
      { status: 503 }
    );
  }

  try {
    const transporter = nodemailer.createTransport({
      host,
      port,
      secure: (process.env.SMTP_SECURE ?? "").toLowerCase() === "true",
      auth: { user, pass },
    });

    await transporter.sendMail({
      from: `${name || "AfriGround visitor"} <${from}>`,
      to,
      replyTo: email,
      subject: `AfriGround contact — ${name || email}`,
      text: [
        `Name: ${name || "(not provided)"}`,
        `Email: ${email}`,
        "",
        message,
      ].join("\n"),
    });

    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json(
      { error: "Message could not be delivered. Please email us directly at ops@afriground.space." },
      { status: 500 }
    );
  }
}