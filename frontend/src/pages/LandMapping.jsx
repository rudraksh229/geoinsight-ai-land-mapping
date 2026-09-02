import React, { useEffect, useState } from 'react';
import {
  MapContainer,
  Polygon,
  Popup,
  TileLayer,
  useMap,
} from 'react-leaflet';

import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import api from '../services/api';
import { useTheme } from '../context/ThemeContext';
import MapLegend from '../components/MapLegend';
import NotificationToast from '../components/NotificationToast';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix Leaflet default marker icons issue in Vite builds
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

// ==========================================
// MAP VIEW CONTROLLER
// ==========================================

const ChangeMapView = ({ center }) => {
  const map = useMap();

  useEffect(() => {
    if (
      center &&
      center.length === 2 &&
      center[0] !== undefined &&
      center[1] !== undefined
    ) {
      map.setView(center, 13, {
        animate: true,
        duration: 1.5,
      });
    }
  }, [center, map]);

  return null;
};

// ==========================================
// LAND MAPPING COMPONENT
// ==========================================

const LandMapping = () => {
  const { theme } = useTheme();

  // ==========================================
  // GEOGRAPHY METADATA
  // ==========================================

  const [geoMetadata, setGeoMetadata] = useState(null);
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [villages, setVillages] = useState([]);

  // ==========================================
  // USER SELECTIONS
  // ==========================================

  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedVillage, setSelectedVillage] = useState('');
  const [selectedDate, setSelectedDate] = useState('');

  // ==========================================
  // MAP STATE
  // ==========================================

  const [mapCenter, setMapCenter] = useState([18.5913, 73.7386]);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // ==========================================
  // TOAST
  // ==========================================

  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  const showToast = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
  };

  // ==========================================
  // LOAD GEOGRAPHY DATA
  // ==========================================

  useEffect(() => {
    const fetchGeoMetadata = async () => {
      try {
        const res = await api.get('/geography/metadata');

        setGeoMetadata(res.data);
        setStates(res.data.states || []);
      } catch (err) {
        console.error('Geography metadata error:', err);

        showToast(
          'Failed to load geographic indices.',
          'error'
        );
      }
    };

    fetchGeoMetadata();
  }, []);

  // ==========================================
  // STATE → DISTRICTS
  // ==========================================

  useEffect(() => {
    if (selectedState && geoMetadata) {
      setDistricts(
        geoMetadata.districts?.[selectedState] || []
      );

      setSelectedDistrict('');
      setVillages([]);
      setSelectedVillage('');
    } else {
      setDistricts([]);
      setVillages([]);
    }
  }, [selectedState, geoMetadata]);

  // ==========================================
  // DISTRICT → VILLAGES
  // ==========================================

  useEffect(() => {
    if (selectedDistrict && geoMetadata) {
      setVillages(
        geoMetadata.villages?.[selectedDistrict] || []
      );

      setSelectedVillage('');
    } else {
      setVillages([]);
    }
  }, [selectedDistrict, geoMetadata]);

  // ==========================================
  // VILLAGE → MAP CENTER
  // ==========================================

  useEffect(() => {
    if (selectedVillage && villages.length > 0) {
      const villageObj = villages.find(
        (v) => v.code === selectedVillage
      );

      if (villageObj) {
        setMapCenter([
          villageObj.lat,
          villageObj.lng,
        ]);

        showToast(
          `Centered map viewport on ${villageObj.name} village.`,
          'info'
        );
      }
    }
  }, [selectedVillage, villages]);

  // ==========================================
  // ANALYZE LAND
  // ==========================================

  const handleAnalyze = async () => {
    if (
      !selectedState ||
      !selectedDistrict ||
      !selectedVillage ||
      !selectedDate
    ) {
      showToast(
        'Mandatory criteria missing. Please complete all form inputs.',
        'warning'
      );

      return;
    }

    const activeVillage = villages.find(
      (v) => v.code === selectedVillage
    );

    if (!activeVillage) {
      showToast(
        'Selected village information could not be found.',
        'error'
      );

      return;
    }

    setIsAnalyzing(true);
    setAnalysisResults(null);

    try {
      const payload = {
        state: selectedState,
        district: selectedDistrict,
        village: activeVillage.name,
        date: selectedDate,
        lat: activeVillage.lat,
        lng: activeVillage.lng,
      };

      console.log(
        'Sending land analysis request:',
        payload
      );

      const res = await api.post(
        '/mapping/analyze',
        payload
      );

      console.log(
        'Land analysis response:',
        res.data
      );

      setAnalysisResults(res.data);

      showToast(
        'AI classification generated successfully!',
        'success'
      );
    } catch (err) {
      console.error(
        'Land analysis error:',
        err
      );

      const message =
        err.response?.data?.detail ||
        'Classification model encountered an operational error.';

      showToast(message, 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // ==========================================
  // RESET
  // ==========================================

  const handleReset = () => {
    setSelectedState('');
    setSelectedDistrict('');
    setSelectedVillage('');
    setSelectedDate('');
    setAnalysisResults(null);

    setMapCenter([18.5913, 73.7386]);

    showToast(
      'Filters and spatial maps reset.',
      'info'
    );
  };

  // ==========================================
  // RENDER AI POLYGONS
  // ==========================================

  const renderPolygons = () => {
    if (
      !analysisResults ||
      !analysisResults.mapData ||
      !analysisResults.mapData.features
    ) {
      return null;
    }

    return analysisResults.mapData.features.map(
      (feature, idx) => {
        const classType = feature.properties?.type;
        const label = feature.properties?.label;
        const area = feature.properties?.area;
        const fillColor = feature.properties?.color;

        if (
          !feature.geometry ||
          !feature.geometry.coordinates
        ) {
          return null;
        }

        const geoCoords =
          feature.geometry.coordinates[0];

        const positions = geoCoords.map((coord) => [
          coord[1],
          coord[0],
        ]);

        return (
          <Polygon
            key={idx}
            positions={positions}
            pathOptions={{
              color: fillColor,
              fillColor: fillColor,
              fillOpacity:
                theme === 'dark' ? 0.65 : 0.5,
              weight: 2,
              dashArray: '3',
            }}
          >
            <Popup>
              <div className="p-1 font-sans">
                <h5 className="font-bold text-xs uppercase text-slate-800 tracking-wide leading-tight">
                  {label}
                </h5>

                <p className="text-[10px] text-slate-400 font-semibold mt-1">
                  Classification:
                  <span className="font-bold text-slate-700 capitalize ml-1">
                    {classType}
                  </span>
                </p>

                <p className="text-[10px] text-slate-400 font-semibold leading-none mt-1">
                  Calculated Area:
                  <span className="font-bold text-slate-700 ml-1">
                    {area}
                  </span>
                </p>
              </div>
            </Popup>
          </Polygon>
        );
      }
    );
  };

  // ==========================================
  // BASE MAP
  // ==========================================

  const baseMapTilesUrl =
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

  // ==========================================
  // DROPDOWN STYLES
  // ==========================================

  const selectStyle = {
    color: '#f1f5f9',
    backgroundColor: '#0f172a',
    WebkitTextFillColor: '#f1f5f9',
    colorScheme: 'dark',
  };

  const optionStyle = {
    color: '#f1f5f9',
    backgroundColor: '#0f172a',
  };

  const placeholderOptionStyle = {
    color: '#94a3b8',
    backgroundColor: '#0f172a',
  };

  // ==========================================
  // UI
  // ==========================================

  return (
    <div className="flex-1 flex flex-col md:flex-row gap-6 relative min-h-[calc(100vh-10rem)]">

      {/* SIDEBAR */}

      <div className="w-full md:w-80 xl:w-96 glass-card rounded-2xl p-5 sm:p-6 shadow-xs flex flex-col justify-between shrink-0 transition-colors duration-300">

        <div className="space-y-5">

          <div>
            <h4 className="text-base font-extrabold text-slate-800 dark:text-slate-200 tracking-tight leading-tight">
              Classification Criteria
            </h4>

            <p className="text-xs text-slate-400 dark:text-slate-500 font-bold mt-1 uppercase tracking-wider">
              Define geographical coordinates and imaging date
            </p>
          </div>

          <hr className="border-slate-100 dark:border-slate-800" />

          <div className="space-y-4">

            {/* STATE */}

            <div>
              <label
                htmlFor="state-select"
                className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5"
              >
                State
              </label>

              <select
                id="state-select"
                value={selectedState}
                onChange={(e) =>
                  setSelectedState(e.target.value)
                }
                style={selectStyle}
                className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-900 text-slate-100 border border-slate-600 hover:border-slate-500 focus:border-green-500 focus:bg-slate-800 focus:text-white rounded-xl outline-none appearance-auto cursor-pointer tech-mono transition-all duration-200"
              >
                <option
                  value=""
                  style={placeholderOptionStyle}
                >
                  Select State
                </option>

                {states.map((st) => (
                  <option
                    key={st.code}
                    value={st.code}
                    style={optionStyle}
                  >
                    {st.name}
                  </option>
                ))}
              </select>
            </div>

            {/* DISTRICT */}

            <div>
              <label
                htmlFor="district-select"
                className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5"
              >
                District
              </label>

              <select
                id="district-select"
                value={selectedDistrict}
                onChange={(e) =>
                  setSelectedDistrict(e.target.value)
                }
                disabled={!selectedState}
                style={selectStyle}
                className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-900 text-slate-100 border border-slate-600 hover:border-slate-500 focus:border-green-500 focus:bg-slate-800 focus:text-white rounded-xl outline-none appearance-auto cursor-pointer disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed tech-mono transition-all duration-200"
              >
                <option
                  value=""
                  style={placeholderOptionStyle}
                >
                  Select District
                </option>

                {districts.map((ds) => (
                  <option
                    key={ds.code}
                    value={ds.code}
                    style={optionStyle}
                  >
                    {ds.name}
                  </option>
                ))}
              </select>
            </div>

            {/* VILLAGE */}

            <div>
              <label
                htmlFor="village-select"
                className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5"
              >
                Village
              </label>

              <select
                id="village-select"
                value={selectedVillage}
                onChange={(e) =>
                  setSelectedVillage(e.target.value)
                }
                disabled={!selectedDistrict}
                style={selectStyle}
                className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-900 text-slate-100 border border-slate-600 hover:border-slate-500 focus:border-green-500 focus:bg-slate-800 focus:text-white rounded-xl outline-none appearance-auto cursor-pointer disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed tech-mono transition-all duration-200"
              >
                <option
                  value=""
                  style={placeholderOptionStyle}
                >
                  Select Village
                </option>

                {villages.map((vl) => (
                  <option
                    key={vl.code}
                    value={vl.code}
                    style={optionStyle}
                  >
                    {vl.name}
                  </option>
                ))}
              </select>
            </div>

            {/* DATE */}

            <div>
              <label
                htmlFor="date-select"
                className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5"
              >
                Imaging Date
              </label>

              <input
                id="date-select"
                type="date"
                value={selectedDate}
                onChange={(e) =>
                  setSelectedDate(e.target.value)
                }
                className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-900 border border-slate-600 focus:border-green-500 focus:bg-slate-800 rounded-xl outline-none text-slate-100 tech-mono"
              />
            </div>

          </div>
        </div>

        {/* ACTION BUTTONS */}

        <div className="grid grid-cols-2 gap-3 mt-6">

          <button
            onClick={handleReset}
            className="w-full border border-slate-600 hover:border-slate-500 text-slate-400 hover:bg-slate-800 py-3 rounded-xl font-bold uppercase tracking-wider text-xs transition-colors cursor-pointer tech-mono"
          >
            Reset Map
          </button>

          <button
            onClick={handleAnalyze}
            disabled={
              isAnalyzing ||
              !selectedState ||
              !selectedDistrict ||
              !selectedVillage ||
              !selectedDate
            }
            className="w-full glow-cyan bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/50 disabled:bg-slate-800 text-cyan-400 py-3 rounded-xl font-bold uppercase tracking-wider text-xs shadow-md hover:shadow-lg transition-all cursor-pointer disabled:cursor-not-allowed flex items-center justify-center gap-1.5 tech-mono"
          >
            {isAnalyzing ? (
              <>
                <svg
                  className="animate-spin h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />

                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c.135 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>

                Processing...
              </>
            ) : (
              'Analyze Imagery'
            )}
          </button>

        </div>
      </div>

      {/* MAIN MAP */}

      <div className="flex-1 glass-card rounded-2xl overflow-hidden shadow-xs flex flex-col relative h-[500px] md:h-auto min-h-[450px] transition-colors duration-300 glow-green">

        {/* LOADING OVERLAY */}

        {isAnalyzing && (
          <div
            className="absolute inset-0 z-[1000] flex items-center justify-center bg-slate-950/85 backdrop-blur-sm p-6"
            style={{ color: '#ffffff' }}
          >
            <div
              className="w-full max-w-md rounded-2xl border-2 border-cyan-400/70 bg-slate-950 p-8 shadow-2xl shadow-cyan-500/20 flex flex-col items-center justify-center"
              style={{ color: '#ffffff' }}
            >

              <div className="relative w-16 h-16 mb-6">
                <div className="absolute inset-0 rounded-full border-4 border-cyan-400/20" />

                <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-cyan-400 border-r-green-400 animate-spin" />

                <div className="absolute inset-2 rounded-full border-2 border-green-400/30 animate-pulse" />
              </div>

              <h3
                className="text-lg sm:text-xl font-extrabold text-center tracking-tight"
                style={{ color: '#ffffff' }}
              >
                AI Land Analysis in Progress
              </h3>

              <p
                className="mt-3 text-sm sm:text-base font-semibold text-center leading-relaxed"
                style={{ color: '#67e8f9' }}
              >
                Model conducting semantic analysis using
                Sentinel-2 satellite imagery...
              </p>

              <div className="mt-5 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />

                <span
                  className="text-xs font-bold uppercase tracking-widest"
                  style={{ color: '#86efac' }}
                >
                  Processing satellite data
                </span>
              </div>

            </div>
          </div>
        )}

        {/* MAP HEADER */}

        <div className="absolute top-4 left-4 z-10 p-3 bg-slate-900/90 backdrop-blur-md rounded-xl border border-slate-600 shadow-md max-w-xs sm:max-w-sm">

          <p className="text-[9px] text-green-400 font-extrabold uppercase tracking-widest leading-none">
            Map Viewport
          </p>

          <h4 className="text-xs font-bold text-white truncate mt-1 leading-normal">
            {selectedVillage && geoMetadata
              ? `${villages.find(
                (v) => v.code === selectedVillage
              )?.name || 'Selected'
              } Village Sector`
              : 'Pan / Zoom Active GIS Layer'}
          </h4>

          <p className="text-[9px] text-slate-300 font-semibold mt-1.5 leading-none">
            {mapCenter[0].toFixed(4)}° N,{' '}
            {mapCenter[1].toFixed(4)}° E
          </p>

        </div>

        {/* MAP */}

        <div className="flex-1 w-full h-full relative z-0">

          <MapContainer
            center={mapCenter}
            zoom={13}
            scrollWheelZoom={true}
            style={{
              width: '100%',
              height: '100%',
            }}
          >
            <ChangeMapView center={mapCenter} />

            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url={baseMapTilesUrl}
            />

            {renderPolygons()}
          </MapContainer>

        </div>

        {/* LEGEND */}

        <MapLegend
          className="absolute bottom-4 right-4 z-10 max-w-[200px]"
        />

        {/* ANALYSIS RESULTS */}

        {analysisResults && (
          <div className="bg-slate-950/95 backdrop-blur-md text-white p-4 sm:p-5 flex flex-wrap items-center gap-4 z-10 border-t-2 border-cyan-400/40 transition-colors duration-300 overflow-visible">

            {/* REPORT ID */}

            <div className="flex items-center gap-3 shrink-0">

              <div className="p-2 rounded-lg bg-green-500/10 text-green-400">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125 1.125 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 013.75 9.375v-4.5zM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5a1.125 1.125 0 001.125 1.125v4.5a1.125 1.125 0 01-1.125 1.125h-4.5a1.125 1.125 0 01-1.125-1.125v-4.5zM13.5 4.875c0-.621.504-1.125 1.125-1.125h4.5a1.125 1.125 0 011.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0113.5 9.375v-4.5zM13.5 16.5a1.5 1.5 0 00-1.5 1.5v2.25a1.5 1.5 0 001.5 1.5h3a1.5 1.5 0 001.5-1.5V18a1.5 1.5 0 00-1.5-1.5h-3z"
                  />
                </svg>
              </div>

              <div>
                <p className="text-[10px] text-slate-300 font-extrabold uppercase tracking-wider">
                  Classification Report
                </p>

                <p className="text-xs font-mono font-bold text-green-400 mt-0.5">
                  {analysisResults.reportId}
                </p>
              </div>

            </div>

            {/* STATS */}

            <div className="w-full flex-1 min-w-0 grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-8">

              {/* TOTAL AREA */}

              <div className="min-w-0">

                <span className="block text-[10px] text-cyan-300 uppercase font-extrabold tracking-wider whitespace-nowrap">
                  Total Area
                </span>

                <span
                  className="block text-sm font-extrabold mt-1 whitespace-nowrap overflow-visible"
                  style={{
                    fontFamily: 'monospace',
                    color: '#ffffff',
                    opacity: 1,
                    visibility: 'visible',
                  }}
                >
                  {analysisResults?.stats?.totalArea ?? 0} Ha
                </span>

              </div>

              {/* MAPPED AREA */}

              <div className="min-w-0">

                <span className="block text-[10px] text-cyan-300 uppercase font-extrabold tracking-wider whitespace-nowrap">
                  Mapped Area
                </span>

                <span
                  className="block text-sm font-extrabold mt-1 whitespace-nowrap overflow-visible"
                  style={{
                    fontFamily: 'monospace',
                    color: '#67e8f9',
                    opacity: 1,
                    visibility: 'visible',
                  }}
                >
                  {analysisResults?.stats?.mappedArea ?? 0} Ha
                </span>

              </div>

              {/* CONFIDENCE */}

              <div className="min-w-0">

                <span className="block text-[10px] text-emerald-300 uppercase font-extrabold tracking-wider whitespace-nowrap">
                  Model Confidence
                </span>

                <span
                  className="block text-sm font-extrabold mt-1 whitespace-nowrap overflow-visible"
                  style={{
                    fontFamily: 'monospace',
                    color: '#6ee7b7',
                    opacity: 1,
                    visibility: 'visible',
                  }}
                >
                  {analysisResults?.stats?.confidence ?? 0}%
                </span>

              </div>

              {/* PREDICTION LATENCY */}

              <div className="min-w-0">

                <span className="block text-[10px] text-cyan-300 uppercase font-extrabold tracking-wider whitespace-nowrap">
                  Prediction Latency
                </span>

                <span
                  className="block text-sm font-extrabold mt-1 whitespace-nowrap overflow-visible"
                  style={{
                    fontFamily: 'monospace',
                    color: '#ffffff',
                    opacity: 1,
                    visibility: 'visible',
                  }}
                >
                  {analysisResults?.stats?.predictionTime ?? 'N/A'}
                </span>

              </div>

            </div>
          </div>
        )}

      </div>

      {/* TOAST */}

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

export default LandMapping;
