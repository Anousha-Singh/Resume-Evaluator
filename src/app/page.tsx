"use client"
import React, { useState } from 'react';
import { Upload, FileText, Briefcase, AlertCircle, CheckCircle, TrendingUp, UserCheck,Settings } from 'lucide-react';

interface EvaluationResult {
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  skill_match: Record<string, string>;
  experience_match: number;
  education_match: number;
  detailed_analysis: string;
  fit_assessment: Record<string, string>;
}

const ResumeEvaluator = () => {
  const [jobDescription, setJobDescription] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setResumeFile(file);
        setError(null);
      } else {
        setError('Please upload a PDF file only');
        setResumeFile(null);
      }
    }
  };

  const handleEvaluate = async () => {
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }

    if (!resumeFile) {
      setError('Please upload a resume PDF file');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('job_description', jobDescription);
      formData.append('resume_file', resumeFile);

      const response = await fetch('http://localhost:8000/evaluate-resume', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: EvaluationResult = await response.json();
      setEvaluation(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during evaluation');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Resume Evaluator
          </h1>
          <p className="text-lg text-gray-600">
            Upload your resume and job description to get AI-powered evaluation
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Job Description Input */}
            <div>
              <label className="flex items-center text-lg font-semibold text-gray-700 mb-3">
                <Briefcase className="w-5 h-5 mr-2" />
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here..."
                className="w-full h-40 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
            </div>

            {/* Resume Upload */}
            <div>
              <label className="flex items-center text-lg font-semibold text-gray-700 mb-3">
                <FileText className="w-5 h-5 mr-2" />
                Resume Upload
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="resume-upload"
                />
                <label htmlFor="resume-upload" className="cursor-pointer">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">
                    {resumeFile ? resumeFile.name : 'Click to upload PDF resume'}
                  </p>
                </label>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              {error}
            </div>
          )}

          {/* Evaluate Button */}
          <div className="mt-6 text-center">
            <button
              onClick={handleEvaluate}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-8 rounded-lg transition-colors flex items-center mx-auto"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                  Evaluating...
                </>
              ) : (
                <>
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Evaluate Resume
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Section */}
        {evaluation && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Evaluation Results</h2>

            {/* Overall Score */}
            <div className={`${getScoreBg(evaluation.overall_score)} rounded-lg p-6 mb-6`}>
              <div className="text-center">
                <div className={`text-4xl font-bold ${getScoreColor(evaluation.overall_score)}`}>
                  {evaluation.overall_score}%
                </div>
                <div className="text-gray-600 text-lg">Overall Match Score</div>
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-700 mb-2">Experience Match</h3>
                <div className={`text-2xl font-bold ${getScoreColor(evaluation.experience_match)}`}>
                  {evaluation.experience_match}%
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-700 mb-2">Education Match</h3>
                <div className={`text-2xl font-bold ${getScoreColor(evaluation.education_match)}`}>
                  {evaluation.education_match}%
                </div>
              </div>
            </div>

            {/* Detailed Analysis */}
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Detailed Analysis</h3>
              <p className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">
                {evaluation.detailed_analysis}
              </p>
            </div>

            {/* Strengths and Weaknesses */}
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="text-xl font-semibold text-green-700 mb-3 flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  Strengths
                </h3>
                <ul className="space-y-2">
                  {evaluation.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      <span className="text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-red-700 mb-3 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  Areas for Improvement
                </h3>
                <ul className="space-y-2">
                  {evaluation.weaknesses.map((weakness, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      <span className="text-gray-700">{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Recommendations */}
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-blue-700 mb-3">Recommendations</h3>
              <ul className="space-y-2">
                {evaluation.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="mt-6 mb-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-2 flex items-center">
                <UserCheck className="w-5 h-5 mr-2" />
                Fit Assessment
              </h3>
              <ul className="space-y-2 text-gray-700">
                {Object.entries(evaluation.fit_assessment).map(([key, value]) => (
                  <li key={key} className="flex items-start">
                    <Settings className="w-4 h-4 mt-1 mr-2 text-blue-500" />
                    <span>
                      <strong className="capitalize">{key.replace(/_/g, " ")}:</strong>{" "}
                      {value}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Skill Match */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Skill Match Analysis</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid md:grid-cols-2 gap-4">
                  {Object.entries(evaluation.skill_match).map(([skill, match]) => (
                    <div key={skill} className="flex justify-between items-center">
                      <span className="text-gray-700">{skill}</span>
                      <span className="font-semibold text-blue-600">{match}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeEvaluator;