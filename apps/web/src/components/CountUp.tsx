"use client";

import { useEffect, useRef, useState } from "react";

export default function CountUp({
  value,
  duration = 1600,
}: {
  value: string;
  duration?: number;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const [text, setText] = useState("0");

  const match = value.match(/^([\d.,]+)(.*)$/);
  const target = match ? parseFloat(match[1].replace(/,/g, "")) : NaN;
  const suffix = match ? match[2] : value;
  const decimals = match && match[1].includes(".") ? (match[1].split(".")[1]?.length || 0) : 0;

  useEffect(() => {
    const el = ref.current;
    if (!el || !Number.isFinite(target)) {
      const t = setTimeout(() => setText(value), 0);
      return () => clearTimeout(t);
    }
    if (typeof IntersectionObserver === "undefined") {
      const t = setTimeout(() => setText(value), 0);
      return () => clearTimeout(t);
    }
    let raf = 0;
    const io = new IntersectionObserver(
      (entries) => {
        if (!entries.some((e) => e.isIntersecting)) return;
        io.disconnect();
        const start = performance.now();
        const tick = (now: number) => {
          const p = Math.min((now - start) / duration, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          setText((target * eased).toFixed(decimals) + suffix);
          if (p < 1) {
            raf = requestAnimationFrame(tick);
          } else {
            setText(value);
          }
        };
        raf = requestAnimationFrame(tick);
      },
      { threshold: 0.4 }
    );
    io.observe(el);
    return () => {
      io.disconnect();
      cancelAnimationFrame(raf);
    };
  }, [target, suffix, decimals, value, duration]);

  return <span ref={ref}>{text}</span>;
}