'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Zap, FileText, CheckCircle } from 'lucide-react'

interface ProgressLoaderProps {
  isVisible: boolean
  progress: number
  currentStep: string
  onComplete?: () => void
}

const steps = [
  { id: 'parsing', label: 'Parsing your resume', icon: FileText },
  { id: 'analyzing', label: 'Analyzing job requirements', icon: Zap },
  { id: 'optimizing', label: 'Optimizing for ATS', icon: CheckCircle },
  { id: 'generating', label: 'Generating final resume', icon: FileText }
]

export default function ProgressLoader({ isVisible, progress, currentStep, onComplete }: ProgressLoaderProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0)

  useEffect(() => {
    if (!isVisible) return

    const stepIndex = steps.findIndex(step => step.id === currentStep)
    if (stepIndex !== -1) {
      setCurrentStepIndex(stepIndex)
    }
  }, [currentStep, isVisible])

  useEffect(() => {
    if (progress >= 100 && onComplete) {
      setTimeout(onComplete, 1000)
    }
  }, [progress, onComplete])

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl p-8 max-w-md w-full mx-4"
      >
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Zap className="w-8 h-8 text-primary animate-pulse" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Optimizing Your Resume
          </h3>
          <p className="text-gray-600">
            Our AI is working hard to create your perfect resume...
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              className="bg-primary h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-3">
          {steps.map((step, index) => {
            const Icon = step.icon
            const isActive = index === currentStepIndex
            const isCompleted = index < currentStepIndex
            const isPending = index > currentStepIndex

            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`
                  flex items-center p-3 rounded-lg transition-all duration-300
                  ${isActive ? 'bg-primary/10 border border-primary/20' : ''}
                  ${isCompleted ? 'bg-green-50' : ''}
                  ${isPending ? 'bg-gray-50' : ''}
                `}
              >
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center mr-3
                  ${isActive ? 'bg-primary text-white' : ''}
                  ${isCompleted ? 'bg-green-500 text-white' : ''}
                  ${isPending ? 'bg-gray-300 text-gray-500' : ''}
                `}>
                  {isCompleted ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    <Icon className="w-4 h-4" />
                  )}
                </div>
                <div className="flex-1">
                  <p className={`
                    font-medium
                    ${isActive ? 'text-primary' : ''}
                    ${isCompleted ? 'text-green-700' : ''}
                    ${isPending ? 'text-gray-500' : 'text-gray-700'}
                  `}>
                    {step.label}
                  </p>
                  {isActive && (
                    <div className="flex items-center mt-1">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse mr-2"></div>
                      <span className="text-sm text-primary">In progress...</span>
                    </div>
                  )}
                </div>
              </motion.div>
            )
          })}
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            This usually takes 30-60 seconds
          </p>
        </div>
      </motion.div>
    </div>
  )
}
