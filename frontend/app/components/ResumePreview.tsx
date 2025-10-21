'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Eye, Download, Mail, Share2, X } from 'lucide-react'

interface ResumePreviewProps {
  resumeData: {
    name: string
    title: string
    summary: string
    experience: Array<{
      title: string
      company: string
      years: string
      description: string
    }>
    skills: string[]
    education: string
  }
  isVisible: boolean
  onClose: () => void
  onDownload: () => void
  onEmail: () => void
}

export default function ResumePreview({ 
  resumeData, 
  isVisible, 
  onClose, 
  onDownload, 
  onEmail 
}: ResumePreviewProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'download'>('preview')

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Your Optimized Resume</h2>
            <p className="text-gray-600">Ready to download and apply!</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'preview'
                ? 'text-primary border-b-2 border-primary'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Eye className="w-4 h-4 inline mr-2" />
            Preview
          </button>
          <button
            onClick={() => setActiveTab('download')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'download'
                ? 'text-primary border-b-2 border-primary'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Download className="w-4 h-4 inline mr-2" />
            Download
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {activeTab === 'preview' ? (
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="bg-white rounded-lg p-8 shadow-sm">
                {/* Header */}
                <div className="text-center mb-8">
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    {resumeData.name}
                  </h1>
                  <h2 className="text-xl text-primary font-semibold">
                    {resumeData.title}
                  </h2>
                </div>

                {/* Summary */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1">
                    Professional Summary
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    {resumeData.summary}
                  </p>
                </div>

                {/* Experience */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b border-gray-200 pb-1">
                    Professional Experience
                  </h3>
                  <div className="space-y-6">
                    {resumeData.experience.map((job, index) => (
                      <div key={index} className="border-l-4 border-primary pl-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-semibold text-gray-900">{job.title}</h4>
                            <p className="text-primary font-medium">{job.company}</p>
                          </div>
                          <span className="text-sm text-gray-500">{job.years}</span>
                        </div>
                        <p className="text-gray-700">{job.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Skills */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1">
                    Key Skills
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {resumeData.skills.map((skill, index) => (
                      <span
                        key={index}
                        className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Education */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1">
                    Education
                  </h3>
                  <p className="text-gray-700">{resumeData.education}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Download className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Your Resume is Ready!
                </h3>
                <p className="text-gray-600">
                  Download your optimized resume or have it sent to your email.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={onDownload}
                  className="flex items-center justify-center p-4 border-2 border-primary rounded-lg hover:bg-primary/5 transition-colors"
                >
                  <Download className="w-5 h-5 text-primary mr-3" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Download PDF</div>
                    <div className="text-sm text-gray-600">Save to your device</div>
                  </div>
                </button>

                <button
                  onClick={onEmail}
                  className="flex items-center justify-center p-4 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Mail className="w-5 h-5 text-gray-600 mr-3" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Send to Email</div>
                    <div className="text-sm text-gray-600">Receive via email</div>
                  </div>
                </button>
              </div>

              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Share2 className="w-5 h-5 text-blue-600 mr-2" />
                  <span className="font-semibold text-blue-900">Share Your Success</span>
                </div>
                <p className="text-sm text-blue-700 mb-3">
                  Share your ATS score on LinkedIn to showcase your optimized resume!
                </p>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                  Share on LinkedIn
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center p-6 border-t border-gray-200 bg-gray-50">
          <div className="text-sm text-gray-500">
            Generated with Rezoom.ai
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              Close
            </button>
            {activeTab === 'preview' && (
              <button
                onClick={onDownload}
                className="btn-primary"
              >
                Download Resume
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  )
}
