import api from "./api";

export const getReports = () => {
    return api.get("/reports");
};

export const getReport = (id) => {
    return api.get(`/reports/${id}`);
};

export const createReport = (data) => {
    return api.post("/reports", data);
};

export const deleteReport = (id) => {
    return api.delete(`/reports/${id}`);
};

// ==========================================
// DOWNLOAD REPORT AS PDF
// ==========================================

export const downloadReport = async (id) => {
    try {
        // Get report data from backend
        const response = await api.get(`/reports/${id}`);

        const report = response.data;

        // Create printable HTML
        const reportWindow = window.open(
            "",
            "_blank",
            "width=900,height=700"
        );

        if (!reportWindow) {
            throw new Error(
                "Popup blocked. Please allow popups for this website."
            );
        }

        reportWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>GeoInsight AI Report #${id}</title>

                <style>
                    body {
                        font-family: Arial, sans-serif;
                        padding: 40px;
                        color: #1e293b;
                    }

                    h1 {
                        color: #166534;
                        margin-bottom: 5px;
                    }

                    h2 {
                        margin-top: 30px;
                        color: #334155;
                        border-bottom: 2px solid #e2e8f0;
                        padding-bottom: 8px;
                    }

                    .subtitle {
                        color: #64748b;
                        margin-bottom: 30px;
                    }

                    .grid {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 15px;
                    }

                    .card {
                        border: 1px solid #e2e8f0;
                        border-radius: 8px;
                        padding: 15px;
                    }

                    .label {
                        font-size: 12px;
                        color: #64748b;
                        margin-bottom: 5px;
                    }

                    .value {
                        font-size: 16px;
                        font-weight: bold;
                    }

                    .footer {
                        margin-top: 40px;
                        padding-top: 15px;
                        border-top: 1px solid #e2e8f0;
                        font-size: 11px;
                        color: #64748b;
                    }

                    @media print {
                        body {
                            padding: 20px;
                        }
                    }
                </style>
            </head>

            <body>

                <h1>GeoInsight AI</h1>

                <div class="subtitle">
                    Land Classification & Spatial Analysis Report
                </div>

                <h2>Report Information</h2>

                <div class="grid">

                    <div class="card">
                        <div class="label">Report ID</div>
                        <div class="value">#${report.id ?? id}</div>
                    </div>

                    <div class="card">
                        <div class="label">Village</div>
                        <div class="value">
                            ${report.village ?? "—"}
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">District</div>
                        <div class="value">
                            ${report.district ?? "—"}
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">State</div>
                        <div class="value">
                            ${report.state ?? "—"}
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">Analysis Date</div>
                        <div class="value">
                            ${report.date
                ? String(report.date).split("T")[0]
                : "—"
            }
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">Status</div>
                        <div class="value">
                            ${report.status ?? "Completed"}
                        </div>
                    </div>

                </div>

                <h2>Land Analysis</h2>

                <div class="grid">

                    <div class="card">
                        <div class="label">Total Area</div>
                        <div class="value">
                            ${Number(
                report.total_area ??
                report.totalArea ??
                0
            ).toFixed(2)} Ha
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">Mapped Area</div>
                        <div class="value">
                            ${Number(
                report.mapped_area ??
                report.mappedArea ??
                0
            ).toFixed(2)} Ha
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">Vegetation</div>
                        <div class="value">
                            ${Number(
                report.vegetation ?? 0
            ).toFixed(2)} Ha
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">Agricultural Land</div>
                        <div class="value">
                            ${Number(
                report.agriculture ??
                report.agriculturalLand ??
                0
            ).toFixed(2)} Ha
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">Water Bodies</div>
                        <div class="value">
                            ${Number(
                report.water ?? 0
            ).toFixed(2)} Ha
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">Built-up / Urban</div>
                        <div class="value">
                            ${Number(
                report.builtup ??
                report.urbanLand ??
                0
            ).toFixed(2)} Ha
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">Barren Land</div>
                        <div class="value">
                            ${Number(
                report.barren ?? 0
            ).toFixed(2)} Ha
                        </div>
                    </div>

                    <div class="card">
                        <div class="label">AI Confidence</div>
                        <div class="value">
                            ${Number(
                report.confidence ?? 0
            ).toFixed(2)}%
                        </div>
                    </div>

                </div>

                <div class="footer">
                    Generated by GeoInsight AI<br>
                    AI-based satellite land mapping and classification system.
                </div>

            </body>
            </html>
        `);

        reportWindow.document.close();

        // Wait for browser to render the report
        reportWindow.onload = () => {
            reportWindow.focus();
            reportWindow.print();
        };

    } catch (error) {
        console.error(
            "Report download error:",
            error
        );

        throw error;
    }
};
