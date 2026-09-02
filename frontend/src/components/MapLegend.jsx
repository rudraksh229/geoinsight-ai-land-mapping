import React from 'react';

const MapLegend = ({ className = '' }) => {
  const legendItems = [
    { label: 'Vegetation', colorClass: 'bg-green-500 border-green-600 dark:border-green-400', description: 'Forests, canopy, green cover' },
    { label: 'Agricultural Land', colorClass: 'bg-yellow-500 border-yellow-600 dark:border-yellow-400', description: 'Crops, farms, cultivation' },
    { label: 'Barren Land', colorClass: 'bg-amber-700 border-amber-800 dark:border-amber-600', description: 'Unused, dry, rocky terrains' },
    { label: 'Urban', colorClass: 'bg-slate-500 border-slate-600 dark:border-slate-400', description: 'Settlements, buildings, roads' },
    { label: 'Water Bodies', colorClass: 'bg-blue-500 border-blue-600 dark:border-blue-400', description: 'Lakes, rivers, ponds, canals' }
  ];

  return (
    <div className={`p-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 rounded-xl shadow-md ${className}`}>
      <h5 className="text-[10px] font-bold text-slate-850 dark:text-slate-350 uppercase tracking-widest mb-3 border-b border-slate-100 dark:border-slate-800 pb-1.5">GIS Map Legend</h5>
      <div className="space-y-2.5">
        {legendItems.map((item) => (
          <div key={item.label} className="flex items-start gap-2.5">
            <span className={`w-3.5 h-3.5 rounded-sm border shrink-0 mt-0.5 ${item.colorClass}`} />
            <div>
              <p className="text-xs font-bold text-slate-800 dark:text-slate-205 leading-tight">{item.label}</p>
              <p className="text-[9px] text-slate-400 dark:text-slate-500 font-semibold leading-none mt-0.5">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MapLegend;
