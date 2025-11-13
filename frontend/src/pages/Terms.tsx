/**
 * Terms of Service Page
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileText, Scale, Shield, Users, AlertTriangle } from 'lucide-react';

const Terms: React.FC = () => {
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
              <FileText size={32} className="text-red-400" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Terms of Service</h1>
              <p className="text-red-400">Last updated: {lastUpdated}</p>
            </div>
          </div>

          <div className="space-y-8 text-gray-300">
            {/* Introduction */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Scale size={24} className="text-red-400" />
                1. Agreement to Terms
              </h2>
              <p className="leading-relaxed mb-4">
                Welcome to Orbis! These Terms of Service ("Terms") govern your access to and use of the Orbis 
                platform, including our website, applications, and services (collectively, the "Service"). By 
                accessing or using the Service, you agree to be bound by these Terms.
              </p>
              <p className="leading-relaxed">
                If you do not agree to these Terms, please do not use our Service. We reserve the right to modify 
                these Terms at any time, and your continued use of the Service constitutes acceptance of any changes.
              </p>
            </section>

            {/* Account Registration */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Users size={24} className="text-red-400" />
                2. Account Registration and Security
              </h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">2.1 Account Creation</h3>
                  <p className="leading-relaxed">
                    To use certain features of the Service, you must create an account. You agree to provide 
                    accurate, current, and complete information during registration and to update such information 
                    to keep it accurate and current.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">2.2 Account Security</h3>
                  <p className="leading-relaxed">
                    You are responsible for maintaining the confidentiality of your account credentials and for all 
                    activities that occur under your account. You must immediately notify us of any unauthorized use 
                    of your account.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">2.3 Age Requirements</h3>
                  <p className="leading-relaxed">
                    You must be at least 13 years old to use the Service. If you are between 13 and 18 years old, 
                    you must have parental or guardian consent to use the Service.
                  </p>
                </div>
              </div>
            </section>

            {/* Use of Service */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Shield size={24} className="text-red-400" />
                3. Acceptable Use
              </h2>
              <p className="leading-relaxed mb-4">You agree NOT to use the Service to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Violate any applicable laws or regulations</li>
                <li>Infringe upon the rights of others, including intellectual property rights</li>
                <li>Transmit harmful, offensive, or inappropriate content</li>
                <li>Harass, threaten, or harm other users</li>
                <li>Attempt to gain unauthorized access to the Service or other users' accounts</li>
                <li>Interfere with or disrupt the Service or servers</li>
                <li>Use automated systems (bots, scrapers) without permission</li>
                <li>Impersonate any person or entity</li>
                <li>Collect or store personal data of other users</li>
              </ul>
            </section>

            {/* Voice Data */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">4. Voice Data and Recordings</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">4.1 Voice Cloning</h3>
                  <p className="leading-relaxed">
                    When you upload voice samples for voice cloning, you grant Orbis a license to process and 
                    store your voice data solely for the purpose of providing the voice cloning feature. You 
                    represent that you have the right to provide such voice data.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">4.2 Meeting Recordings</h3>
                  <p className="leading-relaxed">
                    You are responsible for obtaining consent from all participants before recording meetings. 
                    Orbis is not liable for your failure to obtain proper consent.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">4.3 Data Deletion</h3>
                  <p className="leading-relaxed">
                    You may delete your voice profiles and recordings at any time through your account settings. 
                    Upon deletion, we will remove this data from our active systems within 30 days.
                  </p>
                </div>
              </div>
            </section>

            {/* Intellectual Property */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">5. Intellectual Property</h2>
              <div className="space-y-4">
                <p className="leading-relaxed">
                  The Service and its original content, features, and functionality are owned by Orbis and are 
                  protected by international copyright, trademark, patent, trade secret, and other intellectual 
                  property laws.
                </p>
                <p className="leading-relaxed">
                  You retain ownership of any content you create or upload to the Service. By uploading content, 
                  you grant us a worldwide, non-exclusive, royalty-free license to use, reproduce, and process 
                  such content solely for the purpose of providing the Service to you.
                </p>
              </div>
            </section>

            {/* Disclaimer */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <AlertTriangle size={24} className="text-red-400" />
                6. Disclaimers and Limitations
              </h2>
              <div className="p-6 bg-yellow-500/10 border border-yellow-500/30 rounded-xl space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">6.1 Service "As Is"</h3>
                  <p className="leading-relaxed">
                    THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER 
                    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
                    A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">6.2 Limitation of Liability</h3>
                  <p className="leading-relaxed">
                    TO THE MAXIMUM EXTENT PERMITTED BY LAW, ORBIS SHALL NOT BE LIABLE FOR ANY INDIRECT, 
                    INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, 
                    WHETHER INCURRED DIRECTLY OR INDIRECTLY.
                  </p>
                </div>
              </div>
            </section>

            {/* Termination */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">7. Termination</h2>
              <p className="leading-relaxed mb-4">
                We may terminate or suspend your account and access to the Service immediately, without prior 
                notice or liability, for any reason, including if you breach these Terms.
              </p>
              <p className="leading-relaxed">
                You may terminate your account at any time by deleting it through your account settings. Upon 
                termination, your right to use the Service will immediately cease.
              </p>
            </section>

            {/* Governing Law */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">8. Governing Law</h2>
              <p className="leading-relaxed">
                These Terms shall be governed by and construed in accordance with the laws of the jurisdiction 
                in which Orbis operates, without regard to its conflict of law provisions.
              </p>
            </section>

            {/* Changes to Terms */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">9. Changes to Terms</h2>
              <p className="leading-relaxed">
                We reserve the right to modify or replace these Terms at any time. If a revision is material, 
                we will provide at least 30 days' notice prior to any new terms taking effect. What constitutes 
                a material change will be determined at our sole discretion.
              </p>
            </section>

            {/* Contact */}
            <section className="pt-8 border-t border-white/10">
              <h2 className="text-2xl font-bold text-white mb-4">10. Contact Us</h2>
              <p className="leading-relaxed mb-4">
                If you have any questions about these Terms, please contact us at:
              </p>
              <div className="p-4 bg-white/5 rounded-xl">
                <p className="text-white">Email: <a href="mailto:orbis.ai.app@gmail.com" className="text-red-400 hover:text-red-300">orbis.ai.app@gmail.com</a></p>
                <p className="text-white mt-2">Website: <a href="https://orbis.app" className="text-red-400 hover:text-red-300">https://orbis.app</a></p>
              </div>
            </section>

            {/* Acknowledgment */}
            <section className="pt-8 border-t border-white/10">
              <div className="p-6 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                <p className="text-white font-semibold mb-2">By using Orbis, you acknowledge that:</p>
                <ul className="list-disc list-inside space-y-2 ml-4 text-gray-300">
                  <li>You have read and understood these Terms of Service</li>
                  <li>You agree to be bound by these Terms</li>
                  <li>You meet the age requirements to use the Service</li>
                  <li>You will comply with all applicable laws and regulations</li>
                </ul>
              </div>
            </section>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-8 flex items-center justify-center gap-6 text-gray-400 text-sm">
          <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
          <span>•</span>
          <Link to="/" className="hover:text-white transition-colors">Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default Terms;
