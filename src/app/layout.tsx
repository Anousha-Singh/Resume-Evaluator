// src/app/layout.tsx
import './globals.css'

export const metadata = {
  title: 'Resume Evaluator',
  description: 'AI-powered resume evaluation tool',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  )
}