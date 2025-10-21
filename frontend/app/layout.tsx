import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Rezoom.ai - AI Resume Builder that Beats the ATS Filters',
  description: 'Transform your resume with AI to pass ATS filters and land your dream job. Upload your CV, paste a job description, and get an optimized resume instantly.',
  keywords: 'resume builder, ATS optimization, AI resume, job application, career',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  )
}
