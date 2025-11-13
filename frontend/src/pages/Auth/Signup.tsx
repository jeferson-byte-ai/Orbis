/**
 * Signup Page - Enterprise grade registration
 */
import React, { useState } from 'react';
import { Mail, Lock, User, Eye, EyeOff, AlertCircle, Loader, ArrowRight, Check } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';

// Feature flag - Set to true to enable OAuth signup
const ENABLE_OAUTH = false;

interface SignupProps {
  onSignup: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
}

const Signup: React.FC<SignupProps> = ({ onSignup }) => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const navigate = useNavigate();

  const validatePassword = (pass: string) => {
    const minLength = pass.length >= 8;
    const hasUpperCase = /[A-Z]/.test(pass);
    const hasLowerCase = /[a-z]/.test(pass);
    const hasNumbers = /\d/.test(pass);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(pass);

    return {
      isValid: minLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar,
      requirements: {
        minLength,
        hasUpperCase,
        hasLowerCase,
        hasNumbers,
        hasSpecialChar
      }
    };
  };

  const passwordValidation = validatePassword(password);
  const passwordsMatch = password === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!acceptedTerms) {
      setError('Please accept the Terms of Service and Privacy Policy');
      return;
    }

    if (!passwordValidation.isValid) {
      setError('Password does not meet requirements');
      return;
    }

    if (!passwordsMatch) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await onSignup(email, username, password, fullName);
      // Redirect to home page after successful signup
      window.location.href = '/';
    } catch (err: any) {
      setError(err.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-950 to-zinc-950 flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.03),transparent_50%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem]" />
      <div className="absolute top-1/4 right-20 w-96 h-96 bg-white/5 rounded-full filter blur-3xl animate-float" />
      <div className="absolute bottom-1/4 left-20 w-96 h-96 bg-white/5 rounded-full filter blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      
      <div className="max-w-md w-full relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center mb-4">
            <img src="/logo.png" alt="Orbis" className="w-20 h-20 rounded-3xl shadow-[0_0_40px_rgba(0,0,0,0.5)]" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Join Orbis</h1>
          <p className="text-gray-500">Create your account to get started</p>
        </div>

        {/* Signup Form */}
        <div className="bg-black/40 backdrop-blur-xl rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.4)] p-8 border border-white/10 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] via-transparent to-transparent pointer-events-none" />
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3">
              <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Full Name (Optional)
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-black/60 border border-white/10 text-white pl-11 pr-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 placeholder-gray-600 hover:border-white/20 transition-all"
                  placeholder="John Doe"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-black/60 border border-white/10 text-white pl-11 pr-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 placeholder-gray-600 hover:border-white/20 transition-all"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value.replace(/[^a-zA-Z0-9_-]/g, ''))}
                  className="w-full bg-black/60 border border-white/10 text-white pl-11 pr-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 placeholder-gray-600 hover:border-white/20 transition-all"
                  placeholder="username"
                  minLength={3}
                  maxLength={20}
                  required
                />
              </div>
              <p className="mt-1 text-xs text-gray-400">
                Letters, numbers, underscores, and hyphens only
              </p>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-black/60 border border-white/10 text-white pl-11 pr-12 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 placeholder-gray-600 hover:border-white/20 transition-all"
                  placeholder="••••••••"
                  minLength={8}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>

              {/* Password Requirements */}
              <div className="mt-2 space-y-1">
                <div className="flex items-center text-xs">
                  <Check className={`mr-2 ${password.length >= 8 ? 'text-green-500' : 'text-gray-500'}`} size={14} />
                  <span className={password.length >= 8 ? 'text-green-500' : 'text-gray-400'}>At least 8 characters</span>
                </div>
                <div className="flex items-center text-xs">
                  <Check className={`mr-2 ${/[A-Z]/.test(password) ? 'text-green-500' : 'text-gray-500'}`} size={14} />
                  <span className={/[A-Z]/.test(password) ? 'text-green-500' : 'text-gray-400'}>Uppercase letter</span>
                </div>
                <div className="flex items-center text-xs">
                  <Check className={`mr-2 ${/[a-z]/.test(password) ? 'text-green-500' : 'text-gray-500'}`} size={14} />
                  <span className={/[a-z]/.test(password) ? 'text-green-500' : 'text-gray-400'}>Lowercase letter</span>
                </div>
                <div className="flex items-center text-xs">
                  <Check className={`mr-2 ${/\d/.test(password) ? 'text-green-500' : 'text-gray-500'}`} size={14} />
                  <span className={/\d/.test(password) ? 'text-green-500' : 'text-gray-400'}>Number</span>
                </div>
                <div className="flex items-center text-xs">
                  <Check className={`mr-2 ${/[!@#$%^&*(),.?":{}|<>]/.test(password) ? 'text-green-500' : 'text-gray-500'}`} size={14} />
                  <span className={/[!@#$%^&*(),.?":{}|<>]/.test(password) ? 'text-green-500' : 'text-gray-400'}>Special character</span>
                </div>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`w-full bg-black/60 border border-white/10 text-white pl-11 pr-12 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 placeholder-gray-600 hover:border-white/20 transition-all ${!passwordsMatch && confirmPassword ? 'border-red-500' : ''}`}
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {!passwordsMatch && confirmPassword && (
                <p className="mt-1 text-xs text-gray-400">Passwords do not match</p>
              )}
            </div>

            {/* Terms */}
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={acceptedTerms}
                onChange={(e) => setAcceptedTerms(e.target.checked)}
                className="mt-1 rounded bg-white/5 border-white/20 text-red-500 focus:ring-red-500/50"
              />
              <label className="text-sm text-gray-300">
                I agree to the{' '}
                <Link to="/terms" className="text-red-400 hover:text-red-300">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-red-400 hover:text-red-300">
                  Privacy Policy
                </Link>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !acceptedTerms || !passwordValidation.isValid || !passwordsMatch}
              className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 disabled:from-gray-800 disabled:to-gray-900 text-white py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 shadow-[0_0_40px_rgba(220,38,38,0.3)] hover:shadow-[0_0_60px_rgba(220,38,38,0.5)] border border-red-500/20"
            >
              {loading ? (
                <>
                  <Loader className="animate-spin" size={20} />
                  Creating account...
                </>
              ) : (
                <>
                  Create account
                  <ArrowRight size={20} />
                </>
              )}
            </button>
          </form>

          {/* Sign in link */}
          <p className="mt-6 text-center text-gray-400 text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-red-400 hover:text-red-300 font-semibold">
              Sign in
            </Link>
          </p>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-gray-500 text-sm">
          © 2025 Orbis. All rights reserved.
        </p>
      </div>
    </div>
  );
};

export default Signup;