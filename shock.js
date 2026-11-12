
(() => {
  if (window.__aulaDebugger) {
    window.__aulaDebugger.restore();
  }

  const original = {
    open: HIDDevice.prototype.open,
    sendReport: HIDDevice.prototype.sendReport,
    sendFeatureReport: HIDDevice.prototype.sendFeatureReport,
    receiveFeatureReport: HIDDevice.prototype.receiveFeatureReport,
    getDevices: navigator.hid.getDevices.bind(navigator.hid),
    requestDevice: navigator.hid.requestDevice.bind(navigator.hid),
  };

  const logs = [];
  const listening = new WeakSet();
  const lastTx = new WeakMap();

  const hex = (data) =>
    Array.from(data, b =>
      b.toString(16).padStart(2, "0")
    ).join(" ").toUpperCase();

  function toBytes(data) {
    if (data instanceof DataView) {
      return new Uint8Array(
        data.buffer,
        data.byteOffset,
        data.byteLength
      );
    }

    if (ArrayBuffer.isView(data)) {
      return new Uint8Array(
        data.buffer,
        data.byteOffset,
        data.byteLength
      );
    }

    if (data instanceof ArrayBuffer) {
      return new Uint8Array(data);
    }

    return Uint8Array.from(data);
  }

  function info(device) {
    return {
      productName: device.productName,
      vendorId: device.vendorId,
      productId: device.productId,
      collections: device.collections.map(c => ({
        usagePage: `0x${c.usagePage.toString(16)}`,
        usage: `0x${c.usage.toString(16)}`,
        inputReportIds: c.inputReports.map(r => r.reportId),
        outputReportIds: c.outputReports.map(r => r.reportId),
        featureReportIds: c.featureReports.map(r => r.reportId),
      })),
    };
  }

  function log(direction, device, reportId, data, extra = {}) {
    const bytes = Uint8Array.from(toBytes(data));
    const now = performance.now();

    const entry = {
      time: new Date().toISOString(),
      direction,
      reportId,
      byteLength: bytes.length,
      hex: hex(bytes),
      decimal: Array.from(bytes),
      device: info(device),
      ...extra,
    };

    if (direction === "TX") {
      lastTx.set(device, now);
      entry.stack = new Error().stack;
    } else if (lastTx.has(device)) {
      entry.delayFromLastTxMs =
        Math.round((now - lastTx.get(device)) * 1000) / 1000;
    }

    logs.push(entry);

    const color = direction === "TX" ? "#3B82F6" : "#22C55E";

    console.log(
      `%c[HID ${direction}]`,
      `color:${color};font-weight:bold`,
      `ID=${reportId}`,
      `LEN=${bytes.length}`,
      hex(bytes),
      entry
    );

    return entry;
  }

  function attach(device) {
    if (listening.has(device)) return;

    listening.add(device);

    device.addEventListener("inputreport", event => {
      log(
        "RX",
        device,
        event.reportId,
        event.data
      );
    });
  }

  HIDDevice.prototype.open = async function(...args) {
    attach(this);

    console.log("[HID OPEN]", info(this));

    return original.open.apply(this, args);
  };

  HIDDevice.prototype.sendReport = async function(reportId, data) {
    attach(this);

    log("TX", this, reportId, data, {
      reportType: "output",
    });

    return original.sendReport.call(this, reportId, data);
  };

  HIDDevice.prototype.sendFeatureReport = async function(reportId, data) {
    attach(this);

    log("TX", this, reportId, data, {
      reportType: "feature",
    });

    return original.sendFeatureReport.call(this, reportId, data);
  };

  HIDDevice.prototype.receiveFeatureReport = async function(reportId) {
    attach(this);

    const result =
      await original.receiveFeatureReport.call(this, reportId);

    log("RX", this, reportId, result, {
      reportType: "feature",
    });

    return result;
  };

  async function getDevices(...args) {
    const devices = await original.getDevices(...args);

    devices.forEach(attach);

    console.log(
      "[HID DEVICES]",
      devices.map(info)
    );

    return devices;
  }

  async function requestDevice(...args) {
    const devices = await original.requestDevice(...args);

    devices.forEach(attach);

    console.log(
      "[HID REQUEST]",
      devices.map(info)
    );

    return devices;
  }

  navigator.hid.getDevices = getDevices;
  navigator.hid.requestDevice = requestDevice;

  const debuggerAPI = {
    logs,

    table() {
      console.table(
        logs.map((x, i) => ({
          index: i,
          time: x.time,
          direction: x.direction,
          reportType: x.reportType ?? "input",
          reportId: x.reportId,
          length: x.byteLength,
          hex: x.hex,
          delayMs: x.delayFromLastTxMs,
        }))
      );
    },

    clear() {
      logs.length = 0;
      console.clear();
    },

    export() {
      const json = JSON.stringify(logs, null, 2);

      const blob = new Blob([json], {
        type: "application/json",
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");

      a.href = url;
      a.download = `aula-hid-${Date.now()}.json`;
      a.click();

      setTimeout(() => URL.revokeObjectURL(url), 1000);
    },

    restore() {
      HIDDevice.prototype.open = original.open;
      HIDDevice.prototype.sendReport = original.sendReport;
      HIDDevice.prototype.sendFeatureReport =
        original.sendFeatureReport;
      HIDDevice.prototype.receiveFeatureReport =
        original.receiveFeatureReport;

      navigator.hid.getDevices = original.getDevices;
      navigator.hid.requestDevice = original.requestDevice;

      console.log("[AULA] Hooks restored");
      delete window.__aulaDebugger;
    },
  };

  window.__aulaDebugger = debuggerAPI;

  // Attach to devices already granted to this origin.
  original.getDevices().then(devices => {
    devices.forEach(attach);
  });

  console.log("[AULA] WebHID debugger installed");
})();
