"use client";

import { useEffect, useState } from "react";
import { useT } from "@/lib/useT";

type Destination = {
  id: string;
  type: string;
  is_active: boolean;
};

export default function DataEgressConfig() {
  const { t } = useT("Egress");
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [provider, setProvider] = useState("s3");
  const [config, setConfig] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/platform/data/destinations")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (Array.isArray(data)) setDestinations(data);
      })
      .catch((e) => {
        console.error(e);
      });
  }, []);

  const handleAdd = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/platform/data/destinations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          org_id: "00000000-0000-0000-0000-000000000000",
          type: provider,
          config,
        }),
      });
      if (res.ok) {
        setConfig({});
        const destRes = await fetch("/api/platform/data/destinations");
        if (destRes.ok) {
          const data = await destRes.json();
          if (Array.isArray(data)) setDestinations(data);
        }
      } else {
        const errorData = await res.json();
        setErrorMsg(errorData.detail || t("validate_fail", "验证或保存目标失败", "Failed to validate or save destination"));
      }
    } catch (e) {
      console.error(e);
      setErrorMsg(t("network_error", "网络错误。无法连接 API。", "Network error. Could not connect to API."));
    }
    setLoading(false);
  };

  const PROVIDERS = [
    { id: "s3", name: "Amazon S3", icon: "☁️" },
    { id: "gcs", name: "Google Cloud Storage", icon: "🌐" },
    { id: "alibaba_oss", name: "Alibaba Cloud OSS", icon: "🔶" },
    { id: "huawei_obs", name: "Huawei Cloud OBS", icon: "🔴" },
    { id: "baidu_bos", name: "Baidu Cloud BOS", icon: "🐾" },
    { id: "azure_blob", name: "Azure Blob Storage", icon: "🔷" },
  ];

  return (
    <main className="min-h-screen bg-graphite text-ink">
      {/* ── Header ─────────────────────────────────────────── */}
      <div className="border-b border-graphite-600/60">
        <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-14">
          <span className="mono-label text-signal inline-flex items-center gap-3">
            <span className="w-8 h-px bg-signal" />
            {t("module", "云端数据出口配置", "CLOUD DATA EGRESS CONFIG")}
          </span>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display font-bold text-4xl sm:text-5xl tracking-tight text-white">
                {t("title", "直接云交付", "Direct Cloud Delivery")}
              </h1>
              <p className="mt-4 text-steel-2 leading-relaxed max-w-lg">
                {t("subtitle", "将任务采集到的数据自动路由至您的私有云存储桶中。", "Automatically route captured data from missions directly to your private cloud storage buckets.")}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-12 grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Left: Configuration Form */}
        <div>
          <h2 className="text-2xl font-display font-bold text-white mb-6">
            {t("add_new", "添加新的交付目的地", "Add New Destination")}
          </h2>

          <div className="bg-yellow-500/10 border-l-4 border-yellow-500 p-4 mb-6 text-sm text-yellow-200/90">
            <strong>{t("security_notice", "安全提示：请勿提供根账户密钥。请确保您的访问密钥已通过 IAM 限制为仅对指定存储桶具有 PutObject（只写）权限。所有凭据均已在存储时对称加密。", "Security Notice: Do not provide Root account keys. Ensure your Access Key is restricted by IAM to PutObject (Write-Only) permissions for the designated bucket. All credentials are symmetrically encrypted at rest.")}</strong>
          </div>

          <div className="console-panel p-6 sm:p-8 space-y-6">
            <div>
              <label className="block mono-label text-steel-2 mb-3">
                {t("provider", "云提供商", "Cloud Provider")}
              </label>
              <div className="grid grid-cols-2 gap-3">
                {PROVIDERS.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setProvider(p.id)}
                    className={`flex items-center gap-3 p-4 border text-left transition-colors ${
                      provider === p.id
                        ? "border-signal bg-signal/10 text-white"
                        : "border-graphite-600 bg-graphite hover:border-graphite-500 text-steel-2"
                    }`}
                  >
                    <span className="text-xl">{p.icon}</span>
                    <span className="font-semibold text-sm">{p.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Dynamic Fields */}
            <div className="space-y-4 pt-4 border-t border-graphite-600">
              {provider === "gcs" ? (
                <>
                  <div>
                    <label className="block text-sm font-medium text-steel-2 mb-1">{t("bucket", "存储桶名称", "Bucket Name")}</label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-white focus:border-signal outline-none"
                      value={config.bucket || ""}
                      onChange={(e) => setConfig({ ...config, bucket: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-steel-2 mb-1">{t("gcp_sa", "服务账号 JSON", "Service Account JSON")}</label>
                    <textarea
                      rows={4}
                      className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-white focus:border-signal outline-none font-mono text-xs"
                      value={config.service_account_json || ""}
                      onChange={(e) => setConfig({ ...config, service_account_json: e.target.value })}
                    />
                  </div>
                </>
              ) : provider === "azure_blob" ? (
                <>
                  <div>
                    <label className="block text-sm font-medium text-steel-2 mb-1">{t("container", "容器名称", "Container Name")}</label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-white focus:border-signal outline-none"
                      value={config.container || ""}
                      onChange={(e) => setConfig({ ...config, container: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-steel-2 mb-1">{t("conn_string", "连接字符串", "Connection String")}</label>
                    <input
                      type="password"
                      className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-white focus:border-signal outline-none"
                      value={config.connection_string || ""}
                      onChange={(e) => setConfig({ ...config, connection_string: e.target.value })}
                    />
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-steel-2 mb-1">{t("bucket", "存储桶名称", "Bucket Name")}</label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-white focus:border-signal outline-none"
                      value={config.bucket || ""}
                      onChange={(e) => setConfig({ ...config, bucket: e.target.value })}
                    />
                  </div>
                  {provider !== "s3" && (
                    <div>
                      <label className="block text-sm font-medium text-steel-2 mb-1">{t("endpoint", "端点 (Endpoint)", "Endpoint")}</label>
                      <input
                        type="text"
                        className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-white focus:border-signal outline-none"
                        value={config.endpoint || ""}
                        onChange={(e) => setConfig({ ...config, endpoint: e.target.value })}
                        placeholder={
                          provider === "alibaba_oss" ? "oss-cn-hangzhou.aliyuncs.com" :
                          provider === "huawei_obs" ? "obs.cn-north-4.myhuaweicloud.com" :
                          provider === "baidu_bos" ? "bj.bcebos.com" : ""
                        }
                      />
                    </div>
                  )}
                  {provider === "s3" && (
                    <div>
                      <label className="block text-sm font-medium text-steel-2 mb-1">{t("region", "区域", "Region")}</label>
                      <input
                        type="text"
                        className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-white focus:border-signal outline-none"
                        value={config.region || ""}
                        onChange={(e) => setConfig({ ...config, region: e.target.value })}
                        placeholder="us-east-1"
                      />
                    </div>
                  )}
                  <div>
                    <label className="block text-sm font-medium text-steel-2 mb-1">{t("access_key", "访问密钥 (Access Key)", "Access Key")}</label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-white focus:border-signal outline-none"
                      value={config.access_key || ""}
                      onChange={(e) => setConfig({ ...config, access_key: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-steel-2 mb-1">{t("secret_key", "私有密钥 (Secret Key)", "Secret Key")}</label>
                    <input
                      type="password"
                      className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-white focus:border-signal outline-none"
                      value={config.secret_key || ""}
                      onChange={(e) => setConfig({ ...config, secret_key: e.target.value })}
                    />
                  </div>
                </>
              )}
            </div>

            {errorMsg && (
              <div className="p-3 bg-red-500/10 border border-red-500/50 text-red-400 text-sm rounded-sm">
                <strong>Error:</strong> {errorMsg}
              </div>
            )}

            <button
              onClick={handleAdd}
              disabled={loading}
              className="w-full py-4 bg-signal hover:bg-signal-soft text-graphite font-bold text-lg rounded-sm transition-colors mt-4"
            >
              {loading ? t("saving", "保存中...", "Saving...") : t("save", "保存配置", "Save Configuration")}
            </button>
          </div>
        </div>

        {/* Right: Active Destinations List */}
        <div>
          <h2 className="text-2xl font-display font-bold text-white mb-6">
            {t("active_dest", "活跃的交付目的地", "Active Destinations")}
          </h2>

          <div className="space-y-4">
            {destinations.length === 0 ? (
              <div className="console-panel p-8 text-center text-steel-2">
                {t("no_dest", "未配置目的地。请在左侧添加一个。", "No destinations configured. Add one on the left.")}
              </div>
            ) : (
              destinations.map((d) => {
                const providerInfo = PROVIDERS.find((p) => p.id === d.type);
                return (
                  <div key={d.id} className="console-panel p-5 flex items-center justify-between border-l-4 border-l-green-soft">
                    <div className="flex items-center gap-4">
                      <div className="text-3xl bg-graphite-600 p-3 rounded-md">
                        {providerInfo?.icon || "☁️"}
                      </div>
                      <div>
                        <div className="font-semibold text-white text-lg">{providerInfo?.name || d.type.toUpperCase()}</div>
                        <div className="font-mono text-xs text-steel-2 mt-1">ID: {d.id}</div>
                      </div>
                    </div>
                    <div className="px-3 py-1 bg-green-500/10 border border-green-500/50 text-green-soft text-xs font-mono font-bold">
                      ACTIVE
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
