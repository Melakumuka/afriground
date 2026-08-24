"use client";

import { useEffect, useState } from "react";
import { useT } from "@/lib/useT";
import type { Dataset } from "@/lib/api";

type DatasetRow = {
  id: string;
  satellite: string;
  product_type: string;
  capture_time: string;
  cloud_cover: number;
  size: string;
  status: "AVAILABLE" | "DELIVERING";
};

// Mock dataset
const MOCK_DATASETS: DatasetRow[] = [
  { id: "ds-1", satellite: "Aqua", product_type: "L1B_RAD", capture_time: "2024-05-12T14:30:00Z", cloud_cover: 12.5, size: "1.2 GB", status: "AVAILABLE" },
  { id: "ds-2", satellite: "Terra", product_type: "L0_RAW", capture_time: "2024-05-11T16:15:00Z", cloud_cover: 45.0, size: "850 MB", status: "AVAILABLE" },
  { id: "ds-3", satellite: "Aqua", product_type: "L1B_RAD", capture_time: "2024-05-10T14:28:00Z", cloud_cover: 5.2, size: "1.1 GB", status: "DELIVERING" },
];

function mapDataset(d: Dataset): DatasetRow {
  const satellite = d.satellite_id
    ? `SAT-${d.satellite_id.slice(0, 8).toUpperCase()}`
    : d.sensor_type ?? "UNKNOWN";
  return {
    id: d.id,
    satellite,
    product_type: d.product_type ?? d.processing_level ?? "—",
    capture_time: d.acquisition_date ?? "—",
    cloud_cover: d.cloud_cover ?? 0,
    size: d.storage_url ? "READY" : "—",
    status: d.storage_url ? "AVAILABLE" : "DELIVERING",
  };
}

export default function DataCatalog() {
  const { t } = useT("Data");
  const [datasets, setDatasets] = useState<DatasetRow[]>(MOCK_DATASETS);
  const [source, setSource] = useState<"mock" | "api">("mock");
  const [deliveryTarget, setDeliveryTarget] = useState("");
  const [isDelivering, setIsDelivering] = useState<string | null>(null);
  const [destinations, setDestinations] = useState<any[]>([]);

  useEffect(() => {
    fetch("/api/platform/data/destinations")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (Array.isArray(data)) setDestinations(data);
      })
      .catch(() => {});

  useEffect(() => {
    fetch("/api/platform/data/datasets")
      .then((res) => (res.ok ? res.json() : null))
      .then((payload) => {
        if (payload?.ok && Array.isArray(payload.data) && payload.data.length > 0) {
          setDatasets(payload.data.map(mapDataset));
          setSource("api");
        }
      })
      .catch(() => {
        /* API unreachable — keep the mock catalog */
      });
  }, []);

  const handleDeliver = (id: string) => {
    setIsDelivering(id);
    setTimeout(() => {
      setDatasets(datasets.map((d) => (d.id === id ? { ...d, status: "DELIVERING" } : d)));
      setIsDelivering(null);
    }, 1500);
  };

  return (
    <main className="min-h-screen bg-graphite text-ink">
      {/* ── Ops header ─────────────────────────────────────────── */}
      <div className="border-b border-graphite-600/60">
        <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-14">
          <span className="mono-label text-signal inline-flex items-center gap-3">
            <span className="w-8 h-px bg-signal" />
            {t("module", "运营模块 03 · 数据下传", "OPS-MODULE 03 · DATA DOWNLINK")}
          </span>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display font-bold text-4xl sm:text-5xl tracking-tight text-white">
                {t("title", "对地观测数据目录", "Earth Observation Data Catalog")}
              </h1>
              <p className="mt-4 text-steel-2 leading-relaxed max-w-lg">
                {t("subtitle", "检索已采集的数据集，并将其交付至您的基础设施。", "Search and deliver captured datasets to your infrastructure.")}
              </p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 border border-graphite-600">
              <span className="signal-indicator" />
              <span className="mono-label text-steel-2">{t("archive", "下传归档 · 二级", "Downlink Archive · Tier-2")}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-12 space-y-6">
        {/* Delivery destination */}
        <div className="console-panel rounded-sm p-6 sm:p-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
          <div className="flex items-center gap-3">
            <span className="signal-indicator" />
            <span className="mono-label text-signal-soft">{t("delivery_target", "交付目标", "DELIVERY TARGET")}</span>
          </div>
          <select
            value={deliveryTarget}
            onChange={(e) => setDeliveryTarget(e.target.value)}
            className="w-full sm:w-96 px-4 py-3 bg-graphite border border-graphite-600 text-white rounded-sm focus:border-signal/70 focus:outline-none"
          >
            <option value="">{t("select_dest", "选择交付目的地...", "Select Delivery Destination...")}</option>
            {destinations.map((dest) => (
              <option key={dest.id} value={dest.id}>
                {dest.type.toUpperCase()} ({dest.id.slice(0, 8)})
              </option>
            ))}
          </select>
        </div>

        {/* Data Grid */}
        <div className="console-panel rounded-sm overflow-hidden">
          <div className="px-6 sm:px-8 py-5 border-b border-graphite-600/60 bg-graphite-700/40 flex items-center justify-between">
            <span className="mono-label text-signal-soft">{t("captured", "已采集数据集", "CAPTURED DATASETS")}</span>
            <span className="font-mono text-[10px] text-graphite-mute">
              {source === "api" ? "LIVE · API FEED" : t("mock_feed", "模拟数据 · 模拟环境", "MOCK FEED · SIM ENV")}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[760px]">
              <thead>
                <tr className="bg-graphite-700/40 border-b border-graphite-600/60">
                  <th className="px-6 sm:px-8 py-4 mono-label text-steel-2 font-normal">{t("col_satellite", "卫星", "Satellite")}</th>
                  <th className="px-6 py-4 mono-label text-steel-2 font-normal">{t("col_product", "产品类型", "Product Type")}</th>
                  <th className="px-6 py-4 mono-label text-steel-2 font-normal">{t("col_capture", "采集时间（UTC）", "Capture Time (UTC)")}</th>
                  <th className="px-6 py-4 mono-label text-steel-2 font-normal">{t("col_cloud", "云量", "Cloud Cover")}</th>
                  <th className="px-6 py-4 mono-label text-steel-2 font-normal">{t("col_size", "大小", "Size")}</th>
                  <th className="px-6 py-4 mono-label text-steel-2 font-normal">{t("col_status", "状态", "Status")}</th>
                  <th className="px-6 sm:px-8 py-4 mono-label text-steel-2 font-normal text-right">{t("col_actions", "操作", "Actions")}</th>
                </tr>
              </thead>
              <tbody>
                {datasets.map((dataset) => (
                  <tr key={dataset.id} className="border-b border-graphite-600/40 last:border-0 hover:bg-graphite-700/30 transition-colors">
                    <td className="px-6 sm:px-8 py-4 font-medium text-white">{dataset.satellite}</td>
                    <td className="px-6 py-4 font-mono text-sm text-signal-soft">{dataset.product_type}</td>
                    <td className="px-6 py-4 text-steel-2 font-mono text-sm">
                      {new Date(dataset.capture_time).toLocaleString([], { timeZone: "UTC" })}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-16 h-1.5 bg-graphite-600">
                          <div
                            className={`h-full ${dataset.cloud_cover > 30 ? "bg-signal" : "bg-green-soft"}`}
                            style={{ width: `${dataset.cloud_cover}%` }}
                          />
                        </div>
                        <span className="font-mono text-sm text-steel-2">{dataset.cloud_cover}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-steel-2 font-mono text-sm">{dataset.size}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 border text-xs font-mono ${
                          dataset.status === "AVAILABLE"
                            ? "border-green/50 text-green-soft bg-green/10"
                            : "border-signal/50 text-signal-soft bg-signal/10 animate-pulse"
                        }`}
                      >
                        {dataset.status === "AVAILABLE" && <span className="w-1.5 h-1.5 rounded-full bg-green-soft" />}
                        {dataset.status === "DELIVERING" ? t("status_delivering", "交付中", "DELIVERING") : t("status_available", "可用", "AVAILABLE")}
                      </span>
                    </td>
                    <td className="px-6 sm:px-8 py-4 text-right">
                      <button
                        onClick={() => handleDeliver(dataset.id)}
                        disabled={!deliveryTarget || dataset.status === "DELIVERING" || isDelivering === dataset.id}
                        className="px-4 py-2 bg-signal hover:bg-signal-soft text-graphite text-sm font-semibold rounded-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                      >
                        {isDelivering === dataset.id ? t("pushing", "正在推送...", "Pushing...") : t("deliver", "交付", "Deliver")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <p className="mono-label text-graphite-mute">
          {source === "api"
            ? t("live_footer", "实时环境 · 来自 AfriGround API 的实时数据集", "LIVE ENVIRONMENT · DATASETS FROM THE AFRIGROUND API")
            : t("sim_footer", "模拟环境 · 记录为模拟数据，并非真实任务产品", "SIMULATION ENVIRONMENT · RECORDS ARE MOCK DATA, NOT LIVE MISSION PRODUCTS")}
        </p>
      </div>
    </main>
  );
}