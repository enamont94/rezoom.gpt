'use client'

import { useState } from 'react'
import { FileText, Link, AlertCircle } from 'lucide-react'

interface JobOfferInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
}

export default function JobOfferInput({ value, onChange, placeholder, disabled = false }: JobOfferInputProps) {
  const [isUrl, setIsUrl] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    onChange(newValue)
    
    // Check if it looks like a URL
    const urlPattern = /^https?:\/\/.+/
    setIsUrl(urlPattern.test(newValue.trim()))
  }

  const handlePaste = async (e: React.ClipboardEvent) => {
    const pastedText = e.clipboardData.getData('text')
    
    // If it looks like a URL, try to fetch the content
    if (pastedText.match(/^https?:\/\/.+/)) {
      e.preventDefault()
      onChange(pastedText)
      setIsUrl(true)
      
      // You could add URL fetching logic here
      // For now, we'll just show a message
      console.log('URL detected:', pastedText)
    }
  }

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Job Description
      </label>
      <div className="relative">
        <textarea
          value={value}
          onChange={handleChange}
          onPaste={handlePaste}
          placeholder={placeholder || "Paste the job description here or paste a job posting URL..."}
          disabled={disabled}
          rows={6}
          className={`
            w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all duration-200
            ${disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white'}
            ${isUrl ? 'border-blue-300 bg-blue-50' : 'border-gray-300'}
          `}
        />
        
        {isUrl && (
          <div className="absolute top-3 right-3">
            <Link className="w-5 h-5 text-blue-500" />
          </div>
        )}
      </div>
      
      {isUrl && (
        <div className="mt-2 flex items-center text-sm text-blue-600">
          <AlertCircle className="w-4 h-4 mr-2" />
          URL detected. We'll extract the job description automatically.
        </div>
      )}
      
      <div className="mt-2 flex items-center text-sm text-gray-500">
        <FileText className="w-4 h-4 mr-2" />
        Tip: Copy the entire job posting for best results
      </div>
    </div>
  )
}
