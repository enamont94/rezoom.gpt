'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import UploadZone from '../components/UploadZone'
import JobOfferInput from '../components/JobOfferInput'
import ToneSelector from '../components/ToneSelector'
import ProgressLoader from '../components/ProgressLoader'
import ScoreGauge from '../components/ScoreGauge'
import ResumePreview from '../components/ResumePreview'
import { Zap, FileText, Download, Mail, Share2 } from 'lucide-react'

export default function Dashboard() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [selectedTone, setSelectedTone] = useState('professional')
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('parsing')
  const [showPreview, setShowPreview] = useState(false)
  const [atsScore, setAtsScore] = useState(0)
  const [resumeData, setResumeData] = useState(null)

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file)
    toast.success('Resume uploaded successfully!')
  }, [])

  const handleFileRemove = useCallback(() => {
    setSelectedFile(null)
  }, [])

  const handleGenerateResume = async () => {
    if (!selectedFile || !jobDescription.trim()) {
      toast.error('Please upload a resume and provide a job description')
      return
    }

    setIsProcessing(true)
    setProgress(0)
    setCurrentStep('parsing')

    try {
      // Simulate processing steps
      const steps = [
        { step: 'parsing', progress: 25, delay: 1000 },
        { step: 'analyzing', progress: 50, delay: 1500 },
        { step: 'optimizing', progress: 75, delay: 2000 },
        { step: 'generating', progress: 100, delay: 1000 }
      ]

      for (const { step, progress: stepProgress, delay } of steps) {
        setCurrentStep(step)
        setProgress(stepProgress)
        await new Promise(resolve => setTimeout(resolve, delay))
      }

      // Simulate API call
      const mockResumeData = {
        name: "John Doe",
        title: "Senior Software Engineer",
        summary: "Experienced software engineer with 5+ years of expertise in full-stack development, cloud architecture, and team leadership. Proven track record of delivering scalable solutions and mentoring junior developers.",
        experience: [
          {
            title: "Senior Software Engineer",
            company: "Tech Corp",
            years: "2020 - Present",
            description: "Led development of microservices architecture serving 1M+ users. Mentored 3 junior developers and improved system performance by 40%."
          },
          {
            title: "Software Engineer",
            company: "StartupXYZ",
            years: "2018 - 2020",
            description: "Developed full-stack applications using React, Node.js, and AWS. Collaborated with cross-functional teams to deliver features on time."
          }
        ],
        skills: ["JavaScript", "React", "Node.js", "AWS", "Python", "Docker", "Kubernetes", "PostgreSQL"],
        education: "Bachelor of Science in Computer Science - University of Technology (2018)"
      }

      setResumeData(mockResumeData)
      setAtsScore(87)
      setShowPreview(true)
      toast.success('Resume generated successfully!')

    } catch (error) {
      toast.error('Failed to generate resume. Please try again.')
      console.error('Error generating resume:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleDownload = () => {
    toast.success('Resume downloaded successfully!')
    setShowPreview(false)
  }

  const handleEmail = () => {
    toast.success('Resume sent to your email!')
    setShowPreview(false)
  }

  const handleClosePreview = () => {
    setShowPreview(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary">Rezoom.ai</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome back!</span>
              <button className="text-gray-600 hover:text-primary">
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Create Your Perfect Resume
          </h1>
          <p className="text-xl text-gray-600">
            Upload your resume and paste a job description to get an ATS-optimized resume in seconds.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Inputs */}
          <div className="space-y-6">
            {/* Resume Upload */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-primary" />
                Upload Your Resume
              </h2>
              <UploadZone
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
                selectedFile={selectedFile}
                isProcessing={isProcessing}
              />
            </div>

            {/* Job Description */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-primary" />
                Job Description
              </h2>
              <JobOfferInput
                value={jobDescription}
                onChange={setJobDescription}
                disabled={isProcessing}
              />
            </div>

            {/* Tone Selection */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Choose Your Style
              </h2>
              <ToneSelector
                selectedTone={selectedTone}
                onToneChange={setSelectedTone}
                disabled={isProcessing}
              />
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerateResume}
              disabled={!selectedFile || !jobDescription.trim() || isProcessing}
              className="w-full btn-primary text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                  Generating...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5 mr-2" />
                  Generate My ATS Resume
                </>
              )}
            </button>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            {/* ATS Score */}
            {atsScore > 0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="card p-6"
              >
                <h2 className="text-xl font-semibold text-gray-900 mb-4 text-center">
                  ATS Compatibility Score
                </h2>
                <div className="flex justify-center">
                  <ScoreGauge score={atsScore} size="lg" />
                </div>
              </motion.div>
            )}

            {/* Tips */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                💡 Pro Tips
              </h3>
              <ul className="space-y-3 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  Use specific keywords from the job description
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  Quantify your achievements with numbers
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  Keep formatting simple and clean
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  Use action verbs to start bullet points
                </li>
              </ul>
            </div>

            {/* Recent Activity */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Recent Activity
              </h3>
              <div className="space-y-3">
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  Resume generated for Software Engineer position
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                  ATS score: 87% - Excellent compatibility
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Loader */}
      <ProgressLoader
        isVisible={isProcessing}
        progress={progress}
        currentStep={currentStep}
        onComplete={() => {
          setIsProcessing(false)
          setShowPreview(true)
        }}
      />

      {/* Resume Preview Modal */}
      {showPreview && resumeData && (
        <ResumePreview
          resumeData={resumeData}
          isVisible={showPreview}
          onClose={handleClosePreview}
          onDownload={handleDownload}
          onEmail={handleEmail}
        />
      )}
    </div>
  )
}
