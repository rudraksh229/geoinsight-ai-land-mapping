import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { downloadReport } from '../services/reportService';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import NotificationToast from '../components/NotificationToast';

const Reports = () => {
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  const [selectedVillage, setSelectedVillage] = useState('');
  const [selectedDate, setSelectedDate] = useState('');

  const [villageOptions, setVillageOptions] = useState([]);

  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  const showToast = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
  };

  const fetchReports = async () => {
    setLoading(true);

    try {
      const res = await api.get('/reports', {
        params: {
          search: searchQuery,
          village: selectedVillage,
          date: selectedDate,
        },
      });

      setReports(res.data);

      if (villageOptions.length === 0) {
        const allRes = await api.get('/reports');

        const uniqueVillages = [
          ...new Set(allRes.data.map((r) => r.village)),
        ];

        setVillageOptions(uniqueVillages);
      }
    } catch (err) {
      showToast('Error loading report archives.', 'error');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [selectedVillage, selectedDate]);

  const handleSearchSubmit = (val) => {
    fetchReports();
    showToast(`Search completed for "${val || 'all'}"`, 'info');
  };

  const handleResetFilters = () => {
    setSelectedVillage('');
    setSelectedDate('');
    setSearchQuery('');

    api.get('/reports').then((res) => {
      setReports(res.data);
    });

    showToast('Filters cleared', 'info');
  };

  const handleDownloadCSV = (report) => {
    showToast(
      `Exporting metadata for ${report.id} to CSV...`,
      'success'
    );

    const headers = [
      'ReportID',
      'Village',
      'District',
      'State',
      'Date',
      'Total Area (Ha)',
      'Confidence (%)',
      'Prediction Time (s)',
    ];

    const row = [
      report.id,
      report.village,
      report.district,
      report.state,
      report.date,
      report.totalArea,
      report.confidence,
      report.predictionTime,
    ];

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), row.join(',')].join('\n');

    const encodedUri = encodeURI(csvContent);

    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute(
      'download',
      `${report.id}_classification_metadata.csv`
    );

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadPDF = async (report) => {
    try {
      showToast(
        `Generating PDF report for ${report.id}...`,
        'info'
      );

      await downloadReport(report.id);

      showToast(
        `PDF report ${report.id} downloaded successfully.`,
        'success'
      );
    } catch (error) {
      console.error('PDF download error:', error);

      showToast(
        'Failed to download PDF report.',
        'error'
      );
    }
  };

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl text-white dark:text-white font-bold mt-1 uppercase tracking-wider">
            Spatial Analysis Archives
          </h2>

          <p className="text-xs text-slate-400 dark:text-slate-500 font-bold mt-1 uppercase tracking-wider">
            Review, filter, and export spatial classification records
          </p>
        </div>
      </div>

      {/* Filter and Search Panel */}
      <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xs space-y-4 transition-colors duration-300">

        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">

          <SearchBar
            placeholder="Search report ID, village name..."
            value={searchQuery}
            onChange={(val) => setSearchQuery(val)}
            onSearch={handleSearchSubmit}
            className="md:max-w-md"
          />

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">

            {/* Filter by Village */}
            <div className="flex-1 sm:flex-initial">
              <select
                value={selectedVillage}
                onChange={(e) => setSelectedVillage(e.target.value)}
                className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 focus:border-green-600 focus:bg-white dark:focus:bg-slate-950 rounded-xl outline-hidden text-slate-700 dark:text-slate-300 cursor-pointer"
              >
                <option value="">All Villages</option>

                {villageOptions.map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
            </div>

            {/* Filter by Date */}
            <div className="flex-1 sm:flex-initial">
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full text-xs font-semibold py-2 px-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 focus:border-green-600 focus:bg-white dark:focus:bg-slate-950 rounded-xl outline-hidden text-slate-700 dark:text-slate-100"
              />
            </div>

            {/* Reset Filters */}
            <button
              onClick={handleResetFilters}
              className="text-xs font-bold text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 px-4 py-2.5 rounded-xl uppercase tracking-wider transition-colors cursor-pointer"
            >
              Clear
            </button>

          </div>
        </div>
      </div>

      {/* Reports Table Container */}
      <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl p-6 shadow-xs transition-colors duration-300">

        {loading ? (
          <div className="py-12 flex items-center justify-center">
            <LoadingSpinner message="Searching archive repositories..." />
          </div>
        ) : (
          <div className="overflow-x-auto -mx-6">

            <table className="w-full text-left border-collapse min-w-[800px]">

              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest bg-slate-50/50 dark:bg-slate-950/20">

                  <th className="py-3 px-6">
                    Report Identifier
                  </th>

                  <th className="py-3 px-6">
                    Location (Village / Dist)
                  </th>

                  <th className="py-3 px-6">
                    State
                  </th>

                  <th className="py-3 px-6">
                    Imaging Date
                  </th>

                  <th className="py-3 px-6 text-right">
                    Analysed Area
                  </th>

                  <th className="py-3 px-6 text-right">
                    Model Confidence
                  </th>

                  <th className="py-3 px-6 text-center">
                    Export Actions
                  </th>

                </tr>
              </thead>

              <tbody>

                {reports.length > 0 ? (
                  reports.map((report) => (
                    <tr
                      key={report.id}
                      className="border-b border-slate-50 dark:border-slate-800 last:border-0 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors text-xs font-semibold"
                    >

                      {/* Report ID */}
                      <td className="py-4 px-6 font-mono font-bold text-green-700 dark:text-green-400">
                        {report.id}
                      </td>

                      {/* Location - FORCE INLINE WHITE */}
                      <td className="py-4 px-6 font-bold" style={{ color: '#ffffff', opacity: 1 }}>
                        {report.village || 'N/A'}

                        <span className="block text-[10px] font-bold" style={{ color: '#cbd5e1', opacity: 1 }}>
                          {report.district} District
                        </span>
                      </td>

                      {/* State - FORCE INLINE WHITE */}
                      <td className="py-4 px-6 font-bold" style={{ color: '#ffffff', opacity: 1 }}>
                        {report.state || 'N/A'}
                      </td>

                      {/* Imaging Date - FORCE INLINE WHITE + DATA FALLBACK */}
                      <td className="py-4 px-6 font-bold" style={{ color: '#ffffff', opacity: 1 }}>
                        {report.date || report.created_at || report.imaging_date || 'N/A'}
                      </td>

                      {/* Analysed Area - FORCE INLINE WHITE + DATA FALLBACK */}
                      <td className="py-4 px-6 text-right font-bold" style={{ color: '#ffffff', opacity: 1 }}>
                        {report.totalArea ?? report.analysed_area ?? report.area ?? '0'} Ha
                      </td>

                      {/* Model Confidence */}
                      <td className="py-4 px-6 text-right text-emerald-600 dark:text-emerald-400 font-bold">
                        {report.confidence}%
                      </td>

                      {/* Export Actions */}
                      <td className="py-4 px-6">

                        <div className="flex items-center justify-center gap-2">

                          {/* CSV Button */}
                          <button
                            onClick={() => handleDownloadCSV(report)}
                            className="p-2 rounded-lg bg-green-50 dark:bg-green-950/20 text-green-700 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/40 transition-colors cursor-pointer flex items-center justify-center border border-transparent dark:border-green-800/30"
                            title="Download CSV Metadata"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              fill="none"
                              viewBox="0 0 24 24"
                              strokeWidth={2}
                              stroke="currentColor"
                              className="w-4 h-4"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5a1.5 1.5 0 00-1.5 1.5v16.5A1.5 1.5 0 002.25 22.5h16.5a1.5 1.5 0 001.5-1.5V18m-6-15h.008v.008H16.5V3zm0 3h.008v.008H16.5V6zm0 3h.008v.008H16.5V9zm0 3h.008v.008H16.5v-.008zm-9-1.5h.008v.008H7.5v-.008zm-.75 3h.008v.008H6.75v-.008zm.75 3H7.5v-.008h.008v.008zm1.5-3H9v-.008h.008v.008zm-.75 3H8.25v-.008h.008v.008zm1.5-3H10.5v-.008h.008v.008zm-.75 3H9.75v-.008h.008v.008zm1.5-3H12v-.008h.008v.008zm-.75 3H11.25v-.008h.008v.008z"
                              />
                            </svg>
                          </button>

                          {/* PDF Button */}
                          <button
                            onClick={() => handleDownloadPDF(report)}
                            className="p-2 rounded-lg bg-red-50 dark:bg-red-950/20 text-red-700 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors cursor-pointer flex items-center justify-center border border-transparent dark:border-red-800/30"
                            title="Download PDF Classification Report"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              fill="none"
                              viewBox="0 0 24 24"
                              strokeWidth={2}
                              stroke="currentColor"
                              className="w-4 h-4"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m.75 12H9m3 0H9m3.75-2.25A14.98 14.98 0 0012 11.25c-2.906 0-5.687-.474-8.25-1.343M12 14.25V21m0 0l-3-3m3 3l3-3"
                              />
                            </svg>
                          </button>

                        </div>
                      </td>

                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan="7"
                      className="text-center py-12 font-medium"
                      style={{ color: '#94a3b8' }}
                    >
                      No matching records archived. Try altering filter indices.
                    </td>
                  </tr>
                )}

              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Toast */}
      {toastMessage && (
        <NotificationToast
          message={toastMessage}
          type={toastType}
          onClose={() => setToastMessage('')}
        />
      )}

    </div>
  );
};

export default Reports;
