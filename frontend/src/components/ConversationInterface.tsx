import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Grid,
  TextField,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider,
  Paper
} from '@mui/material';
import {
  Mic,
  MicOff,
  Stop,
  PlayArrow,
  Pause,
  Assessment,
  TrendingUp,
  School
} from '@mui/icons-material';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Types
interface AnalysisResult {
  conversation_id: string;
  overall_score: number;
  grammar_score: number;
  vocabulary_score: number;
  fluency_score: number;
  pronunciation_score: number;
  comprehension_score: number;
  proficiency_level: string;
  strengths: string[];
  areas_for_improvement: string[];
  recommendations: string[];
  detailed_feedback: any;
  grammar_errors: any[];
  vocabulary_analysis: any[];
}

interface Conversation {
  id: string;
  title: string;
  description?: string;
  topic?: string;
  difficulty_level: string;
  language: string;
  status: string;
  created_at: string;
  transcript?: string;
}

// Main Conversation Interface Component
const ConversationInterface: React.FC = () => {
  // State management
  const [isRecording, setIsRecording] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [transcript, setTranscript] = useState('');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize authentication
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      setAuthToken(token);
    } else {
      // For demo purposes, create a mock token
      const mockToken = 'demo_token_' + Date.now();
      localStorage.setItem('auth_token', mockToken);
      setAuthToken(mockToken);
    }
  }, []);

  // Create new conversation
  const createConversation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          title: 'Practice Conversation',
          description: 'AI-powered conversation practice',
          topic: 'General Discussion',
          difficulty_level: 'B1',
          language: 'en'
        })
      });

      if (response.ok) {
        const newConversation = await response.json();
        setConversation(newConversation);
        setError(null);
      } else {
        throw new Error('Failed to create conversation');
      }
    } catch (err) {
      setError('Failed to create conversation. Using demo mode.');
      // Create mock conversation for demo
      setConversation({
        id: 'demo_' + Date.now(),
        title: 'Demo Conversation',
        description: 'Demo conversation for testing',
        topic: 'General Discussion',
        difficulty_level: 'B1',
        language: 'en',
        status: 'draft',
        created_at: new Date().toISOString()
      });
    }
  };

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        processAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err) {
      setError('Failed to access microphone. Please check permissions.');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  // Process audio (mock implementation)
  const processAudio = async (audioBlob: Blob) => {
    setIsAnalyzing(true);
    
    // Mock transcript for demo
    setTimeout(() => {
      setTranscript("Hello, I'm practicing my English conversation skills. I enjoy learning new languages and meeting people from different cultures. Today I want to discuss the importance of education and how it shapes our future. What do you think about the role of technology in modern education?");
      setIsAnalyzing(false);
    }, 2000);
  };

  // Analyze conversation
  const analyzeConversation = async () => {
    if (!conversation || !transcript) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('transcript', transcript);
      formData.append('context', 'General conversation practice');
      formData.append('audio_duration', recordingTime.toString());

      const response = await fetch(
        `${API_BASE_URL}/api/conversations/${conversation.id}/analyze`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`
          },
          body: formData
        }
      );

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
        setShowAnalysis(true);
      } else {
        throw new Error('Analysis failed');
      }
    } catch (err) {
      setError('Analysis failed. Using demo results.');
      // Mock analysis result for demo
      setAnalysisResult({
        conversation_id: conversation.id,
        overall_score: 78.5,
        grammar_score: 20,
        vocabulary_score: 16,
        fluency_score: 15,
        pronunciation_score: 12,
        comprehension_score: 15.5,
        proficiency_level: 'B2',
        strengths: [
          'Good vocabulary range',
          'Clear sentence structure',
          'Appropriate topic discussion'
        ],
        areas_for_improvement: [
          'Pronunciation accuracy',
          'Speaking pace',
          'Complex grammar structures'
        ],
        recommendations: [
          'Practice pronunciation exercises',
          'Work on speaking fluency',
          'Study advanced grammar patterns'
        ],
        detailed_feedback: {
          grammar_notes: 'Good basic grammar usage with minor errors',
          vocabulary_notes: 'Appropriate word choice for the level',
          fluency_notes: 'Some hesitation patterns noted',
          pronunciation_notes: 'Focus on vowel sounds and stress patterns',
          overall_assessment: 'Good progress, continue practicing regularly'
        },
        grammar_errors: [],
        vocabulary_analysis: []
      });
      setShowAnalysis(true);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Format time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Get score color
  const getScoreColor = (score: number, max: number) => {
    const percentage = (score / max) * 100;
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ maxWidth: 1200, margin: '0 auto', padding: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        <School sx={{ mr: 2, verticalAlign: 'middle' }} />
        Language Teacher - LLaMA Powered
      </Typography>

      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Main Recording Interface */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Conversation Practice
              </Typography>

              {!conversation && (
                <Button
                  variant="contained"
                  onClick={createConversation}
                  sx={{ mb: 2 }}
                >
                  Start New Conversation
                </Button>
              )}

              {conversation && (
                <>
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Topic: {conversation.topic} | Level: {conversation.difficulty_level}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {conversation.description}
                    </Typography>
                  </Box>

                  {/* Recording Controls */}
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <Typography variant="h4" sx={{ mb: 2 }}>
                      {formatTime(recordingTime)}
                    </Typography>

                    {!isRecording && !isAnalyzing && (
                      <Button
                        variant="contained"
                        size="large"
                        startIcon={<Mic />}
                        onClick={startRecording}
                        sx={{ mr: 2 }}
                      >
                        Start Recording
                      </Button>
                    )}

                    {isRecording && (
                      <Button
                        variant="contained"
                        color="error"
                        size="large"
                        startIcon={<Stop />}
                        onClick={stopRecording}
                      >
                        Stop Recording
                      </Button>
                    )}

                    {isAnalyzing && (
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <CircularProgress sx={{ mr: 2 }} />
                        <Typography>Processing...</Typography>
                      </Box>
                    )}
                  </Box>

                  {/* Transcript */}
                  {transcript && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        Transcript
                      </Typography>
                      <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                        <Typography variant="body1">
                          {transcript}
                        </Typography>
                      </Paper>
                      <Button
                        variant="contained"
                        onClick={analyzeConversation}
                        disabled={isAnalyzing}
                        sx={{ mt: 2 }}
                        startIcon={<Assessment />}
                      >
                        Analyze with LLaMA
                      </Button>
                    </Box>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Analysis Results */}
        <Grid item xs={12} md={4}>
          {analysisResult && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Analysis Results
                </Typography>

                {/* Overall Score */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h3" align="center" color="primary">
                    {analysisResult.overall_score.toFixed(1)}
                  </Typography>
                  <Typography variant="h6" align="center" gutterBottom>
                    {analysisResult.proficiency_level} Level
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={analysisResult.overall_score}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>

                {/* Detailed Scores */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Detailed Scores
                  </Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="body2">Grammar</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={(analysisResult.grammar_score / 25) * 100}
                        color={getScoreColor(analysisResult.grammar_score, 25)}
                        sx={{ height: 6 }}
                      />
                      <Typography variant="caption">
                        {analysisResult.grammar_score}/25
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">Vocabulary</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={(analysisResult.vocabulary_score / 20) * 100}
                        color={getScoreColor(analysisResult.vocabulary_score, 20)}
                        sx={{ height: 6 }}
                      />
                      <Typography variant="caption">
                        {analysisResult.vocabulary_score}/20
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">Fluency</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={(analysisResult.fluency_score / 20) * 100}
                        color={getScoreColor(analysisResult.fluency_score, 20)}
                        sx={{ height: 6 }}
                      />
                      <Typography variant="caption">
                        {analysisResult.fluency_score}/20
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">Pronunciation</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={(analysisResult.pronunciation_score / 15) * 100}
                        color={getScoreColor(analysisResult.pronunciation_score, 15)}
                        sx={{ height: 6 }}
                      />
                      <Typography variant="caption">
                        {analysisResult.pronunciation_score}/15
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>

                {/* Strengths */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Strengths
                  </Typography>
                  {analysisResult.strengths.map((strength, index) => (
                    <Chip
                      key={index}
                      label={strength}
                      color="success"
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>

                {/* Areas for Improvement */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Areas for Improvement
                  </Typography>
                  {analysisResult.areas_for_improvement.map((area, index) => (
                    <Chip
                      key={index}
                      label={area}
                      color="warning"
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* Detailed Analysis Dialog */}
      <Dialog
        open={showAnalysis}
        onClose={() => setShowAnalysis(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
          Detailed Analysis Report
        </DialogTitle>
        <DialogContent>
          {analysisResult && (
            <>
              <Typography variant="h6" gutterBottom>
                Recommendations
              </Typography>
              <List>
                {analysisResult.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={`${index + 1}. ${rec}`} />
                  </ListItem>
                ))}
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>
                Detailed Feedback
              </Typography>
              {Object.entries(analysisResult.detailed_feedback).map(([key, value]) => (
                <Box key={key} sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    {key.replace('_', ' ').toUpperCase()}
                  </Typography>
                  <Typography variant="body2" sx={{ pl: 2 }}>
                    {value as string}
                  </Typography>
                </Box>
              ))}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAnalysis(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ConversationInterface;
