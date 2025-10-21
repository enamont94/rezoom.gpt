'use client'

import { motion } from 'framer-motion'
import { TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react'

interface ScoreGaugeProps {
  score: number
  maxScore?: number
  size?: 'sm' | 'md' | 'lg'
  showDetails?: boolean
}

export default function ScoreGauge({ score, maxScore = 100, size = 'md', showDetails = true }: ScoreGaugeProps) {
  const percentage = (score / maxScore) * 100
  const circumference = 2 * Math.PI * 45 // radius = 45
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500'
    if (score >= 60) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-50'
    if (score >= 60) return 'bg-yellow-50'
    return 'bg-red-50'
  }

  const getScoreIcon = (score: number) => {
    if (score >= 80) return CheckCircle
    if (score >= 60) return TrendingUp
    return AlertTriangle
  }

  const getScoreMessage = (score: number) => {
    if (score >= 80) return 'Excellent ATS compatibility!'
    if (score >= 60) return 'Good compatibility, minor improvements needed'
    return 'Needs optimization for better ATS performance'
  }

  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-32 h-32',
    lg: 'w-40 h-40'
  }

  const Icon = getScoreIcon(score)

  return (
    <div className={`${getScoreBgColor(score)} rounded-xl p-6 ${sizeClasses[size]}`}>
      <div className="flex flex-col items-center">
        <div className="relative">
          <svg className={`${sizeClasses[size]} transform -rotate-90`} viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-gray-200"
            />
            {/* Progress circle */}
            <motion.circle
              cx="50"
              cy="50"
              r="45"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              className={getScoreColor(score)}
              strokeDasharray={strokeDasharray}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1, ease: "easeInOut" }}
            />
          </svg>
          
          {/* Score text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
                className={`text-2xl font-bold ${getScoreColor(score)}`}
              >
                {score}
              </motion.div>
              <div className="text-xs text-gray-500">/ {maxScore}</div>
            </div>
          </div>
        </div>

        {showDetails && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="mt-4 text-center"
          >
            <div className="flex items-center justify-center mb-2">
              <Icon className={`w-5 h-5 ${getScoreColor(score)} mr-2`} />
              <span className={`font-medium ${getScoreColor(score)}`}>
                ATS Score
              </span>
            </div>
            <p className="text-sm text-gray-600">
              {getScoreMessage(score)}
            </p>
          </motion.div>
        )}
      </div>
    </div>
  )
}
