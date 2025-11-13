/**
 * Privacy Policy Page
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Shield, Lock, Eye, Database, UserCheck, Globe, Download, Trash2 } from 'lucide-react';

const Privacy: React.FC = () => {
  const lastUpdated = "November 11, 2025";

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-950 to-zinc-950 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.03),transparent_50%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem]" />
      {/* Header */}
      <header className="bg-black/40 backdrop-blur-xl border-b border-white/10 sticky top-0 z-50 relative">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 text-white hover:text-gray-300 transition-colors">
            <ArrowLeft size={20} />
            <span>Back to Home</span>
          </Link>
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="Orbis" className="w-10 h-10 rounded-2xl" />
            <h1 className="text-white text-xl font-bold">Orbis</h1>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-black/40 backdrop-blur-xl rounded-2xl p-8 md:p-12 border border-white/10 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] via-transparent to-transparent pointer-events-none" />
          {/* Title */}
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-red-500/20 rounded-xl">
              <Shield size={32} className="text-red-400" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Privacy Policy</h1>
              <p className="text-red-400">Last updated: {lastUpdated}</p>
            </div>
          </div>

          <div className="space-y-8 text-gray-300">
            {/* Introduction */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">Introduction</h2>
              <p className="leading-relaxed mb-4">
                At Orbis, we take your privacy seriously. This Privacy Policy explains how we collect, use, 
                disclose, and safeguard your information when you use our multilingual video conferencing platform.
              </p>
              <p className="leading-relaxed">
                By using Orbis, you agree to the collection and use of information in accordance with this policy. 
                If you do not agree with our policies and practices, please do not use our Service.
              </p>
            </section>

            {/* Information We Collect */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Database size={24} className="text-red-400" />
                1. Information We Collect
              </h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">1.1 Information You Provide</h3>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li><strong>Account Information:</strong> Email address, username, password, full name (optional)</li>
                    <li><strong>Profile Information:</strong> Bio, company, job title, avatar image</li>
                    <li><strong>Voice Data:</strong> Audio recordings you upload for voice cloning</li>
                    <li><strong>Meeting Content:</strong> Audio, video, chat messages, and transcripts from meetings</li>
                    <li><strong>Preferences:</strong> Language settings, theme preferences, notification settings</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">1.2 Information Collected Automatically</h3>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li><strong>Usage Data:</strong> Meeting duration, features used, timestamps</li>
                    <li><strong>Device Information:</strong> Browser type, operating system, IP address</li>
                    <li><strong>Performance Data:</strong> Connection quality, latency, error logs</li>
                    <li><strong>Cookies:</strong> We use cookies to maintain your session and preferences</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">1.3 Information from Third Parties</h3>
                  <p className="leading-relaxed">
                    If you sign up using OAuth (Google), we receive basic profile information such as your name 
                    and email address from these providers.
                  </p>
                </div>
              </div>
            </section>

            {/* How We Use Your Information */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Eye size={24} className="text-red-400" />
                2. How We Use Your Information
              </h2>
              
              <p className="leading-relaxed mb-4">We use the information we collect to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Provide, maintain, and improve our services</li>
                <li>Process voice cloning and real-time translation</li>
                <li>Enable communication between meeting participants</li>
                <li>Personalize your experience and remember your preferences</li>
                <li>Send you important updates about the service</li>
                <li>Respond to your inquiries and provide customer support</li>
                <li>Monitor and analyze usage patterns to improve performance</li>
                <li>Detect and prevent fraud, abuse, and security issues</li>
                <li>Comply with legal obligations</li>
              </ul>

              <div className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-xl">
                <p className="text-green-300">
                  <strong>Important:</strong> We do NOT sell your personal information to third parties. 
                  We do NOT use your voice data for any purpose other than providing you with voice cloning features.
                </p>
              </div>
            </section>

            {/* Voice Data Processing */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Lock size={24} className="text-red-400" />
                3. Voice Data and AI Processing
              </h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">3.1 Voice Cloning</h3>
                  <p className="leading-relaxed mb-2">
                    When you upload audio samples for voice cloning:
                  </p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>Your voice data is processed using AI models (Coqui TTS) to create your voice profile</li>
                    <li>Voice data is stored securely and encrypted at rest</li>
                    <li>Only you can access and use your cloned voice</li>
                    <li>You can delete your voice profile at any time</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">3.2 Real-Time Translation</h3>
                  <p className="leading-relaxed mb-2">
                    During meetings:
                  </p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>Audio is transcribed using Whisper AI for speech-to-text</li>
                    <li>Text is translated using NLLB (No Language Left Behind) models</li>
                    <li>Translated text is converted back to speech using your voice profile</li>
                    <li>Processing happens in real-time and data is not permanently stored unless you record the meeting</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Data Sharing */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Globe size={24} className="text-red-400" />
                4. How We Share Your Information
              </h2>
              
              <p className="leading-relaxed mb-4">
                We may share your information only in the following circumstances:
              </p>

              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">4.1 With Your Consent</h3>
                  <p className="leading-relaxed">
                    We share your information when you explicitly consent, such as when you invite others to a meeting.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">4.2 Service Providers</h3>
                  <p className="leading-relaxed">
                    We may share information with third-party service providers who help us operate our service 
                    (e.g., cloud hosting, email services). These providers are bound by confidentiality agreements.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">4.3 Legal Requirements</h3>
                  <p className="leading-relaxed">
                    We may disclose your information if required by law, court order, or to protect the rights, 
                    property, or safety of Orbis, our users, or the public.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">4.4 Business Transfers</h3>
                  <p className="leading-relaxed">
                    In the event of a merger, acquisition, or sale of assets, your information may be transferred. 
                    We will notify you before your information becomes subject to a different privacy policy.
                  </p>
                </div>
              </div>
            </section>

            {/* Data Security */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Lock size={24} className="text-red-400" />
                5. Data Security
              </h2>
              
              <p className="leading-relaxed mb-4">
                We implement industry-standard security measures to protect your information:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Encryption:</strong> Data is encrypted in transit (TLS/SSL) and at rest</li>
                <li><strong>Access Controls:</strong> Strict access controls and authentication measures</li>
                <li><strong>Secure Storage:</strong> Data stored in secure, access-controlled data centers</li>
                <li><strong>Regular Audits:</strong> Security practices are regularly reviewed and updated</li>
                <li><strong>Password Protection:</strong> Passwords are hashed using bcrypt</li>
              </ul>

              <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl">
                <p className="text-yellow-300">
                  <strong>Note:</strong> While we strive to protect your information, no method of transmission 
                  over the internet or electronic storage is 100% secure. We cannot guarantee absolute security.
                </p>
              </div>
            </section>

            {/* Data Retention */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">6. Data Retention</h2>
              
              <p className="leading-relaxed mb-4">We retain your information for as long as necessary to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Provide you with our services</li>
                <li>Comply with legal obligations</li>
                <li>Resolve disputes and enforce agreements</li>
              </ul>

              <p className="leading-relaxed mt-4">
                <strong>Deletion:</strong> When you delete your account, we remove your personal information 
                within 30 days. Some information may be retained in backups for up to 90 days for disaster recovery.
              </p>
            </section>

            {/* Your Rights */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <UserCheck size={24} className="text-red-400" />
                7. Your Privacy Rights
              </h2>
              
              <p className="leading-relaxed mb-4">You have the following rights regarding your data:</p>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-white/5 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="text-red-400" size={20} />
                    <h3 className="font-semibold text-white">Access</h3>
                  </div>
                  <p className="text-sm">Request a copy of your personal data</p>
                </div>

                <div className="p-4 bg-white/5 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <Download className="text-red-400" size={20} />
                    <h3 className="font-semibold text-white">Export</h3>
                  </div>
                  <p className="text-sm">Download your data in a portable format</p>
                </div>

                <div className="p-4 bg-white/5 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <Lock className="text-red-400" size={20} />
                    <h3 className="font-semibold text-white">Correction</h3>
                  </div>
                  <p className="text-sm">Update or correct inaccurate information</p>
                </div>

                <div className="p-4 bg-white/5 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <Trash2 className="text-red-400" size={20} />
                    <h3 className="font-semibold text-white">Deletion</h3>
                  </div>
                  <p className="text-sm">Request deletion of your personal data</p>
                </div>
              </div>

              <p className="leading-relaxed mt-4">
                To exercise these rights, visit your account settings or contact us at{' '}
                <a href="mailto:orbis.ai.app@gmail.com" className="text-red-400 hover:text-red-300">orbis.ai.app@gmail.com</a>
              </p>
            </section>

            {/* Cookies */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">8. Cookies and Tracking</h2>
              
              <p className="leading-relaxed mb-4">
                We use cookies and similar tracking technologies to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Keep you signed in</li>
                <li>Remember your preferences</li>
                <li>Analyze how you use our service</li>
                <li>Improve user experience</li>
              </ul>

              <p className="leading-relaxed mt-4">
                You can control cookies through your browser settings. Note that disabling cookies may affect 
                the functionality of our service.
              </p>
            </section>

            {/* Children's Privacy */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">9. Children's Privacy</h2>
              
              <p className="leading-relaxed">
                Our service is not intended for children under 13. We do not knowingly collect personal information 
                from children under 13. If you are a parent or guardian and believe your child has provided us with 
                personal information, please contact us immediately.
              </p>
            </section>

            {/* International Users */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">10. International Data Transfers</h2>
              
              <p className="leading-relaxed">
                Your information may be transferred to and processed in countries other than your country of residence. 
                These countries may have different data protection laws. By using our service, you consent to the 
                transfer of your information to these countries.
              </p>
            </section>

            {/* Changes to Policy */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">11. Changes to This Privacy Policy</h2>
              
              <p className="leading-relaxed">
                We may update this Privacy Policy from time to time. We will notify you of any changes by posting 
                the new Privacy Policy on this page and updating the "Last updated" date. For material changes, 
                we will provide more prominent notice (such as email notification).
              </p>
            </section>

            {/* Contact */}
            <section className="pt-8 border-t border-white/10">
              <h2 className="text-2xl font-bold text-white mb-4">12. Contact Us</h2>
              <p className="leading-relaxed mb-4">
                If you have questions or concerns about this Privacy Policy, please contact us:
              </p>
              <div className="p-4 bg-white/5 rounded-xl space-y-2">
                <p className="text-white">
                  <strong>Email:</strong>{' '}
                  <a href="mailto:orbis.ai.app@gmail.com" className="text-red-400 hover:text-red-300">orbis.ai.app@gmail.com</a>
                </p>
                <p className="text-white">
                  <strong>Website:</strong>{' '}
                  <a href="https://orbis.app" className="text-red-400 hover:text-red-300">https://orbis.app</a>
                </p>
              </div>
            </section>

            {/* Acknowledgment */}
            <section className="pt-8 border-t border-white/10">
              <div className="p-6 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                <p className="text-white font-semibold mb-2">Your Privacy Matters</p>
                <p className="text-gray-300 leading-relaxed">
                  We are committed to protecting your privacy and being transparent about how we handle your data. 
                  If you have any questions or concerns, please don't hesitate to reach out to us.
                </p>
              </div>
            </section>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-8 flex items-center justify-center gap-6 text-gray-400 text-sm">
          <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
          <span>•</span>
          <Link to="/" className="hover:text-white transition-colors">Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default Privacy;
