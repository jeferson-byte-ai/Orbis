/**
 * LoadingScreen Component
 * Impressive loading screen with animations and progress
 */
import React, { useState, useEffect } from 'react';

interface LoadingScreenProps {
  onComplete?: () => void;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  const loadingSteps = [
    { text: 'Initializing Orbis...', duration: 500 },
    { text: 'Loading AI models...', duration: 800 },
    { text: 'Connecting to servers...', duration: 600 },
    { text: 'Preparing voice cloning...', duration: 700 },
    { text: 'Setting up translation...', duration: 500 },
    { text: 'Optimizing performance...', duration: 400 },
    { text: 'Ready to break language barriers!', duration: 300 }
  ];

  useEffect(() => {
    let currentProgress = 0;
    let stepIndex = 0;
    
    const interval = setInterval(() => {
      if (stepIndex < loadingSteps.length) {
        const step = loadingSteps[stepIndex];
        setCurrentStep(stepIndex);
        
        // Animate progress for this step
        const stepProgress = 100 / loadingSteps.length;
        const targetProgress = (stepIndex + 1) * stepProgress;
        
        const progressInterval = setInterval(() => {
          currentProgress += 1;
          setProgress(Math.min(currentProgress, targetProgress));
          
          if (currentProgress >= targetProgress) {
            clearInterval(progressInterval);
            stepIndex++;
            
            if (stepIndex >= loadingSteps.length) {
              setIsComplete(true);
              setTimeout(() => {
                onComplete?.();
              }, 1000);
            }
          }
        }, step.duration / stepProgress);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div className="fixed inset-0 bg-gradient-to-r from-black via-black via-70% to-red-950/30 flex items-center justify-center z-50 relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 right-20 w-96 h-96 bg-red-400 rounded-full mix-blend-multiply filter blur-3xl opacity-15 animate-blob"></div>
        <div className="absolute bottom-1/4 right-40 w-96 h-96 bg-red-500 rounded-full mix-blend-multiply filter blur-3xl opacity-12 animate-blob animation-delay-2000"></div>
      </div>

      {/* Main content */}
      <div className="relative z-10 text-center">
        {/* Logo */}
        <div className="mb-8">
          <div className="w-24 h-24 mx-auto bg-gradient-to-br from-red-500 to-red-700 rounded-3xl flex items-center justify-center shadow-2xl animate-pulse">
            <img src="/logo.png" alt="Orbis" className="w-16 h-16 rounded-3xl" />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl md:text-6xl font-bold text-white mb-4 animate-fade-in">
          Orbis
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-300 mb-12 animate-fade-in-delay">
          Talk Without Borders
        </p>

        {/* Progress bar */}
        <div className="w-80 mx-auto mb-8">
          <div className="bg-white/10 rounded-full h-2 overflow-hidden border border-white/10">
            <div 
              className="h-full bg-gradient-to-r from-red-500 to-red-700 rounded-full transition-all duration-300 ease-out shadow-lg"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="text-sm text-gray-300 mt-2">
            {Math.round(progress)}%
          </div>
        </div>

        {/* Loading step */}
        <div className="text-lg text-white mb-8 min-h-[2rem] flex items-center justify-center">
          <span className="animate-fade-in">
            {loadingSteps[currentStep]?.text || ''}
          </span>
        </div>

        {/* Features preview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
          <div className="glass-dark rounded-lg p-4 border border-white/10">
            <div className="text-2xl mb-2">🎙️</div>
            <div className="text-sm text-gray-300">Voice Cloning</div>
          </div>
          <div className="glass-dark rounded-lg p-4 border border-white/10">
            <div className="text-2xl mb-2">🌐</div>
            <div className="text-sm text-gray-300">Real-time Translation</div>
          </div>
          <div className="glass-dark rounded-lg p-4 border border-white/10">
            <div className="text-2xl mb-2">⚡</div>
            <div className="text-sm text-gray-300">Ultra-low Latency</div>
          </div>
        </div>

        {/* Completion animation */}
        {isComplete && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-6xl animate-bounce">✨</div>
          </div>
        )}
      </div>

      {/* Custom animations */}
      <style>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-blob {
          animation: blob 7s infinite;
        }
        
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        
        .animate-fade-in {
          animation: fade-in 0.6s ease-out;
        }
        
        .animate-fade-in-delay {
          animation: fade-in 0.6s ease-out 0.3s both;
        }
      `}</style>
    </div>
  );
};

export default LoadingScreen;

