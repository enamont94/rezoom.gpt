'use client'

import { useState } from 'react'
import { Briefcase, Code, Palette, Check } from 'lucide-react'

interface ToneSelectorProps {
  selectedTone: string
  onToneChange: (tone: string) => void
  disabled?: boolean
}

const tones = [
  {
    id: 'professional',
    name: 'Professional',
    description: 'Traditional, corporate style',
    icon: Briefcase,
    color: 'blue'
  },
  {
    id: 'tech',
    name: 'Tech',
    description: 'Modern, technical focus',
    icon: Code,
    color: 'green'
  },
  {
    id: 'creative',
    name: 'Creative',
    description: 'Innovative, artistic approach',
    icon: Palette,
    color: 'purple'
  }
]

export default function ToneSelector({ selectedTone, onToneChange, disabled = false }: ToneSelectorProps) {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-3">
        Resume Tone
      </label>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tones.map((tone) => {
          const Icon = tone.icon
          const isSelected = selectedTone === tone.id
          
          return (
            <button
              key={tone.id}
              onClick={() => !disabled && onToneChange(tone.id)}
              disabled={disabled}
              className={`
                relative p-4 border-2 rounded-lg text-left transition-all duration-200
                ${isSelected 
                  ? `border-${tone.color}-500 bg-${tone.color}-50` 
                  : 'border-gray-200 hover:border-gray-300 bg-white'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:shadow-md'}
              `}
            >
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <Check className="w-5 h-5 text-green-500" />
                </div>
              )}
              
              <div className="flex items-center mb-2">
                <div className={`
                  w-10 h-10 rounded-lg flex items-center justify-center mr-3
                  ${isSelected ? `bg-${tone.color}-100` : 'bg-gray-100'}
                `}>
                  <Icon className={`w-5 h-5 ${isSelected ? `text-${tone.color}-600` : 'text-gray-600'}`} />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{tone.name}</h3>
                  <p className="text-sm text-gray-500">{tone.description}</p>
                </div>
              </div>
            </button>
          )
        })}
      </div>
      
      <div className="mt-3 text-sm text-gray-500">
        Choose the tone that best matches your industry and target role.
      </div>
    </div>
  )
}
