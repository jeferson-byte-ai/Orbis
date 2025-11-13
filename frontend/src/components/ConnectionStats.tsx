/**
 * Connection Statistics Component
 * Shows real-time connection quality and performance metrics
 */
import React from 'react';
import { Activity, Wifi, Zap, Globe } from 'lucide-react';

interface ConnectionStatsProps {
  isConnected: boolean;
  latency: number;
  bandwidth?: {
    upload: number;
    download: number;
  };
  participants: number;
  sourceLanguage: string;
  targetLanguages: string[];
}

const ConnectionStats: React.FC<ConnectionStatsProps> = ({
  isConnected,
  latency,
  bandwidth,
  participants,
  sourceLanguage,
  targetLanguages
}) => {
  
  // Determine connection quality based on latency
  const getQuality = () => {
    if (!isConnected) return { label: 'Disconnected', color: 'text-red-500', icon: '⚠️' };
    if (latency < 100) return { label: 'Excellent', color: 'text-green-500', icon: '✅' };
    if (latency < 200) return { label: 'Good', color: 'text-blue-500', icon: '👍' };
    if (latency < 300) return { label: 'Fair', color: 'text-yellow-500', icon: '⚡' };
    return { label: 'Poor', color: 'text-red-500', icon: '⚠️' };
  };
  
  const quality = getQuality();
  
  const formatBandwidth = (kbps: number) => {
    if (kbps < 1000) return `${kbps.toFixed(0)} Kbps`;
    return `${(kbps / 1000).toFixed(1)} Mbps`;
  };
  
  return (
    <div className="glass-dark p-4 rounded-xl space-y-3">
      <h3 className="text-white font-semibold text-sm flex items-center gap-2">
        <Activity size={16} className="text-blue-400" />
        Connection Statistics
      </h3>
      
      <div className="space-y-2">
        {/* Connection Quality */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wifi size={14} className={quality.color} />
            <span className="text-gray-300 text-sm">Quality</span>
          </div>
          <span className={`text-sm font-medium ${quality.color}`}>
            {quality.icon} {quality.label}
          </span>
        </div>
        
        {/* Latency */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap size={14} className="text-yellow-400" />
            <span className="text-gray-300 text-sm">Latency</span>
          </div>
          <span className={`text-sm font-mono font-medium ${
            latency < 150 ? 'text-green-400' : 
            latency < 250 ? 'text-yellow-400' : 
            'text-red-400'
          }`}>
            {latency}ms
          </span>
        </div>
        
        {/* Bandwidth */}
        {bandwidth && (
          <>
            <div className="flex items-center justify-between">
              <span className="text-gray-300 text-sm ml-6">↑ Upload</span>
              <span className="text-sm font-mono text-blue-400">
                {formatBandwidth(bandwidth.upload)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300 text-sm ml-6">↓ Download</span>
              <span className="text-sm font-mono text-green-400">
                {formatBandwidth(bandwidth.download)}
              </span>
            </div>
          </>
        )}
        
        {/* Participants */}
        <div className="flex items-center justify-between">
          <span className="text-gray-300 text-sm">👥 Participants</span>
          <span className="text-sm font-medium text-white">
            {participants}
          </span>
        </div>
        
        {/* Languages */}
        <div className="pt-2 border-t border-white/10">
          <div className="flex items-center gap-2 mb-2">
            <Globe size={14} className="text-purple-400" />
            <span className="text-gray-300 text-sm">Languages</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="bg-purple-500/20 text-purple-300 px-2 py-1 rounded">
              🗣️ {sourceLanguage.toUpperCase()}
            </span>
            <span className="text-gray-500">→</span>
            <div className="flex gap-1 flex-wrap">
              {targetLanguages.map(lang => (
                <span key={lang} className="bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                  {lang.toUpperCase()}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Status indicator */}
      <div className="pt-2 border-t border-white/10">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400">Status</span>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`} />
            <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConnectionStats;
