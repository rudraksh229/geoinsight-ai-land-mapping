import React, { useEffect, useState } from 'react';
import {
  MapContainer,
  GeoJSON,
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

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

// MAP VIEW CONTROLLER & AUTO-FIT BOUNDS
const ChangeMapView = ({ center, mapData }) => {
  const map = useMap();

  useEffect(() => {
    if (mapData && mapData.features && mapData.features.length > 0) {
      try {
        const geoJsonLayer = L.geoJSON(mapData);
        map.fitBounds(geoJsonLayer.getBounds(), { padding: [30, 30] });
      } catch (err) {
        console.error("Bounds fit error:", err);
      }
    } else if (center && center.length === 2 && center[0] && center[1]) {
      map.setView(center, 13, { animate: true, duration: 1.5 });
    }
  }, [center, mapData, map]);

  return null;
};

const LandMapping = () => {
  const { theme } = useTheme();

  const [geoMetadata, setGeoMetadata] = useState(null);
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [villages, setVillages] = useState([]);

  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedVillage, setSelectedVillage] = useState('');
  const [selectedDate, setSelectedDate] = useState('');

  const [mapCenter, setMapCenter] = useState([18.5913, 73.7386]);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  const showToast = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
  };

  useEffect(() => {
    const fetchGeoMetadata = async () => {
      try {
        const res = await api.get('/geography/metadata');
        setGeoMetadata(res.data);
        setStates(res.data.states || []);
      } catch (err) {
        console.error('Geography metadata error:', err);
        showToast('Failed to load geographic indices.', 'error');
      }
    };

    fetchGeoMetadata();
  }, []);

  useEffect(() => {
    if (selectedState && geoMetadata) {
      setDistricts(geoMetadata.districts?.[selectedState] || []);
      setSelectedDistrict('');
      setVillages([]);
      setSelectedVillage('');
    } else {
      setDistricts([]);
      setVillages([]);
    }
  }, [selectedState, geoMetadata]);

  useEffect(() => {
    if (selectedDistrict && geoMetadata) {
      setVillages(geoMetadata.villages?.[selectedDistrict] || []);
      setSelectedVillage('');
    } else {
      setVillages([]);
    }
  }, [selectedDistrict, geoMetadata]);

  useEffect(() => {
    if (selectedVillage && villages.length > 0) {
      const villageObj = villages.find((v) => v.code === selectedVillage);
      if (villageObj) {
        setMapCenter([villageObj.lat, villageObj.lng]);
        showToast(`Centered map viewport on ${villageObj.name} village.`, 'info');
      }
    }
  }, [selectedVillage, villages]);

  const handleAnalyze = async () => {
    if (!selectedState || !selectedDistrict || !selectedVillage || !selectedDate) {
      showToast('Mandatory criteria missing. Please complete all form inputs.', 'warning');
      return;
    }

    const activeVillage = villages.find((v) => v.code === selectedVillage);
    if (!activeVillage) {
      showToast('Selected village information could not be found.', 'error');
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

      const res = await api.post('/mapping/analyze', payload);
      setAnalysisResults(res.data);
      showToast('AI classification generated successfully!', 'success');
    } catch (err) {
      console.error('Land analysis error:', err);
      const message = err.response?.data?.detail || 'Classification model encountered an operational error.';
      showToast(message, 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setSelectedState('');
    setSelectedDistrict('');
    setSelectedVillage('');
    setSelectedDate('');
    setAnalysisResults(null);
    setMapCenter([18.5913, 73.7386]);
    showToast('Filters and spatial maps reset.', 'info');
  };

  // DYNAMIC GEOJSON STYLING & POPUP BINDING
  const geoJsonStyle = (feature) => {
    const color = feature.properties?.color || '#2ecc71';
    return {
      fillColor: color,
      color: color,
      weight: 2,
      opacity: 0.9,
      fillOpacity: theme === 'dark' ? 0.65 : 0.5,
      dashArray: '3',
    };
  };

  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      const label = feature.properties.label || 'Classification Area';
      const classType = feature.properties.type || 'N/A';
      const area = feature.properties.area || 'N/A';

      layer.bindPopup(`
        <div style="font-family: sans-serif; padding: 4px;">
          <h5 style="font-weight: bold; font-size: 12px; margin: 0; color: #1e293b; text-transform: uppercase;">${label}</h5>
          <p style="font-size: 10px; margin: 4px 0 0 0; color: #64748b;">Classification: <b style="color: #0f172a;">${classType}</b></p>
          <p style="font-size: 10px; margin: 2px 0 0 0; color: #64748b;">Calculated Area: <b style="color: #0f172a;">${area}</b></p>
        </div>
      `);
    }
  };

  const baseMapTilesUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

  const selectStyle = {
    color: '#f1f5f9',
    backgroundColor: '#0f172a',
    WebkitTextFillColor: '#f1f5f9',
    colorScheme: 'dark',
  };

  const optionStyle = { color: '#f1f5f9', backgroundColor: '#0f172a' };
  const placeholderOptionStyle = { color: '#94a3b8', backgroundColor: '#0f172a' };

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
            <div>
              <label htmlFor="state-select" className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5">State</label>
              <select id="state-select" value={selectedState} onChange={(e) => setSelectedState(e.target.value)} style={selectStyle} className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-900 text-slate-100 border border-slate-600 rounded-xl outline-none cursor-pointer tech-mono">
                <option value="" style={placeholderOptionStyle}>Select State</option>
                {states.map((st) => (<option key={st.code} value={st.code} style={optionStyle}>{st.name}</option>))}
              </select>
            </div>
            <div>
              <label htmlFor="district-select" className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5">District</label>
              <select id="district-select" value={selectedDistrict} onChange={(e) => setSelectedDistrict(e.target.value)} disabled={!selectedState} style={selectStyle} className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-900 text-slate-100 border border-slate-600 rounded-xl outline-none cursor-pointer disabled:bg-slate-800 disabled:text-slate-500 tech-mono">
                <option value="" style={placeholderOptionStyle}>Select District</option>
                {districts.map((ds) => (<option key={ds.code} value={ds.code} style={optionStyle}>{ds.name}</option>))}
              </select>
            </div>
            <div>
              <label htmlFor="village-select" className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5">Village</label>
              <select id="village-select" value={selectedVillage} onChange={(e) => setSelectedVillage(e.target.value)} disabled={!selectedDistrict} style={selectStyle} className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-900 text-slate-100 border border-slate-600 rounded-xl outline-none cursor-pointer disabled:bg-slate-800 disabled:text-slate-500 tech-mono">
                <option value="" style={placeholderOptionStyle}>Select Village</option>
                {villages.map((vl) => (<option key={vl.code} value={vl.code} style={optionStyle}>{vl.name}</option>))}
              </select>
            </div>
            <div>
              <label htmlFor="date-select" className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5">Imaging Date</label>
              <input id="date-select" type="date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-900 border border-slate-600 rounded-xl outline-none text-slate-100 tech-mono" />
            </div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 mt-6">
          <button onClick={handleReset} className="w-full border border-slate-600 text-slate-400 py-3 rounded-xl font-bold uppercase tracking-wider text-xs tech-mono">Reset Map</button>
          <button onClick={handleAnalyze} disabled={isAnalyzing || !selectedState || !selectedDistrict || !selectedVillage || !selectedDate} className="w-full bg-cyan-500/20 border border-cyan-500/50 text-cyan-400 py-3 rounded-xl font-bold uppercase tracking-wider text-xs tech-mono flex items-center justify-center gap-1.5">
            {isAnalyzing ? 'Processing...' : 'Analyze Imagery'}
          </button>
        </div>
      </div>

      {/* MAIN MAP */}
      <div className="flex-1 glass-card rounded-2xl overflow-hidden shadow-xs flex flex-col relative h-[500px] md:h-auto min-h-[450px]">
        <div className="flex-1 w-full h-full relative z-0">
          <MapContainer center={mapCenter} zoom={13} scrollWheelZoom={true} style={{ width: '100%', height: '100%' }}>
            <ChangeMapView center={mapCenter} mapData={analysisResults?.mapData} />
            <TileLayer attribution='&copy; OpenStreetMap contributors' url={baseMapTilesUrl} />

            {/* Direct Native GeoJSON Component */}
            {analysisResults?.mapData?.features?.length > 0 && (
              <GeoJSON
                key={JSON.stringify(analysisResults.mapData)}
                data={analysisResults.mapData}
                style={geoJsonStyle}
                onEachFeature={onEachFeature}
              />
            )}
          </MapContainer>
        </div>

        <MapLegend className="absolute bottom-4 right-4 z-10 max-w-[200px]" />

        {analysisResults && (
          <div className="bg-slate-950/95 text-white p-4 sm:p-5 flex flex-wrap items-center gap-4 z-10 border-t-2 border-cyan-400/40">
            <div className="flex items-center gap-3 shrink-0">
              <div>
                <p className="text-[10px] text-slate-300 font-extrabold uppercase">Classification Report</p>
                <p className="text-xs font-mono font-bold text-green-400">{analysisResults.reportId}</p>
              </div>
            </div>
            <div className="w-full flex-1 grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <span className="block text-[10px] text-cyan-300 uppercase font-extrabold">Total Area</span>
                <span className="block text-sm font-bold font-mono text-white">{analysisResults?.stats?.totalArea ?? 0} Ha</span>
              </div>
              <div>
                <span className="block text-[10px] text-cyan-300 uppercase font-extrabold">Mapped Area</span>
                <span className="block text-sm font-bold font-mono text-cyan-400">{analysisResults?.stats?.mappedArea ?? 0} Ha</span>
              </div>
              <div>
                <span className="block text-[10px] text-emerald-300 uppercase font-extrabold">Model Confidence</span>
                <span className="block text-sm font-bold font-mono text-emerald-400">{analysisResults?.stats?.confidence ?? 0}%</span>
              </div>
              <div>
                <span className="block text-[10px] text-cyan-300 uppercase font-extrabold">Prediction Latency</span>
                <span className="block text-sm font-bold font-mono text-white">{analysisResults?.stats?.predictionTime ?? 'N/A'}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {toastMessage && <NotificationToast message={toastMessage} type={toastType} onClose={() => setToastMessage('')} />}
    </div>
  );
};

export default LandMapping;
